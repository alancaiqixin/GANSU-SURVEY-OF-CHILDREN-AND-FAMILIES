"""02_models.py: descriptive, main, mechanism, heterogeneity, robustness, endogeneity estimates.
Writes CSV tables to output/tables and a pickle of all results for figures and Word tables."""
import pickle, itertools
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from lib import *

d = load()
R = {}

# ---------------- Table 1: descriptive statistics ----------------
desc_vars = [('bw_kg', 'Estimated birth weight (kg)'), ('lbw', 'Low birth weight, maternal category "light"'),
             ('lbw_est', 'Estimated birth weight below 2.5 kg'), ('preterm', 'Preterm birth'),
             ('postterm', 'Post-term birth'), ('gest_unknown', 'Gestational age unknown'), ('inst_birth', 'Born in a clinic or hospital'),
             ('female', 'Female'), ('age00', 'Age in 2000 (years)'), ('father_age', "Father's age in 2000"), ('mother_age', "Mother's age in 2000"),
             ('n_sibs', 'Number of siblings'), ('firstborn', 'First-born'), ('any_brother', 'Has at least one brother'), ('ses', 'Household resource index (z)'),
             ('oldage_high', 'Mother expects a lot of financial help in old age'), ('rely_sons_agree', 'Agrees parents should rely on sons in old age'),
             ('vill_env_good', 'Mother rates village environment as good for children'), ('unsafe_water_share', 'Village share of households using unsafe water'),
             ('invest', 'Parental investment index (z)'), ('edu_aspire', 'Educational aspiration (1 to 4)'), ('asp_college', 'Aspires to college'),
             ('z_cogacad', 'Cognitive and academic composite (z)'), ('z_height04', 'Height in 2004 (z)')]
rows = []
for v, lab in desc_vars:
    s = d[v]; rows.append(dict(Variable=lab, N=int(s.notna().sum()), Mean=s.mean(), SD=s.std(),
                               Mean_normal=d.loc[d.adverse_birth == 0, v].mean(), Mean_adverse=d.loc[d.adverse_birth == 1, v].mean()))
T1 = pd.DataFrame(rows)
R['T1'] = T1; T1.to_csv(f'{TAB}/T1_descriptives.csv', index=False)

# ---------------- Table 2: birth endowments and child development ----------------
exposures = [('bw_c', 'Birth weight (per 1 kg)'), ('lbw_est', 'Estimated birth weight below 2.5 kg'),
             ('lbw', 'Low birth weight, maternal category'), ('preterm', 'Preterm birth')]
main = []
for x, xl in exposures:
    for y, yl in OUTCOMES:
        m, dd = fit(d, y, x); c = coef(m, x); c.update(exposure=x, exposure_label=xl, outcome=y, outcome_label=yl); main.append(c)
M = pd.DataFrame(main)
M['q'] = np.nan
for x in M.exposure.unique():
    idx = M.exposure == x; M.loc[idx, 'q'] = bh(M.loc[idx, 'p'].values)
R['T2'] = M; M.to_csv(f'{TAB}/T2_main_estimates.csv', index=False)
print(M[M.exposure == 'bw_c'][['outcome', 'b', 'se', 'p', 'q', 'n']].round(3).to_string())
print(M[M.exposure == 'lbw_est'][['outcome', 'b', 'se', 'p', 'q', 'n']].round(3).to_string())
print(M[M.exposure == 'preterm'][['outcome', 'b', 'se', 'p', 'q', 'n']].round(3).to_string())

# ---------------- Table 3: parental investment (reinforcement vs compensation) ----------------
mech_out = [('invest', 'Parental investment index'), ('books_z', 'Books owned (log, z)'), ('edu_aspire', 'Educational aspiration (1 to 4)'),
            ('asp_college', 'Aspires to college'), ('exp_college', 'Expects college'), ('mother_rated_perf', 'Mother-rated school performance')]
