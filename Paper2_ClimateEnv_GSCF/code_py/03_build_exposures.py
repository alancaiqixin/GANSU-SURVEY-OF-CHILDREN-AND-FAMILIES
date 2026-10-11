"""03_build_exposures.py: county-level ERA5 exposure windows for each GSCF child.
REQUIRES data_external/county_crosswalk.csv with columns county (GSCF code 31 to 50), lat, lon (decimal degrees).
The GSCF files mask county names, so the crosswalk must come from the GSCF codebook or the data custodian.
Method: inverse-distance weighting of the four nearest 1.5 degree ERA5 cells to the county point; monthly anomalies relative to the
county's own 1980-2009 calendar-month mean; windows defined relative to the child's birth month (health2004t: byear, bmonth).
Output: data_clean/analysis_climate.csv (Paper 1 analysis file + exposure windows).
Set CROSSWALK and OUTDIR environment variables to test with a synthetic file outside the project (never for results)."""
import os, sys
import numpy as np, pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CW = os.environ.get('CROSSWALK', f'{ROOT}/data_external/county_crosswalk.csv')
OUT = os.environ.get('OUTDIR', f'{ROOT}/data_clean'); os.makedirs(OUT, exist_ok=True)
if not os.path.exists(CW):
    sys.exit(f'Missing {CW}. Fill code_py/county_crosswalk_template.csv (county code, name, lat, lon) and save it as data_external/county_crosswalk.csv.')
cw = pd.read_csv(CW)
assert cw[['lat', 'lon']].notna().all().all() and cw.county.nunique() == 20, 'crosswalk needs 20 counties with coordinates'
c = pd.read_csv(f'{ROOT}/data_external/era5_gansu_cells_monthly.csv')
cells = c[['lon', 'lat']].drop_duplicates().reset_index(drop=True)

def hav(lat1, lon1, lat2, lon2):
    p = np.pi / 180; a = np.sin((lat2 - lat1) * p / 2) ** 2 + np.cos(lat1 * p) * np.cos(lat2 * p) * np.sin((lon2 - lon1) * p / 2) ** 2
    return 12742 * np.arcsin(np.sqrt(a))

series = []
for r in cw.itertuples():
    dist = hav(r.lat, r.lon, cells.lat.values, cells.lon.values); k = np.argsort(dist)[:4]
    w = 1 / np.maximum(dist[k], 1.0); w = w / w.sum()
    sub = c.merge(cells.iloc[k].assign(w=w), on=['lon', 'lat'])
    for v in ('tmean', 'precip', 'days_cold', 'days_hot'): sub[v] = sub[v] * sub.w
    m = sub.groupby(['year', 'month'])[['tmean', 'precip', 'days_cold', 'days_hot']].sum().reset_index()
    m['county'] = r.county; m['nearest_km'] = float(dist[k[0]]); series.append(m)
S = pd.concat(series)
for v in ('tmean', 'precip', 'days_cold'):
    g = S.groupby(['county', 'month'])[v]
    S[v + '_a'] = S[v] - g.transform('mean'); S[v + '_z'] = S[v + '_a'] / g.transform('std')
S['idx'] = (S.year - 1980) * 12 + S.month - 1
S = S.set_index(['county', 'idx']).sort_index()

d = pd.read_csv(f'{ROOT}/../Paper1_GSCF/data_clean/analysis_child_2000cohort.csv')
h = pd.read_stata(f'{ROOT}/../health2004t.dta', convert_categoricals=False)[['hhid', 'byear', 'bmonth']]
h = h[h.bmonth.between(1, 12) & h.byear.between(1984, 1992)].drop_duplicates('hhid')
d = d.merge(h, on='hhid', how='left'); d['bidx'] = (d.byear - 1980) * 12 + d.bmonth - 1
WINDOWS = {'preconception': (-18, -10), 'prenatal': (-9, -1), 'tri1': (-9, -7), 'tri2': (-6, -4), 'tri3': (-3, -1), 'infancy': (0, 11), 'age1to3': (12, 47)}
def window(county, idx, a, b, col):
    if pd.isna(idx): return np.nan
    return S.loc[(county, int(idx) + a):(county, int(idx) + b), col].mean()
for name, (a, b) in WINDOWS.items():
    for col in ('tmean_a', 'precip_z', 'days_cold_a'):
        d[f'{name}_{col}'] = [window(cty, i, a, b, col) for cty, i in zip(d.county, d.bidx)]
for name in ('prenatal', 'infancy'):
    d[f'{name}_dry'] = (d[f'{name}_precip_z'] <= -0.5).astype(float).where(d[f'{name}_precip_z'].notna())
d.to_csv(f'{OUT}/analysis_climate.csv', index=False)
print(d.shape, 'children with exposure windows:', int(d.prenatal_tmean_a.notna().sum()))
print(d[['prenatal_tmean_a', 'prenatal_precip_z', 'infancy_tmean_a', 'infancy_precip_z']].describe().round(2).T)
