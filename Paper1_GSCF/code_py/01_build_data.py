"""
01_build_data.py
Build the analysis file for Paper 1 from the GSCF files in the repository root.
Unit: target child of the 2000 cohort (n = 2,000). Python mirror of dofiles/01_build_data.do.
Missing-value codes in GSCF (-1, -2, -3, -6) are set to missing.
"""
import os, sys
import numpy as np, pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'Paper1_GSCF', 'data_clean')
os.makedirs(OUT, exist_ok=True)
rd = lambda f: pd.read_stata(os.path.join(ROOT, f), convert_categoricals=False)

def clean(s):
    s = pd.to_numeric(s, errors='coerce')
    return s.where(s >= 0)

def z(s, by=None):
    if by is None:
        return (s - s.mean()) / s.std()
    g = s.groupby(by)
    return (s - g.transform('mean')) / g.transform('std')

# ---------- wave 2000 mother (birth items, attitudes, household resources) ----------
m = rd('moth2000ts.dta')
d = pd.DataFrame({'hhid': m.hhid, 'county': m.a1, 'township': m.a2, 'village': m.a3})
d['vid'] = (d.hhid // 100).astype(int)          # village identifier (county, township, village)
# birth endowment (maternal report in 2000)
mh2, mh3, mh4 = clean(m.mh2), clean(m.mh3), clean(m.mh4)
d['lbw'] = np.where(mh3.isna(), np.nan, (mh3 == 3).astype(float))       # "light" relative to other children
d['heavy_bw'] = np.where(mh3.isna(), np.nan, (mh3 == 1).astype(float))
d['bw_jin'] = mh4.where((mh4 >= 2) & (mh4 <= 12))                       # estimated birth weight, jin (0.5 kg)
d['bw_kg'] = d.bw_jin * 0.5
d['lbw_est'] = np.where(d.bw_kg.isna(), np.nan, (d.bw_kg < 2.5).astype(float))
d['preterm'] = np.where(mh2.isna(), np.nan, (mh2 == 2).astype(float))
d['postterm'] = np.where(mh2.isna(), np.nan, (mh2 == 3).astype(float))
d['gest_unknown'] = np.where(mh2.isna(), np.nan, (mh2 == 4).astype(float))
d['adverse_birth'] = np.where(d.lbw.isna() & d.preterm.isna(), np.nan,
                              ((d.lbw == 1) | (d.preterm == 1)).astype(float))
mh5 = clean(m.mh5)
d['home_birth'] = np.where(mh5.isna(), np.nan, (mh5 == 1).astype(float))
d['inst_birth'] = np.where(mh5.isna(), np.nan, mh5.isin([3, 4]).astype(float))
d['health_vs_peers'] = 6 - clean(m.mh6)         # 5 = much better than village peers
# old-age support expectations (aging link)
d['oldage_exp'] = 4 - clean(m.md2)              # 3 = expects a lot of financial help from children
d['oldage_high'] = np.where(d.oldage_exp.isna(), np.nan, (d.oldage_exp == 3).astype(float))
d['son_support'] = np.where(clean(m.md3).isna(), np.nan, (clean(m.md3) == 1).astype(float))
d['rely_sons'] = clean(m.md1h)                  # 3 = agrees parents should rely on sons in old age
d['rely_sons_agree'] = np.where(d.rely_sons.isna(), np.nan, (d.rely_sons == 3).astype(float))
# village environment as perceived by mother
d['vill_env'] = clean(m.mb1)                    # 1 bad, 2 average, 3 good for child growth
d['vill_env_good'] = np.where(d.vill_env.isna(), np.nan, (d.vill_env == 3).astype(float))
# household resources
me1, me2, me3 = clean(m.me1), clean(m.me2), clean(m.me3)
comp = pd.DataFrame({
    'sat_econ': 4 - me1, 'rel_econ': 5 - me2, 'income_enough': me3,
    'desk': (clean(m.me8a) == 1).astype(float).where(clean(m.me8a).notna()),
    'dict': (clean(m.me8b) == 1).astype(float).where(clean(m.me8b).notna()),
    'readmat': (clean(m.me8c) == 1).astype(float).where(clean(m.me8c).notna()),
    'food_enough': 4 - clean(m.mf1)})
zc = (comp - comp.mean()) / comp.std()
d['ses'] = zc.mean(axis=1, skipna=True).where(zc.notna().sum(axis=1) >= 5)
d['ses'] = z(d.ses)
# parental investment (mechanisms)
inv = pd.DataFrame({k: clean(m[k]) for k in ['mk1a', 'mk1b', 'mk1d', 'mk1e']})
d['invest'] = z(((inv - inv.mean()) / inv.std()).mean(axis=1, skipna=True).where(inv.notna().sum(axis=1) >= 3))
d['books'] = clean(m.mk14).where(clean(m.mk14) <= 90)
d['books_z'] = z(np.log1p(d.books))
d['edu_expect'] = clean(m.mj11).where(clean(m.mj11) <= 4)
d['edu_aspire'] = clean(m.mj12).where(clean(m.mj12) <= 4)
d['asp_college'] = np.where(d.edu_aspire.isna(), np.nan, (d.edu_aspire == 4).astype(float))
d['exp_college'] = np.where(d.edu_expect.isna(), np.nan, (d.edu_expect == 4).astype(float))
d['mother_rated_perf'] = 4 - clean(m.mi3)       # 3 = above average
d['father_home'] = np.where(clean(m.mc6).isna(), np.nan, (clean(m.mc6) == 1).astype(float))

# ---------- demography from linking file: ages, sibship ----------
g = rd('GSCF_merge_pid.dta')
tgt = g[g.pid00 == 1].drop_duplicates('hhid').set_index('hhid')
d = d.merge(tgt[['byear00', 'fbyear00', 'mbyear00', 'samekid0004', 'samekid0009', 'samekid0015',
                 'from04', 'from09', 'from15', 'hhfrom04', 'hhfrom09', 'hhfrom15']], left_on='hhid', right_index=True, how='left')
d['age00'] = 2000 - d.byear00
d['father_age'] = 2000 - d.fbyear00
d['mother_age'] = 2000 - d.mbyear00
sib = g[g.relat00.notna() & (g.relat00 != 1) & (g.from00 == 1)].copy()
# relation codes (inferred from birth-year pattern): 2x older brother, 3x younger brother,
# 4x older sister, 5x younger sister
first = (sib.relat00 // 10).astype(int)
for code, name in [(2, 'older_bro'), (3, 'young_bro'), (4, 'older_sis'), (5, 'young_sis')]:
    s = sib[first == code].groupby('hhid').size().rename(name)
    d = d.merge(s, left_on='hhid', right_index=True, how='left')
    d[name] = d[name].fillna(0)
d['n_sibs'] = d[['older_bro', 'young_bro', 'older_sis', 'young_sis']].sum(axis=1)
d['any_brother'] = ((d.older_bro + d.young_bro) > 0).astype(float)
d['firstborn'] = ((d.older_bro + d.older_sis) == 0).astype(float)
d['sibs_cat'] = d.n_sibs.clip(upper=3)

# ---------- sex (2004 files; not collected in the 2000 files available here) ----------
h4 = rd('health2004t.dta'); l4 = rd('literacy2004t.dta')
# literacy2004t repeats 9 household ids (target and sibling rows cannot be told apart): drop all repeated ids
l4 = l4[~l4.hhid.duplicated(keep=False)].copy()
sx = pd.concat([h4[['hhid', 'sex']], l4[['hhid', 'sex']]]).dropna().drop_duplicates('hhid')
d = d.merge(sx.rename(columns={'sex': 'sex04'}), on='hhid', how='left')
d['female'] = np.where(d.sex04.isna(), np.nan, (d.sex04 == 2).astype(float))
d['sex_missing'] = d.female.isna().astype(int)

# ---------- outcomes ----------
a0 = rd('achieve2000t.dta')[['hhid', 'ceyan', 'yuwen', 'shuxue']]
a0['math_form'] = a0.shuxue.notna().astype(int)
a0['ach00'] = a0.ceyan
a0['z_ach00'] = z(a0.ach00, a0.math_form)
c0 = rd('litracy2000t.dta')[['hhid', 'renzhi']]
c0['z_cog00'] = z(c0.renzhi)
d = d.merge(a0[['hhid', 'math_form', 'z_ach00']], on='hhid', how='left').merge(c0[['hhid', 'z_cog00']], on='hhid', how='left')

a4 = rd('achieve2004t.dta')[['hhid', 'schlevel', 'yuwen', 'shuxue']]
a4['lev'] = a4.schlevel.fillna(-1)
a4['z_chi04'] = z(a4.yuwen, a4.lev).where(a4.schlevel.notna())
a4['z_mat04'] = z(a4.shuxue, a4.lev).where(a4.schlevel.notna())
l4s = l4[['hhid', 'total']].copy(); l4s['z_lit04'] = z(l4s.total)
h4s = h4[['hhid', 'byear', 'sex', 'height', 'weight', 'hb', 'bmiweightheight2']].copy()
h4s['cell'] = h4s.sex.astype(str) + '_' + h4s.byear.astype(str)
ok = h4s.height.between(120, 200)
h4s['z_height04'] = z(h4s.height.where(ok), h4s.cell)
h4s['z_bmi04'] = z(h4s.bmiweightheight2.where(h4s.bmiweightheight2.between(10, 40)), h4s.cell)
h4s['hb04'] = h4s.hb.where(h4s.hb.between(70, 200))
h4s['z_hb04'] = z(h4s.hb04, h4s.cell)
for df, cols in [(a4, ['z_chi04', 'z_mat04']), (l4s, ['z_lit04']), (h4s, ['z_height04', 'z_bmi04', 'hb04', 'z_hb04'])]:
    d = d.merge(df[['hhid'] + cols], on='hhid', how='left')
l9 = rd('literacy2009t.dta')
l9 = l9[~l9.hhid.duplicated(keep=False)].copy()
items = [c for c in l9.columns if c.startswith(('one', 'two', 'three', 'five'))] + ['four']
l9['lit09_raw'] = l9[items].clip(lower=0).sum(axis=1, min_count=len(items))
l9['z_lit09'] = z(l9.lit09_raw)
d = d.merge(l9[['hhid', 'z_lit09']], on='hhid', how='left')

# composite of cognitive and academic scores across waves (at least 4 of 6 components)
comp_cols = ['z_cog00', 'z_ach00', 'z_chi04', 'z_mat04', 'z_lit04', 'z_lit09']
d['n_cogacad'] = d[comp_cols].notna().sum(axis=1)
d['z_cogacad'] = z(d[comp_cols].mean(axis=1).where(d.n_cogacad >= 4))
d['bw_c'] = d.bw_kg - 3                          # centred at the sample median (3.0 kg)
d['age00_c'] = d.age00.clip(9, 13)
d['ses_low'] = np.where(d.ses.isna(), np.nan, (d.ses < d.ses.median()).astype(float))

# in-sample flags (outcome observed) for attrition analysis
d['obs04_test'] = d[['z_chi04', 'z_mat04', 'z_lit04']].notna().any(axis=1).astype(int)
d['obs04_health'] = d[['z_height04']].notna().any(axis=1).astype(int)
d['obs09'] = d.z_lit09.notna().astype(int)
d['obs00'] = d[['z_cog00', 'z_ach00']].notna().any(axis=1).astype(int)

# ---------- village context ----------
v = rd('vill2000.dta')
v['vid'] = (v.a1.astype('int64') * 10000 + v.a2.astype('int64') * 100 + v.a3.astype('int64'))
# hhid = a1*1e6 + a2*1e4 + a3*1e2 + a4 -> vid = hhid//100 = a1*1e4 + a2*1e2 + a3
src = v[['vd1a', 'vd1b', 'vd1c', 'vd1d', 'vd1e']].clip(lower=0)
tot = src.sum(axis=1).replace(0, np.nan)
v['tap_share'] = (src.vd1c + src.vd1d) / tot
v['unsafe_water_share'] = (src.vd1b + src.vd1e) / tot       # unpumped well, river, lake or pond
v['dist_county_km'] = clean(v.vb7)
d = d.merge(v[['vid', 'tap_share', 'unsafe_water_share', 'dist_county_km']], on='vid', how='left')
d['unsafe_water_hi'] = np.where(d.unsafe_water_share.isna(), np.nan, (d.unsafe_water_share >= d.unsafe_water_share.median()).astype(float))

# ---------- optional external environmental exposure (county-year PM2.5 etc.) ----------
ext = os.path.join(ROOT, 'Paper1_GSCF', 'data_external', 'county_exposure.csv')
if os.path.exists(ext):
    e = pd.read_csv(ext)
    d = d.merge(e, on='county', how='left')
    print('merged external exposure file', ext)
else:
    print('no external exposure file found; skipping')

d.to_csv(os.path.join(OUT, 'analysis_child_2000cohort.csv'), index=False)
d.to_stata(os.path.join(OUT, 'analysis_child_2000cohort.dta'), write_index=False, version=118)
print(d.shape)
print(d[['lbw', 'preterm', 'adverse_birth', 'female', 'ses', 'z_cog00', 'z_ach00', 'z_chi04', 'z_mat04', 'z_lit04', 'z_height04', 'z_lit09',
         'oldage_high', 'vill_env_good', 'invest', 'unsafe_water_share']].describe().round(2).T.to_string())