mech = []
for x, xl in exposures + [('health_vs_peers', 'Mother-rated health vs village peers (1 to 5)')]:
    for y, yl in mech_out:
        m, dd = fit(d, y, x); c = coef(m, x); c.update(exposure=x, exposure_label=xl, outcome=y, outcome_label=yl); mech.append(c)
T3 = pd.DataFrame(mech); T3['q'] = np.nan
for x in T3.exposure.unique():
    idx = T3.exposure == x; T3.loc[idx, 'q'] = bh(T3.loc[idx, 'p'].values)
R['T3'] = T3; T3.to_csv(f'{TAB}/T3_mechanisms.csv', index=False)
print(T3[['exposure', 'outcome', 'b', 'se', 'p', 'n']].round(3).to_string())

# ---------------- Table 4: heterogeneity (interactions with birth weight) ----------------
mods = [('oldage_high', 'Expects a lot of old-age financial help'), ('rely_sons_agree', 'Agrees parents should rely on sons'),
        ('ses_low', 'Below-median household resources'), ('female', 'Female'), ('vill_env_good', 'Village environment rated good'),
        ('unsafe_water_hi', 'Village unsafe-water share above median'), ('any_brother', 'Has a brother')]
het_out = [('z_cogacad', 'Cognitive and academic composite'), ('z_height04', 'Height (z), 2004'), ('invest', 'Parental investment index'), ('edu_aspire', 'Educational aspiration')]
het = []
for mv, ml in mods:
    for y, yl in het_out:
        extra = [mv, f'bw_c:{mv}']
        drop = ['female0', 'sex_missing'] if mv == 'female' else []
        m, dd = fit(d, y, 'bw_c', extra=extra, drop_ctrl=drop)
        ci = coef(m, f'bw_c:{mv}'); cm = coef(m, 'bw_c')
        # subgroup slopes
        d0 = dd[dd[mv] == 0]; d1 = dd[dd[mv] == 1]
        m0, _ = fit(d0, y, 'bw_c', drop_ctrl=drop); m1, _ = fit(d1, y, 'bw_c', drop_ctrl=drop)
        c0 = coef(m0, 'bw_c'); c1 = coef(m1, 'bw_c')
        het.append(dict(moderator=mv, moderator_label=ml, outcome=y, outcome_label=yl, b_main=cm['b'], b_int=ci['b'], se_int=ci['se'], p_int=ci['p'],
                        b0=c0['b'], se0=c0['se'], n0=c0['n'], b1=c1['b'], se1=c1['se'], n1=c1['n'], n=ci['n']))
T4 = pd.DataFrame(het)
T4['q_all'] = bh(T4.p_int.values)
R['T4'] = T4; T4.to_csv(f'{TAB}/T4_heterogeneity.csv', index=False)
print(T4[['moderator', 'outcome', 'b_int', 'se_int', 'p_int', 'b0', 'b1', 'n']].round(3).to_string())

# ---------------- Table 5: robustness ----------------
def spec(label, y, x='bw_c', **kw):
    dsub = kw.pop('data', d)
    m, dd = fit(dsub, y, x, **kw); c = coef(m, x); c.update(spec=label, outcome=y); return c
rob = []
for y in ['z_cogacad', 'z_height04']:
    rob.append(spec('Baseline', y))
    rob.append(spec('No household resource control', y, drop_ctrl=['ses']))
    rob.append(spec('No demographic controls', y, ctrl=['C(county)']))
    rob.append(spec('Village fixed effects', y, ctrl=[c for c in CTRL if c != 'C(county)'] + ['C(vid)']))
    rob.append(spec('Cluster at county (G = 20)', y, cluster='county'))
    rob.append(spec('Exclude gestation unknown', y, data=d[d.gest_unknown == 0]))
    rob.append(spec('Exclude preterm births', y, data=d[d.preterm == 0]))
    rob.append(spec('Birth weight 2.0 to 4.5 kg only', y, data=d[d.bw_kg.between(2.0, 4.5)]))
    rob.append(spec('Girls only', y, data=d[d.female == 1], drop_ctrl=['female0', 'sex_missing']))
    rob.append(spec('Boys only', y, data=d[d.female == 0], drop_ctrl=['female0', 'sex_missing']))
    rob.append(spec('Add delivery in clinic or hospital', y, extra=['inst_birth']))
    rob.append(spec('Add mother-rated health vs peers (potential mediator)', y, extra=['health_vs_peers']))
