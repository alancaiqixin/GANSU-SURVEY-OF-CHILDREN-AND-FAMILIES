# Paper 2: Climate, environment and child development (GSCF + ERA5)

STATUS: data infrastructure built and tested; analysis, tables and manuscript NOT produced yet because one input is missing.

## Missing input: GSCF county locations
The GSCF files identify counties only by code (31 to 50; variable a1) and mask county names. Without a crosswalk from code to
county name or coordinates, climate cannot be assigned to children at any spatial scale finer than the province. A province-wide
test (all children share one exposure series, only birth cohort 1987 to 1991 varies) was run for diagnosis only: exposure variation
is tiny (SD of 9-month prenatal temperature anomaly about 0.3 C, 60 birth months) and coefficients are unstable, so no result from it
is reported or should be cited.
Fix: fill `code_py/county_crosswalk_template.csv` (county, county_name, lat, lon, source_of_coordinates) from the GSCF codebook or from
the data custodian, save as `data_external/county_crosswalk.csv`, then run `python3 code_py/03_build_exposures.py`.

## What exists
- code_py/01_fetch_era5.py   ERA5 (WeatherBench 2 copy on public Google Cloud Storage, 1.5 degree, 6-hourly) aggregated to a monthly
                              grid-cell panel 1980 to 2009 (t2m, daily min/max of 6-hourly values, cold and hot days, precipitation, wet days).
                              Gansu polygon from geoBoundaries ADM1 (media.githubusercontent.com). 18 cells fall inside Gansu.
- code_py/02_diagnostic_figures.py  Figures D1 (cell climate map) and D2 (province series with cohorts and waves); output/figures/*.
- code_py/03_build_exposures.py     County-level exposure windows (preconception, prenatal, trimesters, infancy, ages 1 to 3), anomalies
                                     relative to each county's own calendar-month mean; tested only with a synthetic crosswalk (discarded).
- data_external/              era5_gansu_cells_monthly.csv (48,600 rows), gansu_adm1.geojson
- Sanity check of the extract: Gansu mean annual precipitation 424 mm (cell range 50 to 1,210 mm), mean temperature warming about 1.4 C
  between the 1980s and 2000s; across-cell SD of mean annual precipitation 368 mm versus 41 mm for the province-mean series across years.

## Planned analysis (after crosswalk), see docs/01_design_memo.md
County FE + birth-month-of-year FE + birth-year FE; exposure = county-by-birth-month anomalies; placebo = preconception window;
cluster by county with wild cluster bootstrap; heterogeneity by household resources, sex, old-age support expectation (aging link),
village water and terrain; endogeneity checks (placebo windows, leads, Oster bounds, attrition weights, spatial-correlation robustness).
No Stata run is possible in the cloud container; do-files will be written with the analysis and must be run on the Mac.
