"""02_diagnostic_figures.py: figures from the real ERA5 extract that show why county-level matching is required.
Fig D1: mean annual precipitation and temperature by 1.5 degree cell with the Gansu boundary.
Fig D2: province-mean annual temperature and precipitation anomalies 1980-2009 with GSCF birth cohorts and survey waves marked.
Output: output/figures/FigureD1_gansu_climate_cells.*, FigureD2_gansu_climate_series.* (SVG, PDF, PNG 600 dpi)."""
import os, json
import numpy as np, pandas as pd
import matplotlib as mpl; mpl.use('Agg')
import matplotlib.pyplot as plt
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')); FIG = f'{ROOT}/output/figures'; os.makedirs(FIG, exist_ok=True)
plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'Liberation Sans', 'DejaVu Sans'], 'font.size': 9, 'axes.linewidth': 0.8,
                     'axes.spines.top': False, 'axes.spines.right': False, 'svg.fonttype': 'none', 'pdf.fonttype': 42, 'figure.facecolor': 'white', 'savefig.facecolor': 'white'})
BLUE, VERM, GREY = '#0072B2', '#D55E00', '#6b6b6b'
def save(fig, name):
    fig.savefig(f'{FIG}/{name}.svg', bbox_inches='tight'); fig.savefig(f'{FIG}/{name}.pdf', bbox_inches='tight'); fig.savefig(f'{FIG}/{name}.png', dpi=600, bbox_inches='tight'); plt.close(fig)
c = pd.read_csv(f'{ROOT}/data_external/era5_gansu_cells_monthly.csv')
gj = json.load(open(f'{ROOT}/data_external/gansu_adm1.geojson'))['features'][0]['geometry']
polys = gj['coordinates'] if gj['type'] == 'MultiPolygon' else [gj['coordinates']]
cell = c.groupby(['lon', 'lat', 'in_gansu']).apply(lambda x: pd.Series({'T': x.tmean.mean(), 'P': x.precip.sum() / x.year.nunique()})).reset_index()
fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.6))
for a, (v, lab, cmap) in zip(ax, [('P', 'Mean annual precipitation (mm)', 'Blues'), ('T', 'Mean annual temperature (degrees C)', 'RdYlBu_r')]):
    for p in polys:
        for ring in p:
            xy = np.array(ring); a.plot(xy[:, 0], xy[:, 1], color='black', lw=0.7)
    s = cell[(cell.lon >= 91) & (cell.lon <= 110) & (cell.lat >= 31) & (cell.lat <= 43.5)]
    sc = a.scatter(s.lon, s.lat, c=s[v], s=np.where(s.in_gansu == 1, 70, 18), cmap=cmap, edgecolor=np.where(s.in_gansu == 1, 'black', 'none'), linewidth=0.5, zorder=3)
    cb = fig.colorbar(sc, ax=a, shrink=0.8, pad=0.04); cb.set_label(lab, fontsize=8.5); cb.outline.set_linewidth(0.5)
    a.set_xlabel('Longitude (E)'); a.set_ylabel('Latitude (N)'); a.set_aspect('equal'); a.set_xlim(91, 109.5); a.set_xticks([95, 100, 105]); a.set_ylim(31, 43.5)
ax[0].text(-0.02, 1.05, 'A', transform=ax[0].transAxes, fontsize=11, fontweight='bold'); ax[1].text(-0.02, 1.05, 'B', transform=ax[1].transAxes, fontsize=11, fontweight='bold')
fig.tight_layout(); save(fig, 'FigureD1_gansu_climate_cells')

g = c[c.in_gansu == 1]
ann = g.groupby(['year', 'lon', 'lat']).agg(T=('tmean', 'mean'), P=('precip', 'sum')).reset_index()
cm = ann.groupby(['lon', 'lat']).agg(T0=('T', 'mean'), P0=('P', 'mean'), Ps=('P', 'std')).reset_index(); ann = ann.merge(cm, on=['lon', 'lat'])
ann['Ta'] = ann['T'] - ann.T0; ann['Pz'] = (ann.P - ann.P0) / ann.Ps
prov = ann.groupby('year').agg(Ta=('Ta', 'mean'), Pz=('Pz', 'mean'), Pz_sd=('Pz', 'std')).reset_index()
fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0), sharex=True)
for a, (v, lab, col) in zip(ax, [('Ta', 'Temperature anomaly (degrees C)', VERM), ('Pz', 'Precipitation anomaly (z)', BLUE)]):
    a.axvspan(1986.5, 1991.5, color='#dddddd', lw=0); a.axhline(0, color='black', lw=0.6)
    a.plot(prov.year, prov[v], color=col, lw=1.6, marker='o', ms=3)
    for w in (2000, 2004, 2009): a.axvline(w, color=GREY, lw=0.8, ls=':')
    a.set_xlabel('Year'); a.set_ylabel(lab)
ax[0].text(-0.02, 1.05, 'A', transform=ax[0].transAxes, fontsize=11, fontweight='bold'); ax[1].text(-0.02, 1.05, 'B', transform=ax[1].transAxes, fontsize=11, fontweight='bold')
ax[1].text(1989, ax[1].get_ylim()[1] * 0.92, 'Birth cohorts', ha='center', fontsize=8, color=GREY)
fig.tight_layout(); save(fig, 'FigureD2_gansu_climate_series')
# variation decomposition for the design memo
tot = ann.Pz.var(); between_year = prov.Pz.var()
print('SD of annual precipitation z within cells:', ann.Pz.std().round(2), '| SD of province-mean z across years:', prov.Pz.std().round(2))
print('Across-cell SD of mean annual precipitation (mm):', cm.P0.std().round(0), 'mean', cm.P0.mean().round(0), '| SD of province-mean annual precip (mm):', ann.groupby('year').P.mean().std().round(0))
print('Across-cell SD of mean annual temperature (C):', cm.T0.std().round(2), '| SD of province-mean annual T anomaly:', prov.Ta.std().round(2))
