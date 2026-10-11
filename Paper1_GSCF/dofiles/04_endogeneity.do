*===============================================================================
* 04_endogeneity.do : coefficient stability (Oster), E-values, negative controls, recall checks
* There is no credible instrument for birth weight in the GSCF files; sibling fixed effects
* are not possible because the sibling birth items were not collected in 2000.
*===============================================================================
version 16
use "$p1/data_clean/analysis_child_2000cohort_stata.dta", clear
gen byte needed = !missing(father_age, mother_age, ses)
local base "i.age00_c female0 sex_missing father_age mother_age i.sibs_cat firstborn any_brother ses i.county"

* Oster (2019): delta for beta = 0 and bias-adjusted beta at delta = 1, Rmax = min(1, 1.3 * R2 of the controlled model)
foreach y in z_cogacad z_cog00 z_ach00 z_lit04 z_height04 invest {
    local extra = cond("`y'"=="z_ach00","math_form","")
    quietly regress `y' bw_c `extra' i.county if needed & !missing(`y',bw_c)
    local r0 = e(r2)
    local b0 = _b[bw_c]
    quietly regress `y' bw_c `extra' `base' if needed & !missing(`y',bw_c)
    local rt = e(r2)
    local bt = _b[bw_c]
    local rmax = min(1, 1.3*`rt')
    display "`y': restricted b = " %6.3f `b0' " R2 = " %5.3f `r0' "; controlled b = " %6.3f `bt' " R2 = " %5.3f `rt' "; Rmax = " %5.3f `rmax'
    display "   delta for beta = 0: " %6.3f (`bt'*(`rt'-`r0'))/((`b0'-`bt')*(`rmax'-`rt'))
    display "   beta* at delta = 1: " %6.3f (`bt' - (`b0'-`bt')*(`rmax'-`rt')/(`rt'-`r0'))
}

* E-values for the standardized difference associated with birth weight below 2.5 kg
foreach y in z_cogacad z_height04 {
    quietly regress `y' lbw_est `base' if needed, vce(cluster vid)
    local d = abs(_b[lbw_est])
    local rr = exp(0.91*`d')
    display "`y': |d| = " %5.3f `d' ", RR approx = " %5.3f `rr' ", E-value = " %5.3f (`rr' + sqrt(`rr'*(`rr'-1)))
}

* negative-control outcomes (should be unrelated to birth weight)
foreach y in father_age mother_age vill_env unsafe_water_share tap_share father_home ses {
    local ctl "`base'"
    if inlist("`y'","father_age","mother_age","ses") local ctl "i.age00_c female0 sex_missing i.sibs_cat firstborn any_brother i.county"
    if inlist("`y'","unsafe_water_share","tap_share") local ctl "i.age00_c female0 sex_missing father_age mother_age i.sibs_cat firstborn any_brother ses"
    quietly regress `y' bw_c `ctl' if needed, vce(cluster vid)
    display "Negative control `y': b = " %6.3f _b[bw_c] " (se " %5.3f _se[bw_c] ")"
}

* reporting checks: heaping at 3.0 kg and exclusion of heaped values
quietly count if bw_kg==3 & !missing(bw_kg)
display "Share of birth weights reported as exactly 3.0 kg: " r(N)/1877
foreach y in z_height04 z_cogacad {
    quietly regress `y' bw_c `base' if needed & bw_kg!=3, vce(cluster vid)
    display "`y', excluding 3.0 kg reports: b = " %6.3f _b[bw_c]
}
