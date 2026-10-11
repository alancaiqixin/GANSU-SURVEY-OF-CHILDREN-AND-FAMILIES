"""03_figures.py: publication figures (SVG, PDF, PNG at 600 dpi, width >= 3000 px). Arial where available (Liberation Sans fallback)."""
import pickle
import numpy as np, pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
from lib import *

plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'Liberation Sans', 'DejaVu Sans'],
                     'font.size': 9, 'axes.labelsize': 9, 'axes.titlesize': 10, 'xtick.labelsize': 8.5, 'ytick.labelsize': 8.5,
                     'legend.fontsize': 8.5, 'axes.linewidth': 0.8, 'xtick.major.width': 0.8, 'ytick.major.width': 0.8,
                     'axes.spines.top': False, 'axes.spines.right': False, 'figure.facecolor': 'white', 'axes.facecolor': 'white',
                     'svg.fonttype': 'none', 'pdf.fonttype': 42, 'savefig.facecolor': 'white'})
BLUE, VERM, GREEN, ORANGE, SKY, GREY = '#0072B2', '#D55E00', '#009E73', '#E69F00', '#56B4E9', '#6b6b6b'
R = pickle.load(open(f'{P1}/output/results.pkl', 'rb')); d = load()

def save(fig, name):
    for ext in ('svg', 'pdf'):
        fig.savefig(f'{FIG}/{name}.{ext}', bbox_inches='tight')
    fig.savefig(f'{FIG}/{name}.png', dpi=600, bbox_inches='tight')
    plt.close(fig)

def panel_label(ax, s): ax.text(-0.02, 1.06, s, transform=ax.transAxes, fontsize=11, fontweight='bold', va='bottom', ha='right')

# ---------------- Figure 1: birth weight distribution and county variation ----------------
fig, ax = plt.subplots(1, 2, figsize=(7.0, 3.1), gridspec_kw={'width_ratios': [1.05, 1]})
bw = d.bw_kg.dropna()
bins = np.arange(0.75, 5.25, 0.25)
ax[0].hist(bw, bins=bins, color=SKY, edgecolor='white', linewidth=0.6)
ax[0].axvline(2.5, color=VERM, lw=1.2, ls='--'); ax[0].text(2.45, ax[0].get_ylim()[1] * 0.93, '2.5 kg', color=VERM, ha='right', fontsize=8.5)
ax[0].set_xlabel('Maternal estimate of birth weight (kg)'); ax[0].set_ylabel('Number of children'); panel_label(ax[0], 'A')
g = d.dropna(subset=['lbw_est']).groupby('county').lbw_est.agg(['mean', 'count', 'sum'])
z = 1.96; p = g['mean']; n = g['count']
lo = (p + z**2 / (2 * n) - z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))) / (1 + z**2 / n)
hi = (p + z**2 / (2 * n) + z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))) / (1 + z**2 / n)
o = np.argsort(p.values); yy = np.arange(len(g))
ax[1].hlines(yy, lo.values[o] * 100, hi.values[o] * 100, color=GREY, lw=1)
ax[1].plot(p.values[o] * 100, yy, 'o', color=BLUE, ms=4)
ax[1].axvline(d.lbw_est.mean() * 100, color=VERM, lw=1, ls='--')
ax[1].set_yticks(yy); ax[1].set_yticklabels([f'County {int(c)}' for c in g.index[o]], fontsize=7)
ax[1].set_xlabel('Estimated birth weight below 2.5 kg (%)'); panel_label(ax[1], 'B')
fig.tight_layout(); save(fig, 'Figure1_birth_weight_distribution')