Rb = pd.DataFrame(rob)
# wild cluster bootstrap p-values (village; county)
for y in ['z_cogacad', 'z_height04']:
    pv, t0 = wild_cluster_p(d, y, 'bw_c', cluster='vid', B=1999)
    Rb.loc[(Rb.spec == 'Baseline') & (Rb.outcome == y), 'p_wild_village'] = pv
    pv2, t2 = wild_cluster_p(d, y, 'bw_c', cluster='county', B=1999)
    Rb.loc[(Rb.spec == 'Cluster at county (G = 20)') & (Rb.outcome == y), 'p_wild_county'] = pv2
R['T5'] = Rb; Rb.to_csv(f'{TAB}/T5_robustness.csv', index=False)
print(Rb.round(3).to_string())

# ---------------- attrition and inverse-probability weights ----------------
att = []
for lab, flag in [('Tests observed in 2004', 'obs04_test'), ('Height measured in 2004', 'obs04_health'), ('Literacy test observed in 2009', 'obs09')]:
    dd = d.dropna(subset=['bw_c', 'father_age', 'mother_age', 'ses', 'age00_c']).copy()
    ms = smf.logit(f'{flag} ~ bw_c + lbw_est + preterm + C(age00_c) + female0 + sex_missing + father_age + mother_age + C(sibs_cat) + firstborn + any_brother + ses + C(county)',
                   dd.dropna(subset=['lbw_est', 'preterm'])).fit(disp=0, cov_type='cluster', cov_kwds={'groups': dd.dropna(subset=['lbw_est', 'preterm']).vid})
    att.append(dict(sample=lab, rate=d[flag].mean(), b_bw=ms.params['bw_c'], p_bw=ms.pvalues['bw_c'], b_ses=ms.params['ses'], p_ses=ms.pvalues['ses'],
                    b_pre=ms.params['preterm'], p_pre=ms.pvalues['preterm']))
R['A_attrition'] = pd.DataFrame(att); print(R['A_attrition'].round(3))
# IPW (stabilised) from a model of observing the outcome at 2004/2009
def ipw(flag):
    dd = d.dropna(subset=['bw_c', 'father_age', 'mother_age', 'ses', 'age00_c', 'lbw_est', 'preterm']).copy()
    f = f'{flag} ~ bw_c + preterm + C(age00_c) + female0 + sex_missing + father_age + mother_age + C(sibs_cat) + firstborn + any_brother + ses + vill_env_good + oldage_high + invest + C(county)'
    ms = smf.logit(f, dd.dropna(subset=['vill_env_good', 'oldage_high', 'invest'])).fit(disp=0)
    dd = dd.dropna(subset=['vill_env_good', 'oldage_high', 'invest']).copy()
    dd['phat'] = ms.predict(dd); dd['w'] = dd[flag].mean() / dd.phat
    return dd[['hhid', 'w']]
ipw_rows = []
for y, flag in [('z_chi04', 'obs04_test'), ('z_mat04', 'obs04_test'), ('z_lit04', 'obs04_test'), ('z_height04', 'obs04_health'), ('z_lit09', 'obs09')]:
    w = ipw(flag); dm = d.merge(w, on='hhid', how='inner')
    mu, _ = fit(d, y, 'bw_c'); mw, _ = fit(dm, y, 'bw_c', weights='w')
    cu, cw = coef(mu, 'bw_c'), coef(mw, 'bw_c')
    ipw_rows.append(dict(outcome=y, b_unw=cu['b'], se_unw=cu['se'], b_ipw=cw['b'], se_ipw=cw['se'], p_ipw=cw['p'], n_ipw=cw['n']))
R['T5_ipw'] = pd.DataFrame(ipw_rows); print(R['T5_ipw'].round(3))

