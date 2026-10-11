"""01_fetch_era5.py
Download Gansu province boundary (geoBoundaries ADM1, via media.githubusercontent.com) and ERA5 reanalysis
(WeatherBench 2 copy on public Google Cloud Storage: 1.5 degree grid, 6-hourly) and aggregate to a monthly grid-cell panel.
Variables: 2 m temperature (t2m) and 24 h accumulated total precipitation.
Output: data_external/era5_gansu_cells_monthly.csv, data_external/gansu_adm1.geojson
Method follows ClimateDataIntro (gridded climate data joined to polygons), implemented in Python with shapely.
Note: 1.5 degree cells (about 150 km) smooth terrain, so analyses use deviations from each cell's own monthly climatology."""
import os, json, urllib.request, sys
import numpy as np, pandas as pd, xarray as xr
from shapely.geometry import shape, Point

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
EXT = os.path.join(ROOT, 'data_external'); os.makedirs(EXT, exist_ok=True)
Y0, Y1 = int(sys.argv[1]) if len(sys.argv) > 1 else 1980, int(sys.argv[2]) if len(sys.argv) > 2 else 2009

gj = os.path.join(EXT, 'gansu_adm1.geojson')
if not os.path.exists(gj):
    url = 'https://media.githubusercontent.com/media/wmgeolab/geoBoundaries/main/releaseData/gbOpen/CHN/ADM1/geoBoundaries-CHN-ADM1_simplified.geojson'
    allf = json.load(urllib.request.urlopen(url, timeout=120))
    names = [f['properties'].get('shapeName') for f in allf['features']]
    print('ADM1 names:', names)
    feats = [f for f in allf['features'] if 'gansu' in str(f['properties'].get('shapeName', '')).lower()]
    assert len(feats) == 1
    json.dump({'type': 'FeatureCollection', 'features': feats}, open(gj, 'w'))
poly = shape(json.load(open(gj))['features'][0]['geometry'])
print('Gansu bounds', poly.bounds)

ds = xr.open_zarr('gcs://weatherbench2/datasets/era5/1959-2022-6h-240x121_equiangular_with_poles_conservative.zarr',
                  consolidated=True, storage_options={'token': 'anon'})
lat0, lat1, lon0, lon1 = 30.0, 44.0, 90.0, 112.0
box = ds[['2m_temperature', 'total_precipitation_24hr']].sel(latitude=slice(lat0, lat1), longitude=slice(lon0, lon1))
lons, lats = box.longitude.values, box.latitude.values
inside = np.array([[poly.contains(Point(lo, la)) for la in lats] for lo in lons])
print('grid cells inside Gansu:', int(inside.sum()), 'of', inside.size)
cells = [(i, j) for i in range(len(lons)) for j in range(len(lats))]

rows = []
for yr in range(Y0, Y1 + 1):
    b = box.sel(time=slice(f'{yr}-01-01', f'{yr}-12-31 23:59')).load()
    T = b['2m_temperature'].transpose('time', 'longitude', 'latitude').values - 273.15
    P = b['total_precipitation_24hr'].transpose('time', 'longitude', 'latitude').values * 1000.0   # mm over the preceding 24 h
    tt = pd.DatetimeIndex(b.time.values)
    nd = len(tt) // 4
    assert len(tt) % 4 == 0 and tt[0].hour == 0 and tt[0].dayofyear == 1, (yr, len(tt))
    T4 = T.reshape(nd, 4, *T.shape[1:]); P4 = P.reshape(nd, 4, *P.shape[1:])
    tmean, tmax, tmin = T4.mean(1), T4.max(1), T4.min(1)
    pday = P4[:, 0]                                                    # accumulation at 00 UTC = previous day total
    mon = pd.date_range(f'{yr}-01-01', periods=nd).month.values
    for m in range(1, 13):
        k = mon == m
        rec = {'tmean': tmean[k].mean(0), 'tmax6': tmax[k].mean(0), 'tmin6': tmin[k].mean(0), 'days_cold': (tmean[k] < -10).sum(0),
               'days_hot': (tmax[k] >= 28).sum(0), 'precip': pday[k].sum(0), 'wetdays': (pday[k] >= 1.0).sum(0)}
        for (i, j) in cells:
            rows.append((yr, m, float(lons[i]), float(lats[j]), int(inside[i, j])) + tuple(float(rec[v][i, j]) for v in ('tmean', 'tmax6', 'tmin6', 'days_cold', 'days_hot', 'precip', 'wetdays')))
    print('done', yr, flush=True)
df = pd.DataFrame(rows, columns=['year', 'month', 'lon', 'lat', 'in_gansu', 'tmean', 'tmax6', 'tmin6', 'days_cold', 'days_hot', 'precip', 'wetdays'])
df.to_csv(os.path.join(EXT, 'era5_gansu_cells_monthly.csv'), index=False)
print(df.shape, df.groupby('in_gansu').size().to_dict())
