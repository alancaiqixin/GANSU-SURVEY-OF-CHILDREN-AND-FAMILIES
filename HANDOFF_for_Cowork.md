# Handoff: GSCF papers 1 and 2 (for continuation in Cowork)

Owner: Qixin Cai (PARC, University of Pennsylvania). Repo: alancaiqixin/GANSU-SURVEY-OF-CHILDREN-AND-FAMILIES, branch `claude/jolly-carson-j0pjzi` (all work is committed and pushed there).
Cloud session: https://claude.ai/code/session_01KJLhCiGqY4iSpsTFAStasd

## 1. What was asked (standing instructions, keep applying)
- Topic: climate, environment and child development, with an aging link where possible. Methods inspired by `ClimateDataIntro-main` (gridded climate data joined to polygons).
- Paper 1 (brief): air pollution, birth outcomes, early development in China. Paper 2: climate, environment and child development.
- Deliverables per paper: independent reproduction do-file folder; Stata analysis (Stata 16 at /Applications/Stata 16/StataSE.app/Contents/MacOS/StataSE, verify by driving the GUI); at least 4 main tables and 4 main figures in docx, unlimited appendix; robustness and endogeneity checks; outputs saved to the external drive (/Volumes/My Passport/Source_初始数据库 holds the full raw data); AER-level standard of care.
- Journal: RUC 2022 core list, B and above (local files: `中国人民大学核心期刊目录2022版.docx`, `A类及以上期刊战略布局.xlsx`), ideally Penn OA agreement journals (https://guides.library.upenn.edu/penn-oa-agreements, upenn.openjournalfinder.com).
- Writing: SSCI style, concise, no dashes of any kind in body text (no em dash, en dash), active voice, American spelling, no generic transitions.
- Files: anonymous manuscript, Title Page, Cover Letter, Highlights, Tables, Figures (docx). All headings must use Word built-in Heading 1 to 3, with a three-level TOC and working navigation pane.
- Figures: white background, Arial 9 to 11 pt, colorblind-safe, no gridlines or 3D, SVG + PDF + PNG at 600 dpi and at least 3000 px wide. Stata figures: clean scheme, white regions.
- Literature: about 50 English-language top-journal references, no Chinese sources, every reference verified against a real source (rule: better to omit than cite something unverifiable).

## 2. Environment facts (why things are the way they are)
- The cloud container has no Stata, no `/Volumes/My Passport`, no `/Applications`. Stata do-files were written but never executed. All numbers come from the Python pipeline.
- Network is restricted. Reachable: PyPI, `media.githubusercontent.com` (git LFS files of public repos), `raw.githubusercontent.com`, `storage.googleapis.com` (public GCS buckets, anonymous). Blocked: sites.wustl.edu (ACAG PM2.5), zenodo.org, geodata.ucdavis.edu, geoboundaries.org, earthdata, CHIRPS host, CDS, doi.org, CrossRef.
- Consensus (30 searches/month) and Scholar Gateway free quotas were exhausted; they reset on 1 November 2026. No reference could be verified online.
- Arial is not installed in the container; figures fall back to Liberation Sans (SVG files name Arial first).
- Data in the repo is a subset of GSCF: no household roster files (parental education, income, ethnicity, grandparents), no 2015 child files. County names are masked (codes 31 to 50 in `a1`).

## 3. Paper 1 (done as a draft): `Paper1_GSCF/`
Title: "Birth Weight, Parental Investment, and Child Development in Rural China: Evidence from the Gansu Survey of Children and Families". Provisional target: Social Science & Medicine (backups: JMF, Population Studies, Demography). Penn OA status unchecked.
Why the topic changed: GSCF has no pollution or climate variable and external pollution data could not be downloaded, so Paper 1 uses the data's real strengths: maternal-reported birth weight and gestation (moth2000ts: mh2 to mh5), tests 2000/2004/2009, height 2004, parental investment, old-age support expectations (md1h, md2, md3), village water and environment ratings.
Sample: 2,000 target children, 100 villages, 20 counties; age 9 to 12 in 2000 (born 1987 to 1991).
Design: OLS, county FE, village-clustered SE, standardized outcomes; BH q-values; wild cluster bootstrap; Oster bounds; E-values; IPW for attrition; negative control outcomes; exploratory interactions.
Key results (do not overstate):
- Height (2004): 0.17 SD per kg of birth weight (95% CI 0.08 to 0.26; about 1.3 cm), robust (q = 0.003; wild bootstrap p < 0.01; IPW 0.18).
- Cognitive and academic composite: 0.07 SD per kg (95% CI -0.03 to 0.17), positive in all specifications, never significant at 5%.
- Estimated weight below 2.5 kg: height -0.29 SD (p = 0.004), composite -0.15 (p = 0.078). Preterm: no consistent pattern.
- Investment: reinforcing, not compensating (books for <2.5 kg children -0.21 SD, p < 0.001, q < 0.05; lower aspirations).
- Heterogeneity by old-age expectations and reliance on sons: exploratory only; all 28 interaction q-values >= 0.060.
- Caveat found by negative control: birth weight correlates with the mother's subjective village-environment rating (p = 0.011), so subjective reports share a reporting tendency. Objective village water share shows no association.
Folder map: `code_py/` (01_build_data, 02_models, 03_figures, 04_build_word, lib, wordlib, manuscript_text, refs, verify_refs), `dofiles/` (00_master to 05_figures, untested), `data_clean/`, `output/` (tables csv, figures svg/pdf/png, results.pkl), `manuscript/` (7 docx), `docs/`, `README.md`.
Reproduce: `cd Paper1_GSCF/code_py; python3 01_build_data.py; python3 02_models.py; python3 03_figures.py; python3 04_build_word.py` (needs pandas, statsmodels, matplotlib, python-docx, shapely not needed).
Open items for Paper 1:
1. References: 56 entries written from memory (refs.py). Run `python3 code_py/verify_refs.py` with internet (CrossRef), fix flagged items, and read each source to confirm it supports the sentence citing it. A yellow drafting note sits above the reference list; delete after verification.
2. Add parental education, household income, ethnicity from the household files on the external drive and rerun (the manuscript names this as the main limitation).
3. Run the Stata do-files on the Mac (edit `root` in 00_master.do) and diff against `output/tables/*.csv`.
4. Placeholders in yellow: co-authors, funding, conflicts, ethics, suggested reviewers, AI-use wording. Table 4 note, abstract (192 words) and highlights (4, <= 85 characters) follow Social Science & Medicine conventions as recalled; check current guidelines.
5. In Word: right-click TOC, Update Field (page numbers were cached from LibreOffice layout).
6. Relationship codes in GSCF_merge_pid (2x older brother, 3x younger brother, 4x older sister, 5x younger sister) were inferred from birth-year patterns; confirm in the codebook.

## 4. Paper 2 (infrastructure only): `Paper2_ClimateEnv_GSCF/`
Blocking input: GSCF county code to county name or coordinates. Without it climate cannot be assigned below province level. A province-wide test had almost no identifying variation (prenatal temperature anomaly SD about 0.3 C) and is not reported; do not cite it.
Built and tested:
- `code_py/01_fetch_era5.py`: ERA5 from the WeatherBench 2 public copy (gs://weatherbench2/datasets/era5/1959-2022-6h-240x121_equiangular_with_poles_conservative.zarr, 1.5 degree, 6-hourly) aggregated to a monthly grid-cell panel 1980 to 2009 (tmean, tmax6, tmin6, cold and hot days, precipitation, wet days); Gansu polygon from geoBoundaries ADM1 through media.githubusercontent.com; 18 cells inside Gansu; output `data_external/era5_gansu_cells_monthly.csv` (48,600 rows) and `gansu_adm1.geojson`.
- Validation: mean annual precipitation 424 mm (cells 50 to 1,210 mm), warming about 1.4 C from the 1980s to the 2000s. Across-cell SD of annual precipitation 368 mm versus 41 mm for the province-mean series across years.
- `code_py/02_diagnostic_figures.py`: Figures D1 and D2 (svg/pdf/png in `output/figures`).
- `code_py/03_build_exposures.py`: county-level windows (preconception, prenatal, trimesters, infancy, ages 1 to 3) by inverse-distance weighting of four nearest cells; runs once `data_external/county_crosswalk.csv` exists (template: `code_py/county_crosswalk_template.csv`, columns county 31 to 50, county_name, lat, lon). Code path tested only with a synthetic crosswalk in the scratchpad (discarded).
Planned analysis (docs/01_design_memo.md): county FE + birth-month-of-year FE + birth-year FE; placebo with preconception window; wild cluster bootstrap with 20 counties; heterogeneity by household resources, sex, old-age support expectation, village terrain (vill2004/2007 vb5) and rainwater use (vill2004 vd2d1); Oster, leads, attrition weights. Birth month exists only in health2004t (about 1,740 children).
Not started: models, tables, figures for results, Stata do-files, manuscript package, literature.
Possible extra data: ClimateDataIntro contains only Philadelphia UTCI files, Pennsylvania counties, and Bangladesh DHS 2017-18 cluster GPS (no survey outcomes); not usable for GSCF. The wid-world repo is unrelated (inequality series).

## 5. Suggested first steps in Cowork
1. Pull branch `claude/jolly-carson-j0pjzi`; copy the project to the external drive if desired.
2. Supply the county crosswalk (from the GSCF codebook or `Source_初始数据库`), then run Paper 2 steps 03 onward; ask for the models, tables, figures and manuscript package to be built with the same toolchain as Paper 1 (`wordlib.py`, `04_build_word.py`).
3. Where Stata is available, run the do-files and verify; use CrossRef/Consensus (after 1 Nov) to verify the reference lists.
4. If the full GSCF household files are available, rerun Paper 1 with parental education, income and ethnicity.

## 6. Paste-ready starting prompt for Cowork
"Continue the GSCF research project. Read HANDOFF_for_Cowork.md at the repo root and the README.md in Paper1_GSCF and Paper2_ClimateEnv_GSCF. Do not fabricate data or citations. Priorities: (a) verify the 56 references in Paper1_GSCF/code_py/refs.py against CrossRef and check each supports its citing sentence; (b) use the county crosswalk I provide to build Paper 2 exposures, run the models, and produce at least 4 tables and 4 figures plus robustness and endogeneity checks; (c) run the Stata do-files and reconcile with the Python output; (d) keep all headings in Word built-in styles and avoid any dashes in manuscript text."
