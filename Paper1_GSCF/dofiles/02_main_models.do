*===============================================================================
* 02_main_models.do : Tables 1 to 4 (descriptives, main, mechanisms, heterogeneity)
* Village-clustered standard errors; county fixed effects.
*===============================================================================
version 16
use "$p1/data_clean/analysis_child_2000cohort_stata.dta", clear
gen byte needed = !missing(father_age, mother_age, ses)

*---------------- Table 2: birth endowments and child development ----------------
tempname M
postfile `M' str12 exposure str12 outcome double(b se p n) using "$out/tables/stata_T2_main.dta", replace
foreach x in bw_c lbw_est lbw preterm {
    foreach y in z_cogacad z_cog00 z_ach00 z_chi04 z_mat04 z_lit04 z_lit09 z_height04 {
        local extra = cond("`y'"=="z_ach00","math_form","")
        quietly regress `y' `x' $ctrl `extra' if needed, vce(cluster vid)
        post `M' ("`x'") ("`y'") (_b[`x']) (_se[`x']) (2*ttail(e(df_r), abs(_b[`x']/_se[`x']))) (e(N))
    }
}
postclose `M'

*---------------- Table 3: parental investment ----------------
tempname P
postfile `P' str16 exposure str18 outcome double(b se p n) using "$out/tables/stata_T3_mechanisms.dta", replace
foreach x in bw_c lbw_est lbw preterm health_vs_peers {
    foreach y in invest books_z edu_aspire asp_college exp_college mother_rated_perf {
        quietly regress `y' `x' $ctrl if needed, vce(cluster vid)
        post `P' ("`x'") ("`y'") (_b[`x']) (_se[`x']) (2*ttail(e(df_r), abs(_b[`x']/_se[`x']))) (e(N))
    }
}
postclose `P'

*---------------- Table 4: heterogeneity (interaction with birth weight) ----------------
tempname H
postfile `H' str18 moderator str12 outcome double(b_int se_int p_int b0 b1 n) using "$out/tables/stata_T4_heterogeneity.dta", replace
foreach mv in oldage_high rely_sons_agree ses_low female vill_env_good unsafe_water_hi any_brother {
    foreach y in z_cogacad z_height04 invest edu_aspire {
        local ctl "$ctrl"
        if "`mv'"=="female" local ctl "i.age00_c father_age mother_age i.sibs_cat firstborn any_brother ses i.county"
        quietly regress `y' c.bw_c##i.`mv' `ctl' if needed & !missing(`mv'), vce(cluster vid)
        local bi = _b[1.`mv'#c.bw_c]
        local si = _se[1.`mv'#c.bw_c]
        local pi = 2*ttail(e(df_r), abs(`bi'/`si'))
        local nn = e(N)
        quietly regress `y' bw_c `ctl' if needed & `mv'==0, vce(cluster vid)
        local b0 = _b[bw_c]
        quietly regress `y' bw_c `ctl' if needed & `mv'==1, vce(cluster vid)
        local b1 = _b[bw_c]
        post `H' ("`mv'") ("`y'") (`bi') (`si') (`pi') (`b0') (`b1') (`nn')
    }
}
postclose `H'

*---------------- Benjamini-Hochberg q-values (within exposure, Table 2) ----------------
use "$out/tables/stata_T2_main.dta", clear
sort exposure p
by exposure: gen rk = _n
by exposure: gen m = _N
gen qraw = p*m/rk
gsort exposure -rk
by exposure: gen q = qraw if _n==1
by exposure: replace q = min(qraw, q[_n-1]) if _n>1
drop rk m qraw
save "$out/tables/stata_T2_main.dta", replace
export delimited using "$out/tables/stata_T2_main.csv", replace
