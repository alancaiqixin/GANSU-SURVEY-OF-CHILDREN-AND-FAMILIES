*===============================================================================
* 01_build_data.do : build analysis file (unit = target child, 2000 cohort, n = 2,000)
* Mirror of code_py/01_build_data.py. Negative GSCF codes (-1,-2,-3,-6) are missing.
*===============================================================================
version 16
tempfile moth ach0 cog0 sexf a4 l4 h4 l9 vil sibs tgt

*---------------- wave 2000 mother questionnaire ----------------
use "$root/moth2000ts.dta", clear
rename (a1 a2 a3) (county township village)
gen long vid = floor(hhid/100)
foreach v of varlist mh2 mh3 mh4 mh5 mh6 mb1 md1h md2 md3 me1 me2 me3 me8a me8b me8c mf1 mk1a mk1b mk1d mk1e mk14 mj11 mj12 mi3 mc6 {
    replace `v' = . if `v' < 0
}
* birth endowment
gen lbw       = (mh3==3) if !missing(mh3)
gen heavy_bw  = (mh3==1) if !missing(mh3)
gen bw_jin    = mh4 if inrange(mh4,2,12)
gen bw_kg     = bw_jin*0.5
gen lbw_est   = (bw_kg<2.5) if !missing(bw_kg)
gen preterm   = (mh2==2) if !missing(mh2)
gen postterm  = (mh2==3) if !missing(mh2)
gen gest_unknown = (mh2==4) if !missing(mh2)
gen adverse_birth = ((lbw==1)|(preterm==1)) if !missing(lbw) | !missing(preterm)
gen home_birth = (mh5==1) if !missing(mh5)
gen inst_birth = inlist(mh5,3,4) if !missing(mh5)
gen health_vs_peers = 6 - mh6
* old-age support expectations
gen oldage_exp  = 4 - md2
gen oldage_high = (oldage_exp==3) if !missing(oldage_exp)
gen son_support = (md3==1) if !missing(md3)
gen rely_sons_agree = (md1h==3) if !missing(md1h)
gen vill_env = mb1
gen vill_env_good = (mb1==3) if !missing(mb1)
* household resource index: mean of z-scored components, at least 5 of 7 observed
gen c1 = 4 - me1
gen c2 = 5 - me2
gen c3 = me3
gen c4 = (me8a==1) if !missing(me8a)
gen c5 = (me8b==1) if !missing(me8b)
gen c6 = (me8c==1) if !missing(me8c)
gen c7 = 4 - mf1
foreach c of varlist c1-c7 {
    quietly summarize `c'
    replace `c' = (`c' - r(mean))/r(sd)
}
egen nc = rownonmiss(c1-c7)
egen ses = rowmean(c1-c7)
replace ses = . if nc<5
quietly summarize ses
replace ses = (ses - r(mean))/r(sd)
* parental investment index, at least 3 of 4 items
foreach c in mk1a mk1b mk1d mk1e {
    quietly summarize `c'
    gen z_`c' = (`c' - r(mean))/r(sd)
}
egen ni = rownonmiss(z_mk1a z_mk1b z_mk1d z_mk1e)
egen invest = rowmean(z_mk1a z_mk1b z_mk1d z_mk1e)
replace invest = . if ni<3
quietly summarize invest
replace invest = (invest - r(mean))/r(sd)
gen books = mk14 if mk14<=90
gen lbooks = ln(1+books)
quietly summarize lbooks
gen books_z = (lbooks - r(mean))/r(sd)
gen edu_expect = mj11 if mj11<=4
gen edu_aspire = mj12 if mj12<=4
gen asp_college = (edu_aspire==4) if !missing(edu_aspire)
gen exp_college = (edu_expect==4) if !missing(edu_expect)
gen mother_rated_perf = 4 - mi3
gen father_home = (mc6==1) if !missing(mc6)
keep hhid county township village vid lbw heavy_bw bw_jin bw_kg lbw_est preterm postterm gest_unknown adverse_birth home_birth inst_birth ///
     health_vs_peers oldage_exp oldage_high son_support rely_sons_agree vill_env vill_env_good ses invest books_z edu_expect edu_aspire ///
     asp_college exp_college mother_rated_perf father_home md1h
rename md1h rely_sons
save `moth'

*---------------- linking file: ages and sibship ----------------
use "$root/GSCF_merge_pid.dta", clear
preserve
    keep if relat00!=1 & !missing(relat00) & from00==1
    gen first = floor(relat00/10)
    gen older_bro = (first==2)
    gen young_bro = (first==3)
    gen older_sis = (first==4)
    gen young_sis = (first==5)
    collapse (sum) older_bro young_bro older_sis young_sis, by(hhid)
    save `sibs'
restore
keep if pid00==1
duplicates drop hhid, force
keep hhid byear00 fbyear00 mbyear00 samekid0004 samekid0009 samekid0015
save `tgt'

*---------------- sex (2004 files) ----------------
use "$root/health2004t.dta", clear
keep hhid sex
save `h4', replace
use "$root/literacy2004t.dta", clear
duplicates tag hhid, gen(dup)
drop if dup>0
keep hhid sex total
rename total lit04_raw
save `l4'
use `h4', clear
append using `l4'
keep hhid sex
drop if missing(sex)
duplicates drop hhid, force
rename sex sex04
save `sexf'

