# Paper 1: Birth weight, parental investment and child development in rural Gansu (GSCF)

Target journal (provisional): Social Science & Medicine (RUC 2022 list: A; strategy workbook rank 9).
Backups: Journal of Marriage and Family, Population Studies, Demography (needs stronger identification).
Open-access status under the Penn agreements was NOT checked (Penn and OpenJournalFinder pages are unreachable
from the cloud session). Check the current author guidelines (abstract length, highlights, reference style).

## What this paper is, and what it is not
The brief asked for air pollution and child development. The GSCF files contain no pollution, temperature or
rainfall variable, and the session could not download external exposure data (network policy blocked
sites.wustl.edu, zenodo.org, geodata.ucdavis.edu, geoboundaries.org, earthdata.nasa.gov, doi.org). The paper was
therefore built on what the data support: birth endowments, child development, parental investment, and
old-age support expectations (the aging link). Village environment enters only as a mother-rated item and a
village drinking-water measure. `code_py/01_build_data.py` has a hook: if `data_external/county_exposure.csv`
(columns: county, plus exposure variables) exists it is merged, so a pollution module can be added later.

## Folder layout
- code_py/    Python pipeline that produced every number, table and figure in the manuscript
- dofiles/    Stata 16 do-files (00_master.do to 05_figures.do), mirror of the Python pipeline
- data_clean/ analysis_child_2000cohort.csv/.dta (2,000 target children; Python build)
- output/     tables (csv), figures (SVG, PDF, PNG at 600 dpi, width over 3000 px), results.pkl, logs
- manuscript/ Manuscript_Anonymous, Title_Page, Cover_Letter, Highlights, Tables, Figures, Supplementary_Appendix (docx)
- docs/       design memo

## Reproduce
Python: `cd code_py; python3 01_build_data.py; python3 02_models.py; python3 03_figures.py; python3 04_build_word.py`
Stata (on the Mac): edit the `root` global in dofiles/00_master.do, then `do 00_master.do`.
The Stata do-files were written but NOT run (Stata is not installed in the cloud container). Compare their output
with output/tables/*.csv before relying on them. Fonts: Arial is not installed in the container, so figures use
Liberation Sans (metric compatible); the SVG files name Arial first and will render in Arial where it is installed.

## Open items before submission
1. References: all 56 entries were written from memory. Consensus and Scholar Gateway quotas were exhausted and
   CrossRef was unreachable. Run `python3 code_py/verify_refs.py` with internet access, fix flagged entries, and
   read each source to confirm it supports the sentence that cites it. A highlighted drafting note sits above the
   reference list in the manuscript; delete it after verification.
2. Covariates: parental education, household income and ethnicity live in household questionnaire files that are
   not in this repository. Add them from the external drive (Source_初始数据库) and rerun; the manuscript names
   this as the main limitation.
3. Word TOC: three-level TOC was generated with cached page numbers (LibreOffice layout). In Word, right-click the
   TOC and choose Update Field to refresh page numbers. Navigation pane works from the built-in Heading 1 to 3 styles.
4. Placeholders (highlighted yellow): co-authors, funding, competing interests, ethics, reviewers, AI-use wording.
5. Stata run of the do-files and a diff against the Python tables.
