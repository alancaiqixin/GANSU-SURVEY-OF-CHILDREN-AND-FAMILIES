*===============================================================================
* 05_figures.do : Figures 2 and 3 in Stata (clean scheme, Arial, exported as SVG, PDF and PNG)
* The full set of figures is produced by code_py/03_figures.py; these Stata versions are provided
* for the two figures most often requested by reviewers.
*===============================================================================
version 16
set scheme s1mono
graph set window fontface "Arial"
graph set svg fontface "Arial"

use "$out/tables/stata_T2_main.dta", clear
keep if exposure=="bw_c"
gen lo = b - 1.96*se
gen hi = b + 1.96*se
gen ypos = _n
label define yl 1 "Cognitive and academic composite" 2 "Cognitive test, 2000" 3 "Achievement test, 2000" 4 "Chinese test, 2004" ///
                5 "Mathematics test, 2004" 6 "Literacy test, 2004" 7 "Literacy test, 2009" 8 "Height (z), 2004"
label values ypos yl
twoway (rcap lo hi ypos, horizontal lcolor("0 114 178") lwidth(medthick)) ///
       (scatter ypos b, mcolor("0 114 178") msymbol(O) msize(medium)), ///
       xline(0, lcolor(black) lwidth(thin)) ylabel(1(1)8, valuelabel angle(0) labsize(small) nogrid) ///
       yscale(reverse) xtitle("Difference in standardized outcome per 1 kg of birth weight (SD)", size(small)) ///
       ytitle("") legend(off) graphregion(color(white)) plotregion(color(white) lstyle(none)) xlabel(, nogrid) ///
       name(fig2, replace) xsize(7) ysize(3.6)
graph export "$out/figures/Stata_Figure2_main_estimates.svg", replace
graph export "$out/figures/Stata_Figure2_main_estimates.pdf", replace
graph export "$out/figures/Stata_Figure2_main_estimates.png", replace width(4200)
