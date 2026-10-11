# Design memo: Paper 2 (climate, environment and child development)

## Refined research questions
RQ1. Do temperature and precipitation anomalies in utero and in the first three years of life predict adolescent height and cognitive and
     academic scores among rural Gansu children born 1987 to 1991?
RQ2. Are the associations concentrated in drought or cold-stress months, and in households with fewer resources?
RQ3. (Aging link) Do parental expectations of old-age support from children, a proxy for household reliance on child outcomes, change the
     climate gradient in parental investment and child outcomes?

## Data in hand
- Outcomes and covariates: Paper 1 analysis file (2,000 children, 100 villages, 20 counties). Birth month is available only in health2004t
  (n about 1,740 with valid month); sex from 2004 files.
- Climate: ERA5 monthly grid-cell panel 1980 to 2009 (data_external), validated against known Gansu climatology.
- Village terrain (vill2004/2007: vb5) and rainwater use (vill2004: vd2d1) are available as moderators once checked against the codebook.

## Identification
Variation in county-specific monthly anomalies across birth months within county, after birth-month-of-year and birth-year fixed effects.
The conventional assumptions are that weather anomalies are as good as random conditional on place and season, and that migration is limited
(the sample is rural and sedentary). Threats: coarse 1.5 degree reanalysis (smoothed terrain, so anomalies not levels), exposure windows that
overlap, 20 clusters (wild bootstrap), and attrition.

## Why a provincial design is not credible
Using one Gansu-wide series leaves only five birth cohorts and 60 birth months of variation (prenatal temperature anomaly SD about 0.3 C),
and fixed effects absorb most of it. Across 1.5 degree cells, by contrast, mean annual precipitation varies by 368 mm (SD) while the province
mean varies by 41 mm across years. County placement is therefore the binding requirement.

## Target journals (RUC 2022 list and workbook; tiers to be confirmed in the catalogue)
Population and Environment (listed under Demography), Demography (A+), Social Science & Medicine (A), Journal of Environmental Economics and
Management and Journal of Population Economics (listed under Economics). Open-access status under Penn agreements not checked (pages unreachable).