# ---------------- Figure 2: forest plot of main estimates ----------------
M = R['T2']
fig, axs = plt.subplots(1, 2, figsize=(7.0, 3.6), sharey=True)
labels = [l for _, l in OUTCOMES]
for ax_, (x, title, col) in zip(axs, [('bw_c', 'Birth weight, per 1 kg', BLUE), ('lbw_est', 'Estimated birth weight below 2.5 kg', VERM)]):
    s = M[M.exposure == x].set_index('outcome').loc[[o for o, _ in OUTCOMES]]
    yy = np.arange(len(s))[::-1]
    ax_.axvline(0, color='black', lw=0.8)
    ax_.hlines(yy, s.lo, s.hi, color=col, lw=1.6)
    ax_.plot(s.b, yy, 'o', color=col, ms=5, mfc='white' if False else col)
    for yi, (b, q) in zip(yy, zip(s.b, s.q)):
        pass
    ax_.set_title(title, fontsize=9.5); ax_.set_xlabel('Difference in standardized outcome (SD)')
    ax_.set_yticks(yy); ax_.set_yticklabels(labels)
panel_label(axs[0], 'A'); panel_label(axs[1], 'B')
axs[0].set_xlim(-0.2, 0.3); axs[1].set_xlim(-0.55, 0.3)
fig.tight_layout(); save(fig, 'Figure2_main_estimates')

# ---------------- Figure 3: binned partial-residual plots ----------------
def resid_bins(y, x='bw_c', nb=12):
    dd = d.dropna(subset=[y, x] + NEEDED).copy()
    rhs = ' + '.join(CTRL + (['math_form'] if y == 'z_ach00' else []))
    ry = smf.ols(f'{y} ~ {rhs}', dd).fit().resid; rx = smf.ols(f'{x} ~ {rhs}', dd).fit().resid
    dd['ry'], dd['rx'] = ry, rx
    dd['bin'] = pd.qcut(dd.rx, nb, duplicates='drop')
    b = dd.groupby('bin').agg(rx=('rx', 'mean'), ry=('ry', 'mean'), n=('ry', 'size'), se=('ry', lambda s: s.std() / np.sqrt(len(s))))
    return dd, b
fig, axs = plt.subplots(1, 2, figsize=(7.0, 3.2))
for ax_, (y, ttl, col) in zip(axs, [('z_cogacad', 'Cognitive and academic composite (SD)', BLUE), ('z_height04', 'Height in 2004 (SD)', VERM)]):
    dd, b = resid_bins(y)
    m = smf.ols('ry ~ rx', dd).fit(cov_type='cluster', cov_kwds={'groups': dd.vid})
    xs = np.linspace(dd.rx.quantile(0.01), dd.rx.quantile(0.99), 50)
    pr = m.get_prediction(pd.DataFrame({'rx': xs})).summary_frame()
    ax_.fill_between(xs, pr['mean_ci_lower'], pr['mean_ci_upper'], color=col, alpha=0.15, lw=0)
    ax_.plot(xs, pr['mean'], color=col, lw=1.6)
    ax_.errorbar(b.rx, b.ry, yerr=1.96 * b.se, fmt='o', color='black', ms=3.5, lw=0.8, capsize=0)
    ax_.axhline(0, color=GREY, lw=0.6); ax_.set_xlabel('Birth weight, residual (kg)'); ax_.set_ylabel('Residual ' + ttl)
    ax_.text(0.04, 0.93, f'Slope = {m.params["rx"]:.3f} (SE {m.bse["rx"]:.3f})', transform=ax_.transAxes, fontsize=8.5, va='top')
panel_label(axs[0], 'A'); panel_label(axs[1], 'B')
fig.tight_layout(); save(fig, 'Figure3_binned_residual_plots')

# ---------------- Figure 4: parental investment responses ----------------
T3 = R['T3']
mech_labels = {'invest': 'Parental investment index', 'books_z': 'Books owned (log)', 'edu_aspire': 'Educational aspiration', 'asp_college': 'Aspires to college',
               'exp_college': 'Expects college', 'mother_rated_perf': 'Mother-rated school performance'}
