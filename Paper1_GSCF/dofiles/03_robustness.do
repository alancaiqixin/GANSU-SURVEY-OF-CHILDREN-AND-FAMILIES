*===============================================================================
* 03_robustness.do : Table 5 (alternative specifications), wild cluster bootstrap, IPW for attrition
*===============================================================================
version 16
use "$p1/data_clean/analysis_child_2000cohort_stata.dta", clear
gen byte needed = !missing(father_age, mother_age, ses)
local base "i.age00_c female0 sex_missing father_age mother_age i.sibs_cat firstborn any_brother ses i.county"

tempname R
postfile `R' str40 spec str12 outcome double(b se p n) using "$out/tables/stata_T5_robustness.dta", replace
foreach y in z_cogacad z_height04 {
    quietly regress `y' bw_c `base' if needed, vce(cluster vid)
    post `R' ("Baseline") ("`y'") (_b[bw_c]) (_se[bw_c]) (2*ttail(e(df_r),abs(_b[bw_c]/_se[bw_c]))) (e(N))
    quietly regress `y' bw_c i.age00_c female0 sex_missing father_age mother_age i.sibs_cat firstborn any_brother i.county if needed, vce(cluster vid)
    post `R' ("No household resource control") ("`y'") (_b[bw_c]) (_se[bw_c]) (2*ttail(e(df_r),abs(_b[bw_c]/_se[bw_c]))) (e(N))
    quietly regress `y' bw_c i.county if needed, vce(cluster vid)
    post `R' ("No demographic controls") ("`y'") (_b[bw_c]) (_se[bw_c]) (2*ttail(e(df_r),abs(_b[bw_c]/_se[bw_c]))) (e(N))
    quietly regress `y' bw_c i.age00_c female0 sex_missing father_age mother_age i.sibs_cat firstborn any_brother ses i.vid if needed, vce(cluster vid)
    post `R' ("Village fixed effects") ("`y'") (_b[bw_c]) (_se[bw_c]) (2*ttail(e(df_r),abs(_b[bw_c]/_se[bw_c]))) (e(N))
    quietly regress `y' bw_c `base' if needed, vce(cluster county)
    post `R' ("Cluster at county (G = 20)") ("`y'") (_b[bw_c]) (_se[bw_c]) (2*ttail(e(df_r),abs(_b[bw_c]/_se[bw_c]))) (e(N))
    quietly regress `y' bw_c `base' if needed & gest_unknown==0, vce(cluster vid)
    post `R' ("Exclude gestation unknown") ("`y'") (_b[bw_c]) (_se[bw_c]) (2*ttail(e(df_r),abs(_b[bw_c]/_se[bw_c]))) (e(N))
    quietly regress `y' bw_c `base' if needed & preterm==0, vce(cluster vid)
    post `R' ("Exclude preterm births") ("`y'") (_b[bw_c]) (_se[bw_c]) (2*ttail(e(df_r),abs(_b[bw_c]/_se[bw_c]))) (e(N))
    quietly regress `y' bw_c `base' if needed & inrange(bw_kg,2,4.5), vce(cluster vid)
    post `R' ("Birth weight 2.0 to 4.5 kg only") ("`y'") (_b[bw_c]) (_se[bw_c]) (2*ttail(e(df_r),abs(_b[bw_c]/_se[bw_c]))) (e(N))
    quietly regress `y' bw_c i.age00_c father_age mother_age i.sibs_cat firstborn any_brother ses i.county if needed & female==1, vce(cluster vid)
    post `R' ("Girls only") ("`y'") (_b[bw_c]) (_se[bw_c]) (2*ttail(e(df_r),abs(_b[bw_c]/_se[bw_c]))) (e(N))
    quietly regress `y' bw_c i.age00_c father_age mother_age i.sibs_cat firstborn any_brother ses i.county if needed & female==0, vce(cluster vid)
    post `R' ("Boys only") ("`y'") (_b[bw_c]) (_se[bw_c]) (2*ttail(e(df_r),abs(_b[bw_c]/_se[bw_c]))) (e(N))
    quietly regress `y' bw_c inst_birth `base' if needed, vce(cluster vid)
    post `R' ("Add delivery in clinic or hospital") ("`y'") (_b[bw_c]) (_se[bw_c]) (2*ttail(e(df_r),abs(_b[bw_c]/_se[bw_c]))) (e(N))
    quietly regress `y' bw_c health_vs_peers `base' if needed, vce(cluster vid)
    post `R' ("Add mother-rated health vs peers") ("`y'") (_b[bw_c]) (_se[bw_c]) (2*ttail(e(df_r),abs(_b[bw_c]/_se[bw_c]))) (e(N))
}
postclose `R'

* wild cluster bootstrap-t (Rademacher, null imposed), 1,999 replications
set seed 20260101
foreach y in z_cogacad z_height04 {
    quietly regress `y' bw_c `base' if needed, vce(cluster vid)
    boottest bw_c, cluster(vid) reps(1999) weight(rademacher) nograph seed(20260101)
    display "Wild cluster bootstrap (village), `y': p = " r(p)
    quietly regress `y' bw_c `base' if needed, vce(cluster county)
    boottest bw_c, cluster(county) reps(1999) weight(rademacher) nograph seed(20260101)
    display "Wild cluster bootstrap (county), `y': p = " r(p)
}

* inverse-probability weights for attrition (stabilised)
foreach pair in "z_chi04 obs04_test" "z_mat04 obs04_test" "z_lit04 obs04_test" "z_height04 obs04_health" "z_lit09 obs09" {
    local y : word 1 of `pair'
    local f : word 2 of `pair'
    quietly logit `f' bw_c preterm i.age00_c female0 sex_missing father_age mother_age i.sibs_cat firstborn any_brother ses vill_env_good oldage_high invest i.county ///
        if needed & !missing(lbw_est, preterm, vill_env_good, oldage_high, invest)
    predict double phat if e(sample), pr
    quietly summarize `f' if e(sample)
    gen double w = r(mean)/phat
    quietly regress `y' bw_c `base' if needed, vce(cluster vid)
    local bu = _b[bw_c]
    quietly regress `y' bw_c `base' [pweight=w] if needed, vce(cluster vid)
    display "IPW `y': unweighted b = " %6.3f `bu' "  weighted b = " %6.3f _b[bw_c] " (se " %5.3f _se[bw_c] ")"
    drop phat w
}
preserve
use "$out/tables/stata_T5_robustness.dta", clear
export delimited using "$out/tables/stata_T5_robustness.csv", replace
restore
