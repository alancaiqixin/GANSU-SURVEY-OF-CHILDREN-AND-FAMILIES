# Design memo (revised after data audit)

## Why the original air pollution design was not feasible with the available inputs
- GSCF cohorts were born 1987 to 1991; satellite PM2.5 products start in 1998, and no pollution or climate files
  are in the repositories. External hosts for gridded data and county boundaries were blocked in the session.
- CFPS and CEPS, hukou stratification and the 2013 Clean Air Action do not map onto a Gansu-only rural cohort.

## Question answered with the data in hand
RQ1 Does maternal-reported birth weight predict adolescent height and cognitive and academic scores (2000 to 2009)?
RQ2 Do parents reinforce or compensate in investment in learning?
RQ3 Are gradients steeper where mothers expect old-age support from children (aging link), and do they vary with
    household resources, sex and village environment?

## Data facts (verified in the files)
- 2,000 target children, 100 villages, 20 counties; mother birth items in moth2000ts (mh2 gestation, mh3 weight category,
  mh4 weight in jin, mh5 delivery place). Tests: 2000, 2004, 2009; measured height 2004. Sex only in 2004 files.
- Household roster files (parental education, income, ethnicity, grandparents) are not in the repository.
- Relationship codes in GSCF_merge_pid (2x older brother, 3x younger brother, 4x older sister, 5x younger sister) were
  inferred from birth-year patterns and should be confirmed in the codebook.

## Findings (see manuscript)
Height gradient 0.17 SD per kg (robust); cognitive and academic gradient 0.07 SD per kg (imprecise); reinforcing
investment; exploratory old-age moderation (q above 0.05).

## Not feasible and why
Sibling fixed effects (no sibling birth items), instruments (none credible), pollution exposure (no data).