# ---------------- Endogeneity: Oster bounds, E-values, negative controls, recall checks ----------------
def oster(y, x='bw_c', rmax_mult=1.3):
    m0, dd = fit(d, y, x, ctrl=['C(county)'])     # restricted: county fixed effects only
    mc, _ = fit(d, y, x)                          # full controls (same sample by construction of NEEDED)
    # force same sample
    dd2 = d.dropna(subset=[y, x] + NEEDED + ['vid']).copy()
    m0 = smf.ols(f"{y} ~ {x} + C(county)" + (' + math_form' if y == 'z_ach00' else ''), dd2).fit()
    mc = smf.ols(f"{y} ~ {x} + " + ' + '.join(CTRL) + (' + math_form' if y == 'z_ach00' else ''), dd2).fit()
    b0, r0, bt, rt = m0.params[x], m0.rsquared, mc.params[x], mc.rsquared
    rmax = min(1.0, rmax_mult * rt)
    delta = bt * (rt - r0) / ((b0 - bt) * (rmax - rt)) if (b0 - bt) != 0 else np.inf
    beta_star = bt - 1.0 * (b0 - bt) * (rmax - rt) / (rt - r0)
    return dict(outcome=y, b_restricted=b0, r2_restricted=r0, b_full=bt, r2_full=rt, rmax=rmax, delta_for_zero=delta, beta_star_delta1=beta_star)
R['T6_oster'] = pd.DataFrame([oster(y) for y in ['z_cogacad', 'z_cog00', 'z_ach00', 'z_lit04', 'z_height04', 'invest']])
print(R['T6_oster'].round(3).to_string())

def evalue(rr): return rr + np.sqrt(rr * (rr - 1)) if rr >= 1 else evalue(1 / rr)
ev = []
for y in ['z_cogacad', 'z_height04']:
    m, dd = fit(d, y, 'lbw_est'); c = coef(m, 'lbw_est')
    dstd = abs(c['b']); rr = np.exp(0.91 * dstd); rr_lo = np.exp(0.91 * max(abs(c['b']) - 1.96 * c['se'], 0)) if c['b'] != 0 else 1
    ev.append(dict(outcome=y, b=c['b'], se=c['se'], rr_approx=rr, e_value_point=evalue(rr), e_value_ci=evalue(rr_lo) if (abs(c['b']) - 1.96 * c['se']) > 0 else 1.0))
R['T6_evalue'] = pd.DataFrame(ev); print(R['T6_evalue'].round(3))

# negative-control outcomes: variables that birth weight cannot plausibly cause
nco = []
for y, lab in [('father_age', "Father's age"), ('mother_age', "Mother's age"), ('vill_env', 'Village environment rating'), ('unsafe_water_share', 'Village unsafe-water share'),
               ('tap_share', 'Village tap-water share'), ('father_home', 'Father lives at home'), ('ses', 'Household resource index')]:
    ctrl = [c for c in CTRL if c not in ('father_age', 'mother_age', 'ses')] if y in ('father_age', 'mother_age', 'ses') else CTRL
    dd = d.dropna(subset=[y, 'bw_c', 'vid', 'father_age', 'mother_age', 'ses']).copy()
    cc = [c for c in ctrl if c != 'C(county)'] if y in ('unsafe_water_share', 'tap_share', 'vill_env') else ctrl
    cc = [c for c in cc if c != 'C(county)'] if y in ('unsafe_water_share', 'tap_share') else cc
    f = f'{y} ~ bw_c + ' + ' + '.join(cc if cc else ['1'])
    m = smf.ols(f, dd).fit(cov_type='cluster', cov_kwds={'groups': dd.vid})
    c = coef(m, 'bw_c'); c.update(outcome=lab); nco.append(c)
R['T6_nco'] = pd.DataFrame(nco); print(R['T6_nco'][['outcome', 'b', 'se', 'p', 'n']].round(3))

