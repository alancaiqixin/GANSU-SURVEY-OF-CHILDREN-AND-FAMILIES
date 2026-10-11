"""Shared helpers: data loading, OLS with village-clustered SEs, wild cluster bootstrap, Benjamini-Hochberg."""
import os, warnings
import numpy as np, pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
warnings.filterwarnings('ignore')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
P1 = os.path.join(ROOT, 'Paper1_GSCF')
TAB = os.path.join(P1, 'output', 'tables'); FIG = os.path.join(P1, 'output', 'figures')
for p in (TAB, FIG): os.makedirs(p, exist_ok=True)

def load():
    d = pd.read_csv(os.path.join(P1, 'data_clean', 'analysis_child_2000cohort.csv'))
    d['female0'] = d.female.fillna(0)
    return d

CTRL = ['C(age00_c)', 'female0', 'sex_missing', 'father_age', 'mother_age', 'C(sibs_cat)', 'firstborn', 'any_brother', 'ses', 'C(county)']
NEEDED = ['father_age', 'mother_age', 'ses']

OUTCOMES = [('z_cogacad', 'Cognitive and academic composite'),
            ('z_cog00', 'Cognitive test, 2000'), ('z_ach00', 'Achievement test, 2000'),
            ('z_chi04', 'Chinese test, 2004'), ('z_mat04', 'Mathematics test, 2004'),
            ('z_lit04', 'Literacy test, 2004'), ('z_lit09', 'Literacy test, 2009'),
            ('z_height04', 'Height (z), 2004')]

def fit(d, y, x, ctrl=None, extra=(), cluster='vid', weights=None, drop_ctrl=()):
    ctrl = [c for c in (CTRL if ctrl is None else ctrl) if c not in drop_ctrl]
    terms = [x] if isinstance(x, str) else list(x)
    rhs = terms + list(extra) + ctrl + (['math_form'] if y == 'z_ach00' else [])
    cols = [y] + [t for t in terms] + NEEDED + [cluster] + ([weights] if weights else [])
    # variables inside extra terms (interactions) must be present too
    import re
    need = set(cols)
    for e in extra:
        for tok in re.findall(r'[A-Za-z_][A-Za-z0-9_]*', e):
            if tok in d.columns: need.add(tok)
    dd = d.dropna(subset=[c for c in need if c in d.columns]).copy()
    f = y + ' ~ ' + ' + '.join(rhs)
    if weights:
        m = smf.wls(f, dd, weights=dd[weights]).fit(cov_type='cluster', cov_kwds={'groups': dd[cluster]})
    else:
        m = smf.ols(f, dd).fit(cov_type='cluster', cov_kwds={'groups': dd[cluster]})
    return m, dd

def coef(m, name):
    b, se, p = m.params[name], m.bse[name], m.pvalues[name]
    return dict(b=b, se=se, p=p, lo=b - 1.96 * se, hi=b + 1.96 * se, n=int(m.nobs), r2=m.rsquared)

def bh(p):
    """Benjamini-Hochberg q-values."""
    p = np.asarray(p, float); n = len(p); o = np.argsort(p); q = np.empty(n)
    prev = 1.0
    for rank, i in zip(range(n, 0, -1), o[::-1]):
        prev = min(prev, p[i] * n / rank); q[i] = prev
    return q

def wild_cluster_p(d, y, x, ctrl=None, cluster='vid', B=1999, seed=20260101):
    """Wild cluster bootstrap-t p-value (Rademacher weights, null imposed) for coefficient on x."""
    rng = np.random.default_rng(seed)
    ctrl = CTRL if ctrl is None else ctrl
    rhs = [x] + ctrl + (['math_form'] if y == 'z_ach00' else [])
    dd = d.dropna(subset=[y, x] + NEEDED + [cluster]).copy()
    import patsy
    Y, X = patsy.dmatrices(y + ' ~ ' + ' + '.join(rhs), dd, return_type='dataframe')
    Y = Y.values.ravel(); Xn = X.values; names = list(X.columns)
    j = names.index(x); g = dd[cluster].values; ug, gi = np.unique(g, return_inverse=True); G = len(ug)
    def tstat(Yv, Xm):
        XtXi = np.linalg.pinv(Xm.T @ Xm); beta = XtXi @ Xm.T @ Yv; u = Yv - Xm @ beta
        S = np.zeros((Xm.shape[1],) * 2)
        sc = np.zeros((G, Xm.shape[1])); np.add.at(sc, gi, Xm * u[:, None])
        S = sc.T @ sc
        V = XtXi @ S @ XtXi * (G / (G - 1))
        return beta[j] / np.sqrt(V[j, j]), beta
    t0, _ = tstat(Y, Xn)
    Xr = np.delete(Xn, j, axis=1)
    br = np.linalg.pinv(Xr.T @ Xr) @ Xr.T @ Y; fit_r = Xr @ br; ur = Y - fit_r
    cnt = 0
    for _ in range(B):
        w = rng.choice([-1.0, 1.0], size=G)[gi]
        tb, _ = tstat(fit_r + ur * w, Xn)
        cnt += abs(tb) >= abs(t0)
    return (cnt + 1) / (B + 1), t0