fig, axs = plt.subplots(1, 3, figsize=(7.2, 3.4), sharey=True)
for ax_, (x, title, col) in zip(axs, [('bw_c', 'Birth weight, per 1 kg', BLUE), ('lbw_est', 'Birth weight below 2.5 kg', VERM), ('preterm', 'Preterm birth', GREEN)]):
    s = T3[T3.exposure == x].set_index('outcome').loc[list(mech_labels)]
    yy = np.arange(len(s))[::-1]
    ax_.axvline(0, color='black', lw=0.8); ax_.hlines(yy, s.lo, s.hi, color=col, lw=1.6); ax_.plot(s.b, yy, 'o', color=col, ms=5)
    ax_.set_title(title, fontsize=9); ax_.set_xlabel('Difference (SD or scale units)')
    ax_.set_yticks(yy); ax_.set_yticklabels(list(mech_labels.values()))
for a, l in zip(axs, 'ABC'): panel_label(a, l)
fig.tight_layout(); save(fig, 'Figure4_parental_investment')

# ---------------- Figure 5: heterogeneity by old-age support expectations and other moderators ----------------
T4 = R['T4']
mod_order = ['oldage_high', 'rely_sons_agree', 'ses_low', 'female', 'vill_env_good', 'unsafe_water_hi', 'any_brother']
mod_lab = {'oldage_high': 'Expects a lot of old-age\nfinancial help', 'rely_sons_agree': 'Agrees parents should\nrely on sons', 'ses_low': 'Below-median\nhousehold resources',
           'female': 'Female', 'vill_env_good': 'Village environment\nrated good', 'unsafe_water_hi': 'High unsafe-water\nshare (village)', 'any_brother': 'Has a brother'}
fig, axs = plt.subplots(1, 3, figsize=(7.4, 4.0), sharey=True)
for ax_, (y, title) in zip(axs, [('z_cogacad', 'Cognitive and academic composite'), ('z_height04', 'Height (z), 2004'), ('invest', 'Parental investment index')]):
    s = T4[T4.outcome == y].set_index('moderator').loc[mod_order]
    yy = np.arange(len(s))[::-1] * 1.0
    ax_.axvline(0, color='black', lw=0.8)
    ax_.hlines(yy + 0.14, s.b0 - 1.96 * s.se0, s.b0 + 1.96 * s.se0, color=GREY, lw=1.4)
    ax_.plot(s.b0, yy + 0.14, 'o', color=GREY, ms=4.5, label='Moderator = 0')
    ax_.hlines(yy - 0.14, s.b1 - 1.96 * s.se1, s.b1 + 1.96 * s.se1, color=BLUE, lw=1.4)
    ax_.plot(s.b1, yy - 0.14, 's', color=BLUE, ms=4.5, label='Moderator = 1')
    ax_.set_title(title, fontsize=9); ax_.set_xlabel('Birth-weight slope (SD per kg)')
    ax_.set_yticks(yy); ax_.set_yticklabels([mod_lab[m] for m in s.index], fontsize=8)
h, l = axs[0].get_legend_handles_labels()
fig.legend(h, l, frameon=False, loc='lower center', ncol=2, fontsize=8.5, bbox_to_anchor=(0.5, -0.02))
for a, l in zip(axs, 'ABC'): panel_label(a, l)
fig.tight_layout(rect=(0, 0.04, 1, 1)); save(fig, 'Figure5_heterogeneity')

# ---------------- Figure 6: robustness of the birth-weight coefficient ----------------
Rb = R['T5']
fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.9), sharey=True)
specs = list(dict.fromkeys(Rb.spec))
for ax_, (y, title, col) in zip(axs, [('z_cogacad', 'Cognitive and academic composite', BLUE), ('z_height04', 'Height (z), 2004', VERM)]):
    s = Rb[Rb.outcome == y].set_index('spec').loc[specs]
    yy = np.arange(len(s))[::-1]
    ax_.axvline(0, color='black', lw=0.8); ax_.axvline(s.loc['Baseline', 'b'], color=GREY, lw=0.8, ls=':')
    ax_.hlines(yy, s.lo, s.hi, color=col, lw=1.5); ax_.plot(s.b, yy, 'o', color=col, ms=4.5)
    ax_.set_title(title, fontsize=9); ax_.set_xlabel('Birth-weight coefficient (SD per kg)')
    ax_.set_yticks(yy); ax_.set_yticklabels(specs, fontsize=7.5)