*---------------- outcomes ----------------
use "$root/achieve2000t.dta", clear
gen math_form = !missing(shuxue)
egen z_ach00 = std(ceyan), by(math_form)
keep hhid math_form z_ach00
save `ach0'
use "$root/litracy2000t.dta", clear
egen z_cog00 = std(renzhi)
keep hhid z_cog00
save `cog0'

use "$root/achieve2004t.dta", clear
gen lev = schlevel
replace lev = -1 if missing(lev)
egen z_chi04 = std(yuwen) , by(lev)
egen z_mat04 = std(shuxue), by(lev)
replace z_chi04 = . if missing(schlevel)
replace z_mat04 = . if missing(schlevel)
keep hhid z_chi04 z_mat04
save `a4'

use `l4', clear
egen z_lit04 = std(lit04_raw)
keep hhid z_lit04
save `l4', replace

use "$root/health2004t.dta", clear
gen cell = string(sex) + "_" + string(byear)
replace height = . if !inrange(height,120,200)
replace bmiweightheight2 = . if !inrange(bmiweightheight2,10,40)
gen hb04 = hb if inrange(hb,70,200)
egen z_height04 = std(height), by(cell)
egen z_bmi04 = std(bmiweightheight2), by(cell)
egen z_hb04 = std(hb04), by(cell)
keep hhid z_height04 z_bmi04 z_hb04 hb04
save `h4', replace

use "$root/literacy2009t.dta", clear
duplicates tag hhid, gen(dup)
drop if dup>0
egen lit09_raw = rowtotal(one1-one5 two1-two3 three1-three6 four five1-five4), missing
egen z_lit09 = std(lit09_raw)
keep hhid z_lit09
save `l9'

*---------------- village context ----------------
use "$root/vill2000.dta", clear
gen long vid = a1*10000 + a2*100 + a3
foreach v of varlist vd1a vd1b vd1c vd1d vd1e {
    replace `v' = 0 if `v'<0
}
egen tot = rowtotal(vd1a vd1b vd1c vd1d vd1e)
replace tot = . if tot==0
gen tap_share = (vd1c+vd1d)/tot
gen unsafe_water_share = (vd1b+vd1e)/tot
gen dist_county_km = vb7 if vb7>=0
keep vid tap_share unsafe_water_share dist_county_km
save `vil'

*---------------- merge ----------------
use `moth', clear
merge 1:1 hhid using `tgt', nogen keep(master match)
merge 1:1 hhid using `sibs', nogen keep(master match)
foreach v of varlist older_bro young_bro older_sis young_sis {
    replace `v' = 0 if missing(`v')
}
merge 1:1 hhid using `sexf', nogen keep(master match)
merge 1:1 hhid using `ach0', nogen keep(master match)
merge 1:1 hhid using `cog0', nogen keep(master match)
merge 1:1 hhid using `a4', nogen keep(master match)
merge 1:1 hhid using `l4', nogen keep(master match)
merge 1:1 hhid using `h4', nogen keep(master match)
merge 1:1 hhid using `l9', nogen keep(master match)
merge m:1 vid using `vil', nogen keep(master match)

gen age00 = 2000 - byear00
gen age00_c = min(max(age00,9),13)
gen father_age = 2000 - fbyear00
gen mother_age = 2000 - mbyear00
gen n_sibs = older_bro+young_bro+older_sis+young_sis
gen any_brother = (older_bro+young_bro>0)
gen firstborn = (older_bro+older_sis==0)
gen sibs_cat = min(n_sibs,3)
gen female = (sex04==2) if !missing(sex04)
gen sex_missing = missing(female)
gen female0 = female
replace female0 = 0 if missing(female0)
gen bw_c = bw_kg - 3
quietly summarize ses, detail
gen ses_low = (ses < r(p50)) if !missing(ses)
quietly summarize unsafe_water_share, detail
gen unsafe_water_hi = (unsafe_water_share >= r(p50)) if !missing(unsafe_water_share)

* composite of cognitive and academic scores (at least 4 of 6 components)
egen n_cogacad = rownonmiss(z_cog00 z_ach00 z_chi04 z_mat04 z_lit04 z_lit09)
egen cmp = rowmean(z_cog00 z_ach00 z_chi04 z_mat04 z_lit04 z_lit09)
replace cmp = . if n_cogacad<4
egen z_cogacad = std(cmp)
drop cmp

* observation flags for attrition analysis
gen obs00 = !missing(z_cog00) | !missing(z_ach00)
gen obs04_test = !missing(z_chi04) | !missing(z_mat04) | !missing(z_lit04)
gen obs04_health = !missing(z_height04)
gen obs09 = !missing(z_lit09)

label var bw_c "Birth weight, kg, centred at 3.0"
compress
save "$p1/data_clean/analysis_child_2000cohort_stata.dta", replace
count
