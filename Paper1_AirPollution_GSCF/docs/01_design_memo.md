# Design memo: Paper 1 (GSCF, air pollution and child development)

## 1. What the data can support (verified in the repository files)
- GSCF waves 2000, 2004, 2007, 2009, 2015. Linkage file GSCF_merge_pid.dta: 5,119 rows, person IDs per wave
  (pid00 n=4,639; pid04 n=4,464; pid07 n=4,152; pid09 n=4,471; pid15 n=3,894).
- Child birth years in the linkage file: median 1989, IQR 1987 to 1990 (some outliers, 1969 to 2011, to be cleaned).
- Wave 1 mother file (moth2000ts.dta, n=2,000): mh2 gestational age (categories), mh3 birth weight (three
  categories, 1,422 in the modal category, 320 in category 1, 237 in category 3), mh4 birth weight estimate in
  jin-style units (to be checked against the codebook), mh5 delivery place.
- Wave 1 child file (child2000t.dta, n=2,000): a1 = county code (20 counties), a2 township (42), a3 village.
- Outcomes: achieve2000t (Chinese and math scores), litracy2000t (cognitive score), literacy2004t, achieve2004s/t,
  health2004t (height, weight, hemoglobin, zinc, lung capacity, vision), literacy2007n, literacy2009t.
- No household fuel, smoking or respiratory-morbidity variables were found by label search in the mother, child
  or village files; household air pollution therefore cannot be modelled directly without a codebook check.

## 2. Mismatch with the original Study 2 brief
The brief (CFPS, CEPS, post-2013 air quality improvement, hukou stratification) does not map onto GSCF.
- Gansu only; rural; cohorts born 1987 to 1991. The 2013 Clean Air Action falls outside every child-development
  wave; it touches only the 2015 adult follow-up.
- Satellite-derived PM2.5 products start in 1998, so prenatal exposure for these births cannot be measured from
  them. Reanalysis aerosol products (e.g., MERRA-2 from 1980) can, with larger measurement error.
- Hukou/migrant stratification has little leverage in a rural Gansu sample.

## 3. Proposed refined research questions (to be confirmed)
RQ1. Does county-level PM2.5 during gestation and infancy (reanalysis-based) predict birth weight category and
     gestational age reported by mothers in 2000?
RQ2. Does cumulative exposure between the 2000 and 2007 waves reduce cognitive and academic test scores,
     child fixed effects, and does exposure in sensitive school ages matter more?
RQ3. Is the association stronger for children from lower-SES households and for those with older co-resident
     adults (an aging link through multigenerational households)? In 2015, do childhood exposure effects persist
     into adult education and health?

## 4. Identification options
- Child and county fixed effects with year-to-year variation in PM2.5 (two-way FE, cluster at county, 20 clusters,
  so wild cluster bootstrap is required).
- Instrument: natural dust events (Gobi and Taklimakan dust days) or thermal inversion frequency.
- Placebos: future exposure; sibling comparisons (target_sib04 in the linkage file).

## 5. Inputs that cannot be obtained in this session
- Annual PM2.5 grids (e.g., ACAG V5/V6.GL, MERRA-2) and China county boundaries or county coordinates.
- Crosswalk from GSCF numeric county codes (a1, countyid in county2007.dta) to county names. This has to come
  from the GSCF codebook; it has not been guessed.

## 6. Target journals (RUC 2022 list, local files)
Candidates found in the local RUC catalogue and strategy workbook: Demography (A+), Population and Development
Review (A), Population Studies (A), Social Science & Medicine (A), Journals of Gerontology Series B (A),
Population and Environment (listed under Demography; tier to be confirmed in the catalogue),
Journal of Population Economics and Economics of Education Review (listed under Economics and Education).
Open-access status under the Penn agreements has not been checked (the Penn and OpenJournalFinder pages are not
reachable from this session).
Provisional first choice: Population and Environment or Social Science & Medicine for the environmental-health
framing; Demography only if the exposure design is strengthened.