for a, l in zip(axs, 'AB'): panel_label(a, l)
fig.tight_layout(); save(fig, 'Figure6_robustness')

# ---------------- Appendix figures ----------------
# A1: nonlinear birth-weight bins
B = R['A_bins']
fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.9), sharex=True)
order = ['<2.5', '3.0-3.5', '>3.5']
for ax_, (y, title, col) in zip(axs, [('z_cogacad', 'Cognitive and academic composite', BLUE), ('z_height04', 'Height (z), 2004', VERM), ('invest', 'Parental investment index', GREEN)]):
    s = B[B.outcome == y].set_index('bin').loc[order]; xs = np.arange(3)
    ax_.axhline(0, color='black', lw=0.8); ax_.vlines(xs, s.b - 1.96 * s.se, s.b + 1.96 * s.se, color=col, lw=1.5); ax_.plot(xs, s.b, 'o', color=col, ms=5)
    ax_.set_xticks(xs); ax_.set_xticklabels(['<2.5', '3.0 to 3.5', '>3.5']); ax_.set_title(title, fontsize=9)
    ax_.set_xlabel('Birth weight (kg), ref. 2.5 to 3.0 kg')
axs[0].set_ylabel('Difference (SD)')
fig.tight_layout(); save(fig, 'FigureA1_birth_weight_bins')
# A2: attrition by birth weight (observed share by birth weight bin)
d['bw_bin'] = pd.cut(d.bw_kg, [0, 2.5, 3.0, 3.5, 10], labels=['<2.5', '2.5 to 3.0', '3.0 to 3.5', '>3.5'], right=False)
fig, ax_ = plt.subplots(figsize=(5.2, 3.0))
w = 0.25
for i, (flag, lab, col) in enumerate([('obs04_test', 'Tests, 2004', BLUE), ('obs04_health', 'Height, 2004', VERM), ('obs09', 'Literacy, 2009', GREEN)]):
    sh = d.groupby('bw_bin')[flag].mean()
    ax_.bar(np.arange(4) + (i - 1) * w, sh.values * 100, width=w, color=col, label=lab)
ax_.set_xticks(np.arange(4)); ax_.set_xticklabels(['<2.5', '2.5 to 3.0', '3.0 to 3.5', '>3.5']); ax_.set_ylabel('Children with outcome observed (%)'); ax_.set_xlabel('Birth weight (kg)')
ax_.legend(frameon=False, ncol=3, loc='lower center', bbox_to_anchor=(0.5, 1.0)); fig.tight_layout(); save(fig, 'FigureA2_attrition')
# A3: Oster delta
O = R['T6_oster']; fig, ax_ = plt.subplots(figsize=(5.2, 3.0))
lab = {'z_cogacad': 'Cognitive and academic composite', 'z_cog00': 'Cognitive test, 2000', 'z_ach00': 'Achievement test, 2000', 'z_lit04': 'Literacy test, 2004', 'z_height04': 'Height (z), 2004', 'invest': 'Parental investment index'}
yy = np.arange(len(O))[::-1]
ax_.barh(yy, O.beta_star_delta1, color=[BLUE if v > 0.1 else SKY for v in O.beta_star_delta1], height=0.55)
ax_.plot(O.b_full, yy, 'k|', ms=12, label='Estimate with controls')
ax_.set_yticks(yy); ax_.set_yticklabels([lab[o] for o in O.outcome]); ax_.axvline(0, color='black', lw=0.8)
ax_.set_xlabel('Bias-adjusted coefficient at delta = 1 (bars); controlled estimate (ticks)'); ax_.legend(frameon=False, loc='lower right')
fig.tight_layout(); save(fig, 'FigureA3_oster_bounds')
print('figures done')
