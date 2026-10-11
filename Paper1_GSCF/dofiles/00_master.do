*===============================================================================
* 00_master.do
* Paper 1: Birth endowments, parental investment and child development in rural Gansu
* Reproduces all estimates, tables and figures from the GSCF files.
* NOTE: written for Stata 16 (StataSE). Python mirrors of every step are in code_py/.
*       These do-files have NOT been executed in Stata inside the cloud session
*       (Stata is not installed there); run 00_master.do on the Mac and compare with
*       output/tables/*.csv produced by code_py/02_models.py.
*===============================================================================
version 16
clear all
set more off
set linesize 120

* ---- EDIT THIS LINE: folder that holds the GSCF .dta files (repository root) ----
global root "/Volumes/My Passport/Source_初始数据库/GANSU-SURVEY-OF-CHILDREN-AND-FAMILIES"
global p1   "$root/Paper1_GSCF"
global out  "$p1/output"
capture mkdir "$p1/data_clean"
capture mkdir "$out"
capture mkdir "$out/tables"
capture mkdir "$out/figures"
capture mkdir "$out/logs"

* ---- user-written packages (install once) ----
foreach pkg in boottest {
    capture which `pkg'
    if _rc ssc install `pkg', replace
}

* ---- common model specification ----
global ctrl "i.age00_c female0 sex_missing father_age mother_age i.sibs_cat firstborn any_brother ses i.county"

log using "$out/logs/master.log", replace text
do "$p1/dofiles/01_build_data.do"
do "$p1/dofiles/02_main_models.do"
do "$p1/dofiles/03_robustness.do"
do "$p1/dofiles/04_endogeneity.do"
do "$p1/dofiles/05_figures.do"
log close