# recall check: does the birth-weight gradient differ by whether outcome post-dates the interview (no scope for recall contamination)?
rec = []
for y in ['z_cog00', 'z_ach00', 'z_chi04', 'z_mat04', 'z_lit04', 'z_lit09']:
    m, dd = fit(d, y, 'bw_c'); c = coef(m, 'bw_c'); c.update(outcome=y, wave='2000 (same wave as report)' if y.endswith('00') else ('2004' if y.endswith('04') else '2009')); rec.append(c)
R['T6_recall'] = pd.DataFrame(rec)
# validation against measured height and gender gap in agreement
mm, ddm = fit(d, 'z_height04', 'bw_c'); R['validation_height'] = coef(mm, 'bw_c')
# height gradient by sex (measured outcome): correlation of recall with biology
print(R['T6_recall'][['outcome', 'wave', 'b', 'se', 'p']].round(3))

# birth-weight reporting: heaping at 3.0 kg and robustness excluding heaped values
R['heaping'] = dict(share_3kg=float((d.bw_kg == 3.0).sum() / d.bw_kg.notna().sum()), n=int(d.bw_kg.notna().sum()))
m, dd = fit(d[d.bw_kg != 3.0], 'z_height04', 'bw_c'); R['heaping_excl_3kg_height'] = coef(m, 'bw_c')
m, dd = fit(d[d.bw_kg != 3.0], 'z_cogacad', 'bw_c'); R['heaping_excl_3kg_cogacad'] = coef(m, 'bw_c')
print(R['heaping'], R['heaping_excl_3kg_height']['b'], R['heaping_excl_3kg_cogacad']['b'])

# ---------------- Appendix: county variation, hemoglobin, BMI, nonlinear ----------------
app = []
for y, yl in [('z_hb04', 'Hemoglobin (z), 2004'), ('z_bmi04', 'BMI (z), 2004')]:
    for x, xl in exposures:
        m, dd = fit(d, y, x); c = coef(m, x); c.update(exposure=x, exposure_label=xl, outcome=y, outcome_label=yl); app.append(c)
R['A_extra_health'] = pd.DataFrame(app)
# nonlinearity: birth-weight bins
d['bw_bin'] = pd.cut(d.bw_kg, [0, 2.5, 3.0, 3.5, 10], labels=['<2.5', '2.5-3.0', '3.0-3.5', '>3.5'], right=False)
nl = []
for y in ['z_cogacad', 'z_height04', 'invest']:
    dd = d.dropna(subset=[y, 'bw_bin'] + NEEDED).copy()
    f = f"{y} ~ C(bw_bin, Treatment('2.5-3.0')) + " + ' + '.join(CTRL)
    m = smf.ols(f, dd).fit(cov_type='cluster', cov_kwds={'groups': dd.vid})
    for k in m.params.index:
        if 'bw_bin' in k:
            nl.append(dict(outcome=y, bin=k.split('[T.')[1].rstrip(']'), b=m.params[k], se=m.bse[k], p=m.pvalues[k], n=int(m.nobs)))
R['A_bins'] = pd.DataFrame(nl); print(R['A_bins'].round(3))

# who reports birth weight? item nonresponse
d['bw_missing'] = d.bw_kg.isna().astype(int)
dd = d.dropna(subset=['father_age', 'mother_age', 'ses']).copy()
mm = smf.logit('bw_missing ~ ses + father_age + mother_age + any_brother + firstborn + female0 + sex_missing + oldage_high + C(county)', dd.dropna(subset=['oldage_high'])).fit(disp=0, cov_type='cluster', cov_kwds={'groups': dd.dropna(subset=['oldage_high']).vid})
R['A_bwmissing'] = pd.DataFrame({'b': mm.params, 'se': mm.bse, 'p': mm.pvalues}).loc[['ses', 'father_age', 'mother_age', 'any_brother', 'firstborn', 'female0', 'oldage_high']]
R['bw_missing_rate'] = float(d.bw_missing.mean()); print(R['A_bwmissing'].round(3), R['bw_missing_rate'])
pickle.dump(R, open(f'{P1}/output/results.pkl', 'wb'))
print('saved')
