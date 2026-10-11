"""04_build_word.py: build all Word deliverables in Paper1_GSCF/manuscript/ from output/results.pkl and output/figures."""
import os, re, pickle, datetime
import numpy as np, pandas as pd
from lib import P1, FIG, OUTCOMES
import manuscript_text as mt
from refs import REFS
from wordlib import *

MS = os.path.join(P1, 'manuscript'); os.makedirs(MS, exist_ok=True)
R = mt.R
STAR = lambda p: '***' if p < 0.01 else ('**' if p < 0.05 else ('*' if p < 0.10 else ''))
c3 = lambda b, p: f'{b:.3f}{STAR(p)}'
s3 = lambda se: f'({se:.3f})'
OUTL = dict(OUTCOMES)
OUTL.update({'invest': 'Parental investment index', 'books_z': 'Books owned (log, z)', 'edu_aspire': 'Educational aspiration (1 to 4)',
             'asp_college': 'Aspires to college', 'exp_college': 'Expects college', 'mother_rated_perf': 'Mother-rated school performance',
             'z_hb04': 'Hemoglobin (z), 2004', 'z_bmi04': 'Body mass index (z), 2004'})
EXPL = {'bw_c': 'Birth weight, per 1 kg', 'lbw_est': 'Estimated weight below 2.5 kg', 'lbw': 'Maternal category "light"', 'preterm': 'Preterm birth',
        'health_vs_peers': 'Health vs village peers (1 to 5)'}
MODL = {'oldage_high': 'Expects a lot of old-age financial help', 'rely_sons_agree': 'Agrees parents should rely on sons', 'ses_low': 'Below-median household resources',
        'female': 'Female', 'vill_env_good': 'Village environment rated good', 'unsafe_water_hi': 'Village unsafe-water share above median', 'any_brother': 'Has a brother'}
SAMPLE_NOTE = ('All models are OLS with county fixed effects and controls for age in single years, sex (with a missing indicator), parents\' ages, sibship size, first-born status, '
               'presence of a brother, and the household resource index; standard errors are clustered at the village level (100 clusters). Outcomes are standardized. ')
STARS_NOTE = '* p < 0.10, ** p < 0.05, *** p < 0.01.'

# ================================================================== table builders
def tab1():
    T1 = R['T1']; rows = []
    for _, r in T1.iterrows():
        dec = 2 if r.Variable.startswith(('Estimated birth weight (kg)', 'Age', "Father", "Mother's age", 'Number', 'Household', 'Parental', 'Educational', 'Cognitive', 'Height')) else 3
        rows.append([r.Variable, f'{int(r.N):,}'] + [(f'{v:.{dec}f}'.replace('-0.00', '0.00')) for v in (r.Mean, r.SD, r.Mean_normal, r.Mean_adverse)])
    return ('Table 1. Descriptive statistics, GSCF target children (2000 cohort)', ['Variable', 'N', 'Mean', 'SD', 'Mean, no adverse birth', 'Mean, adverse birth'], rows, [2.9, 0.5, 0.6, 0.6, 0.95, 0.95],
            'Notes. Adverse birth is a maternal report of a "light" birth weight or a preterm birth. Binary variables are shown as proportions. Birth weight is the maternal estimate converted from jin. Sex is recorded in the 2004 files. '
            'Village unsafe-water share is the share of households drawing drinking water from unpumped wells, rivers, lakes, or ponds (2000 village survey). Source: Gansu Survey of Children and Families.')

def tab2():
    M = R['T2']; rows = []
    for y, yl in OUTCOMES:
        b = M[(M.exposure == 'bw_c') & (M.outcome == y)].iloc[0]
        row1 = [yl, f'{b.n:,}', c3(b.b, b.p), f'{b.q:.3f}']; row2 = ['', '', s3(b.se), '']
        for x in ('lbw_est', 'lbw', 'preterm'):
            r = M[(M.exposure == x) & (M.outcome == y)].iloc[0]; row1.append(c3(r.b, r.p)); row2.append(s3(r.se))
        rows += [row1, row2]
    return ('Table 2. Birth endowments and child development', ['Outcome', 'N', 'Birth weight,\nper 1 kg', 'q', 'Estimated weight\nbelow 2.5 kg', 'Maternal\n"light"', 'Preterm'], rows, [1.95, 0.5, 0.95, 0.5, 1.0, 0.8, 0.8],
            'Notes. Each cell is a coefficient from a separate regression, with the village-clustered standard error in parentheses. ' + SAMPLE_NOTE +
            'N refers to the birth weight model. q is the Benjamini-Hochberg false discovery rate q-value across the eight outcomes for the birth weight coefficient. ' + STARS_NOTE)

def tab3():
    T = R['T3']; rows = []
    for y in ['invest', 'books_z', 'edu_aspire', 'asp_college', 'exp_college', 'mother_rated_perf']:
        r1, r2 = [OUTL[y]], ['']
        for x in ('bw_c', 'lbw_est', 'preterm', 'health_vs_peers'):
            r = T[(T.exposure == x) & (T.outcome == y)].iloc[0]; r1.append(c3(r.b, r.p)); r2.append(s3(r.se))
        rows += [r1, r2]
    return ('Table 3. Birth endowments and parental investment in learning', ['Outcome', 'Birth weight,\nper 1 kg', 'Estimated weight\nbelow 2.5 kg', 'Preterm', 'Health vs village\npeers (1 to 5)'], rows, [2.0, 1.1, 1.2, 0.9, 1.3],
            'Notes. Each cell is a coefficient from a separate regression, with the village-clustered standard error in parentheses. Investment index, books owned (log), and the investment items are standardized; aspiration is on a four-point scale (primary to college). '
            'Health relative to village peers is the mother\'s current rating, not a birth measure. ' + SAMPLE_NOTE + STARS_NOTE)

def tab4():
    T = R['T4']; rows = []
    for mv, ml in MODL.items():
        r1, r2 = [ml], ['']
        for y in ['z_cogacad', 'z_height04', 'invest', 'edu_aspire']:
            r = T[(T.moderator == mv) & (T.outcome == y)].iloc[0]; r1.append(c3(r.b_int, r.p_int)); r2.append(s3(r.se_int))
        rows += [r1, r2]
    return ('Table 4. Heterogeneity: interactions between birth weight and moderators', ['Moderator', 'Cognitive and\nacademic composite', 'Height (z),\n2004', 'Parental investment\nindex', 'Educational\naspiration'], rows, [2.3, 1.1, 0.95, 1.15, 1.0],
            'Notes. Each cell is the coefficient on the interaction between birth weight (per 1 kg) and the moderator, from a separate regression that includes both main terms, with the village-clustered standard error in parentheses. ' + SAMPLE_NOTE +
            'The 28 tests are exploratory. Benjamini-Hochberg q-values across all 28 interactions exceed 0.05; the smallest are 0.060 (reliance on sons with height, and low household resources with investment). ' + STARS_NOTE)

def tab5():
    T = R['T5']; specs = list(dict.fromkeys(T.spec)); rows = []
    for s in specs:
        a = T[(T.spec == s) & (T.outcome == 'z_cogacad')].iloc[0]; b = T[(T.spec == s) & (T.outcome == 'z_height04')].iloc[0]
        rows.append([s, f'{c3(a.b, a.p)}\n{s3(a.se)}', f'{a.n:,}', f'{c3(b.b, b.p)}\n{s3(b.se)}', f'{b.n:,}'])
    wb = T[(T.spec == 'Baseline')].set_index('outcome')
    return ('Table 5. Robustness of the birth weight coefficient (per 1 kg)', [['', 'Cognitive and academic composite', '', 'Height (z), 2004', ''], ['Specification', 'Coefficient (SE)', 'N', 'Coefficient (SE)', 'N']], rows, [2.7, 1.3, 0.6, 1.3, 0.6],
            'Notes. Each row is a separate regression of the standardized outcome on birth weight (per 1 kg) with the controls in the baseline unless altered. Standard errors are clustered at the village level except where stated. '
            f'Wild cluster bootstrap-t p-values (1,999 Rademacher draws, null imposed) for the baseline model: composite {wb.loc["z_cogacad","p_wild_village"]:.3f}, height {wb.loc["z_height04","p_wild_village"]:.3f} (village clusters); '
            f'with 20 county clusters, composite {T[(T.spec=="Cluster at county (G = 20)")&(T.outcome=="z_cogacad")].p_wild_county.iloc[0]:.3f}, height {T[(T.spec=="Cluster at county (G = 20)")&(T.outcome=="z_height04")].p_wild_county.iloc[0]:.3f}. ' + STARS_NOTE)

def tab6():
    O = R['T6_oster']; E = R['T6_evalue']; N = R['T6_nco']
    A = [[OUTL[r.outcome] if r.outcome in OUTL else r.outcome, f'{r.b_restricted:.3f}', f'{r.b_full:.3f}', f'{r.r2_restricted:.3f}', f'{r.r2_full:.3f}', f'{r.rmax:.3f}', f'{r.delta_for_zero:.2f}', f'{r.beta_star_delta1:.3f}'] for r in O.itertuples()]
    Bt = [[OUTL[r.outcome], f'{r.b:.3f}', f'{r.se:.3f}', f'{r.rr_approx:.2f}', f'{r.e_value_point:.2f}', f'{r.e_value_ci:.2f}'] for r in E.reset_index().itertuples()]
    C = [[r.Index, f'{r.b:.3f}', f'{r.se:.3f}', f'{r.p:.3f}', f'{int(r.n):,}'] for r in N.itertuples()]
    return A, Bt, C

# ================================================================== manuscript
def make_manuscript(pages=None):
    doc = new_doc(line_numbers=True)
    B = mt.build()
    p = doc.add_paragraph(style='Title'); p.add_run(mt.TITLE)
    para(doc, 'Anonymous manuscript for peer review', spacing=1.0, align='center', italic=True, space_after=12)
    anchor = para(doc, '', spacing=1.0)
    cited = set()
    for kind, text in B:
        if kind == 'title': continue
        if kind in ('h1', 'h2', 'h3'):
            heading(doc, text, int(kind[1]))
            if text == 'References':
                para(doc, '[Drafting note, delete before submission: the reference entries were compiled without access to CrossRef, Consensus, or Scholar Gateway and have not been verified. Run code_py/verify_refs.py and check each entry, and check that each source supports the sentence that cites it.]', spacing=1.0, highlight=True, size=10, space_after=6)
                references(doc, sorted(cited))
        elif kind == 'p':
            cited.update(k for m in re.findall(r'\[\[[cn]:([^\]]+)\]\]', text) for k in m.split(';'))
            para(doc, cite_text(text), first_indent=0.5, align=None)
        elif kind == 'note':
            para(doc, text, align='center', italic=True, spacing=1.5)
    insert_toc_at(doc, anchor, pages)
    return doc

def body_words(B):
    n = 0; on = False
    for kind, text in B:
        if kind == 'h1' and text.startswith('1.'): on = True
        if kind == 'h1' and text in ('Data and code availability', 'References'): on = False
        if on and kind in ('p',): n += len(re.sub(r'\[\[[^\]]+\]\]', '', text).split())
    return n

def build_manuscript():
    path = os.path.join(MS, 'Manuscript_Anonymous.docx')
    d1 = make_manuscript(); d1.save(path)
    pages = compute_pages(path, d1._heads, 'Keywords:')
    d2 = make_manuscript(pages); d2.save(path)
    return d2._heads, pages

# ================================================================== tables document
def build_tables():
    def make(pages=None):
        doc = new_doc(body_size=10, margins=1.0)
        p = doc.add_paragraph(style='Title'); p.add_run('Tables')
        para(doc, 'Birth Weight, Parental Investment, and Child Development in Rural China (anonymous)', spacing=1.0, align='center', italic=True, space_after=10)
        anchor = para(doc, '', spacing=1.0)
        para(doc, 'Tables follow the order of citation in the manuscript.', spacing=1.0, space_after=8)
        for fn in (tab1, tab2, tab3, tab4, tab5):
            title, header, rows, widths, note = fn()
            heading(doc, title, 1)
            table(doc, header, rows, widths, font=9, note=note, merges=([(0, 1, 2), (0, 3, 4)] if fn is tab5 else []))
            doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        heading(doc, 'Table 6. Identification checks: coefficient stability, E-values, and negative control outcomes', 1)
        A, Bt, C = tab6()
        heading(doc, 'Panel A. Coefficient stability (Oster bounds), birth weight per 1 kg', 2)
        table(doc, ['Outcome', 'b, county FE only', 'b, full controls', 'R2, restricted', 'R2, full', 'Rmax', 'Delta for b = 0', 'b* at delta = 1'], A, [1.7, 0.65, 0.65, 0.6, 0.6, 0.55, 0.9, 0.85], font=8.5,
              note='Notes. Restricted model: county fixed effects only; full model: baseline controls. Rmax = min(1, 1.3 times the R2 of the full model). Delta is the proportional strength of selection on unobservables relative to observables needed to set the coefficient to zero; '
                   'b* is the bias-adjusted coefficient at delta = 1. A negative delta means that adding controls raised the coefficient.')
        heading(doc, 'Panel B. E-values for estimated birth weight below 2.5 kg', 2)
        table(doc, ['Outcome', 'Difference (SD)', 'SE', 'Approx. risk ratio', 'E-value, estimate', 'E-value, CI limit'], Bt, [2.2, 0.8, 0.8, 0.9, 0.9, 0.9], font=8.5,
              note='Notes. Standardized mean differences converted to an approximate risk ratio by exp(0.91 d), then to E-values (VanderWeele and Ding, 2017). An E-value for the confidence limit of 1.00 means that the interval includes no effect.')
        heading(doc, 'Panel C. Negative control outcomes regressed on birth weight (per 1 kg)', 2)
        table(doc, ['Outcome', 'Coefficient', 'SE', 'p', 'N'], C, [2.7, 0.9, 0.9, 1.0, 1.0], font=8.5,
              note='Notes. Birth weight should not cause these variables. Models include the baseline controls except where the outcome is itself a control (parents\' ages, resource index) and omit county fixed effects for the two village water variables. Standard errors are clustered at the village level.')
        insert_toc_at(doc, anchor, pages)
        return doc
    path = os.path.join(MS, 'Tables.docx'); d1 = make(); d1.save(path)
    pages = compute_pages(path, d1._heads, 'Tables follow the order'); d2 = make(pages); d2.save(path)

# ================================================================== figures document
FIGS = [('Figure1_birth_weight_distribution', 'Figure 1. Distribution of maternal-reported birth weight and county variation in low birth weight',
         'Notes. Panel A: histogram of the maternal estimate of birth weight (converted from jin); the dashed line marks 2.5 kg and heaping at 3.0 kg is visible. Panel B: share of children with an estimated weight below 2.5 kg by county (points) with 95% Wilson confidence intervals; the dashed line is the sample share. County codes are the GSCF numeric codes.'),
        ('Figure2_main_estimates', 'Figure 2. Birth endowments and child development',
         'Notes. Coefficients and 95% confidence intervals from separate OLS regressions of standardized outcomes on birth weight per 1 kg (Panel A) and on an indicator for estimated weight below 2.5 kg (Panel B), with county fixed effects and baseline controls; standard errors clustered at the village level.'),
        ('Figure3_binned_residual_plots', 'Figure 3. Partial residual plots of the birth weight gradient',
         'Notes. Residuals of the outcome and of birth weight after partialling out the baseline controls and county fixed effects. Points are means within twelve equal-sized bins of residual birth weight with 95% confidence intervals; the line and band are the linear fit with village-clustered 95% confidence interval.'),
        ('Figure4_parental_investment', 'Figure 4. Birth endowments and parental investment in learning',
         'Notes. Coefficients and 95% confidence intervals from separate OLS regressions with county fixed effects and baseline controls. Investment index and books owned are standardized; aspiration and expectation items are on their original scales.'),
        ('Figure5_heterogeneity', 'Figure 5. Birth weight gradients by old-age support expectations and other moderators',
         'Notes. Birth weight slopes (per 1 kg) with 95% confidence intervals estimated separately for children in households with the moderator equal to 0 (grey circles) and 1 (blue squares). Interaction tests are in Table 4 and are exploratory.'),
        ('Figure6_robustness', 'Figure 6. Robustness of the birth weight coefficient across specifications',
         'Notes. Coefficients and 95% confidence intervals for birth weight per 1 kg under the specifications listed in Table 5. The dotted line marks the baseline estimate.')]
def build_figures():
    def make(pages=None):
        doc = new_doc(body_size=10)
        p = doc.add_paragraph(style='Title'); p.add_run('Figures')
        para(doc, 'Birth Weight, Parental Investment, and Child Development in Rural China (anonymous)', spacing=1.0, align='center', italic=True, space_after=10)
        anchor = para(doc, '', spacing=1.0)
        para(doc, 'Figures follow the order of citation in the manuscript. Vector versions (SVG, PDF) and 600 dpi PNG files are in the figures folder.', spacing=1.0)
        for f, ttl, note in FIGS:
            heading(doc, ttl, 1)
            figure(doc, os.path.join(FIG, f + '.png'), width=6.5)
            para(doc, note, spacing=1.0, size=9)
            doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        insert_toc_at(doc, anchor, pages)
        return doc
    path = os.path.join(MS, 'Figures.docx'); d1 = make(); d1.save(path)
    pages = compute_pages(path, d1._heads, 'Figures follow the order'); d2 = make(pages); d2.save(path)

# ================================================================== supplementary appendix
VARDEF = [
 ('Birth weight (continuous)', 'moth2000ts: mh4', 'Mother\'s estimate of birth weight in jin, valid range 2 to 12, multiplied by 0.5 (kg) and centered at 3.0 kg.'),
 ('Estimated weight below 2.5 kg', 'moth2000ts: mh4', 'Indicator, estimated weight below 2.5 kg.'),
 ('Maternal "light" category', 'moth2000ts: mh3', 'Indicator, mother rated birth weight as light (1 heavy, 2 average, 3 light).'),
 ('Preterm birth', 'moth2000ts: mh2', 'Indicator, mother reported preterm birth (1 term, 2 preterm, 3 post-term, 4 unknown); unknown is retained in the comparison group.'),
 ('Delivery place', 'moth2000ts: mh5', 'Clinic or hospital (village clinic, township or higher hospital) versus home or other.'),
 ('Health vs village peers', 'moth2000ts: mh6', 'Mother\'s rating of current child health compared with village children, reversed so that 5 is much better.'),
 ('Old-age support expectation', 'moth2000ts: md2', 'Indicator, mother expects "a lot" of financial help from children in the future (reversed three-point scale).'),
 ('Reliance on sons', 'moth2000ts: md1h', 'Indicator, agrees that parents should rely on sons for care in old age.'),
 ('Village environment rating', 'moth2000ts: mb1', 'Mother\'s rating of the village environment for child growth; indicator for "good".'),
 ('Unsafe-water share', 'vill2000: vd1a to vd1e', 'Share of village households drinking from unpumped wells, rivers, lakes, or ponds; indicator for above the village median.'),
 ('Household resource index', 'moth2000ts: me1, me2, me3, me8a to me8c, mf1', 'Mean of seven standardized items (satisfaction with economic situation, relative standing, income sufficiency, desk, dictionary, reading materials, food sufficiency); at least five required; re-standardized.'),
 ('Parental investment index', 'moth2000ts: mk1a, mk1b, mk1d, mk1e', 'Mean of four standardized items (reading story books, helping with homework, playing, taking the child to a bookstore or shop); at least three required; re-standardized.'),
 ('Books owned', 'moth2000ts: mk14', 'Number of books owned by the child (values above 90 excluded), log(1 + books), standardized.'),
 ('Educational aspiration / expectation', 'moth2000ts: mj12, mj11', 'Highest level the mother hopes (expects) the child will reach, 1 primary to 4 college; indicators for college.'),
 ('Child age', 'GSCF_merge_pid: byear00', 'Age in 2000 = 2000 minus birth year; truncated to 9 to 13 and entered as single-year dummies.'),
 ('Child sex', 'health2004t, literacy2004t: sex', 'Female indicator; missing for children not observed in the 2004 files (indicator included).'),
 ('Parents\' ages', 'GSCF_merge_pid: fbyear00, mbyear00', 'Age in 2000.'),
 ('Sibship', 'GSCF_merge_pid: relat00', 'Counts by relationship code (first digit 2 older brother, 3 younger brother, 4 older sister, 5 younger sister, inferred from the pattern of birth years); sibship size truncated at 3, first-born, any brother.'),
 ('Cognitive test, 2000', 'litracy2000t: renzhi', 'Standardized score.'),
 ('Achievement test, 2000', 'achieve2000t: ceyan, a4', 'Chinese or mathematics test (assigned by the parity of the household code), standardized within form.'),
 ('Chinese and mathematics, 2004', 'achieve2004t: yuwen, shuxue, schlevel', 'Standardized within school-level test form.'),
 ('Literacy test, 2004', 'literacy2004t: total', 'Total score, standardized; nine repeated household identifiers dropped.'),
 ('Literacy test, 2009', 'literacy2009t: items', 'Sum of item scores, standardized; one repeated household identifier dropped.'),
 ('Height, 2004', 'health2004t: height, sex, byear', 'Measured height (120 to 200 cm) standardized within sex by birth-year cells.'),
 ('Cognitive and academic composite', 'constructed', 'Mean of the six standardized test scores, at least four required, re-standardized.'),
]
def build_appendix():
    def make(pages=None):
        doc = new_doc(body_size=10)
        p = doc.add_paragraph(style='Title'); p.add_run('Supplementary Appendix')
        para(doc, 'Birth Weight, Parental Investment, and Child Development in Rural China (anonymous)', spacing=1.0, align='center', italic=True, space_after=10)
        anchor = para(doc, '', spacing=1.0)
        para(doc, 'This appendix contains supplementary tables and figures referred to in the manuscript.', spacing=1.0, space_after=8)
        heading(doc, 'Part 1. Supplementary tables', 1)
        heading(doc, 'Table A1. Variable definitions', 2)
        table(doc, ['Construct', 'GSCF file: variables', 'Definition'], [[a, b, c] for a, b, c in VARDEF], [1.6, 1.7, 3.2], font=8.5, left_cols=(0, 1, 2), note='Notes. Negative GSCF codes (-1, -2, -3, -6) are set to missing. GSCF = Gansu Survey of Children and Families.')
        heading(doc, 'Table A2. Full main estimates with confidence intervals and q-values', 2)
        M = R['T2']; rows = []
        for r in M.itertuples():
            rows.append([EXPL[r.exposure], OUTL[r.outcome], c3(r.b, r.p), f'{r.se:.3f}', f'{r.lo:.3f} to {r.hi:.3f}', f'{r.p:.3f}', f'{r.q:.3f}', f'{r.n:,}'])
        table(doc, ['Exposure', 'Outcome', 'b', 'SE', '95% CI', 'p', 'q', 'N'], rows, [1.3, 1.55, 0.6, 0.5, 1.1, 0.45, 0.45, 0.55], font=8, note='Notes. q is the Benjamini-Hochberg q-value within exposure across eight outcomes. ' + SAMPLE_NOTE + STARS_NOTE)
        heading(doc, 'Table A3. Parental investment estimates with q-values', 2)
        T3 = R['T3']; rows = [[EXPL[r.exposure], OUTL[r.outcome], c3(r.b, r.p), f'{r.se:.3f}', f'{r.p:.3f}', f'{r.q:.3f}', f'{r.n:,}'] for r in T3.itertuples()]
        table(doc, ['Predictor', 'Outcome', 'b', 'SE', 'p', 'q', 'N'], rows, [1.5, 1.9, 0.65, 0.5, 0.5, 0.5, 0.6], font=8, note='Notes. q is the Benjamini-Hochberg q-value within predictor across six outcomes. ' + SAMPLE_NOTE + STARS_NOTE)
        heading(doc, 'Table A4. Heterogeneity: subgroup slopes and interaction tests', 2)
        T4 = R['T4']; rows = [[MODL[r.moderator], OUTL[r.outcome], f'{r.b0:.3f} ({r.se0:.3f})', f'{r.b1:.3f} ({r.se1:.3f})', c3(r.b_int, r.p_int), f'{r.p_int:.3f}', f'{r.q_all:.3f}', f'{int(r.n):,}'] for r in T4.itertuples()]
        table(doc, ['Moderator', 'Outcome', 'Slope, moderator = 0', 'Slope, moderator = 1', 'Interaction', 'p', 'q', 'N'], rows, [1.55, 1.25, 0.8, 0.8, 0.6, 0.4, 0.4, 0.5], font=7.5, note='Notes. Slopes are birth weight per 1 kg estimated separately by group with baseline controls; q is the Benjamini-Hochberg q-value across the 28 interaction tests. ' + STARS_NOTE)
        heading(doc, 'Table A5. Attrition and inverse probability weights', 2)
        heading(doc, 'Panel A. Predictors of being observed in later waves (logit coefficients)', 3)
        att = R['A_attrition']; rows = [[r.sample, f'{r.rate:.3f}', f'{r.b_bw:.3f}', f'{r.p_bw:.3f}', f'{r.b_ses:.3f}', f'{r.p_ses:.3f}', f'{r.b_pre:.3f}', f'{r.p_pre:.3f}'] for r in att.itertuples()]
        table(doc, ['Sample', 'Share observed', 'Birth weight', 'p', 'Resource index', 'p', 'Preterm', 'p'], rows, [2.0, 0.7, 0.7, 0.5, 0.8, 0.5, 0.7, 0.5], font=8.5, note='Notes. Logit models include county fixed effects and the baseline controls, village-clustered standard errors.')
        heading(doc, 'Panel B. Birth weight coefficient with and without inverse probability weights', 3)
        ipw = R['T5_ipw']; rows = [[OUTL[r.outcome], f'{r.b_unw:.3f} ({r.se_unw:.3f})', f'{r.b_ipw:.3f} ({r.se_ipw:.3f})', f'{r.p_ipw:.3f}', f'{r.n_ipw:,}'] for r in ipw.itertuples()]
        table(doc, ['Outcome', 'Unweighted (SE)', 'Weighted (SE)', 'p, weighted', 'N, weighted'], rows, [2.2, 1.3, 1.3, 0.9, 0.8], font=8.5, note='Notes. Stabilized weights are the inverse of the predicted probability of observing the outcome, from a logit on baseline covariates, birth weight, preterm birth, old-age expectation, village environment rating, and investment.')
        heading(doc, 'Table A6. Additional health outcomes (2004)', 2)
        ah = R['A_extra_health']; rows = [[EXPL[r.exposure], OUTL[r.outcome], c3(r.b, r.p), f'{r.se:.3f}', f'{r.p:.3f}', f'{r.n:,}'] for r in ah.itertuples()]
        table(doc, ['Exposure', 'Outcome', 'b', 'SE', 'p', 'N'], rows, [1.9, 2.0, 0.7, 0.6, 0.6, 0.7], font=8.5, note='Notes. ' + SAMPLE_NOTE + STARS_NOTE)
        heading(doc, 'Table A7. Nonlinearity: birth weight bins (reference 2.5 to 3.0 kg)', 2)
        bn = R['A_bins']; rows = [[OUTL[r.outcome], r.bin, f'{r.b:.3f}', f'{r.se:.3f}', f'{r.p:.3f}', f'{r.n:,}'] for r in bn.itertuples()]
        table(doc, ['Outcome', 'Birth weight (kg)', 'b', 'SE', 'p', 'N'], rows, [2.2, 1.2, 0.8, 0.7, 0.7, 0.9], font=8.5, note='Notes. ' + SAMPLE_NOTE)
        heading(doc, 'Table A8. Item nonresponse for birth weight', 2)
        bm = R['A_bwmissing']
        names = {'ses': 'Household resource index', 'father_age': "Father's age", 'mother_age': "Mother's age", 'any_brother': 'Has a brother', 'firstborn': 'First-born', 'female0': 'Female', 'oldage_high': 'Old-age support expectation high'}
        rows = [[names[i], f'{r.b:.3f}', f'{r.se:.3f}', f'{r.p:.3f}'] for i, r in bm.iterrows()]
        table(doc, ['Predictor', 'Logit coefficient', 'SE', 'p'], rows, [2.8, 1.3, 1.0, 1.0], font=8.5, note=f'Notes. Outcome is a missing estimate of birth weight ({100 * R["bw_missing_rate"]:.1f}% of children). County fixed effects included; village-clustered standard errors.')
        heading(doc, 'Part 2. Supplementary figures', 1)
        for f, ttl, note in [('FigureA1_birth_weight_bins', 'Figure A1. Nonlinearity in the birth weight gradient', 'Notes. Coefficients and 95% confidence intervals for birth weight bins (reference 2.5 to 3.0 kg), baseline controls and county fixed effects, village-clustered standard errors.'),
                             ('FigureA2_attrition', 'Figure A2. Follow-up by birth weight', 'Notes. Share of children with the outcome observed, by estimated birth weight bin.'),
                             ('FigureA3_oster_bounds', 'Figure A3. Bias-adjusted coefficients (Oster bounds)', 'Notes. Bars: bias-adjusted coefficient assuming selection on unobservables equals selection on observables (delta = 1) and Rmax = min(1, 1.3 times the R2 of the controlled model); ticks: controlled estimate.')]:
            heading(doc, ttl, 2)
            figure(doc, os.path.join(FIG, f + '.png'), width=5.8)
            para(doc, note, spacing=1.0, size=9)
        insert_toc_at(doc, anchor, pages)
        return doc
    path = os.path.join(MS, 'Supplementary_Appendix.docx'); d1 = make(); d1.save(path)
    pages = compute_pages(path, d1._heads, 'This appendix contains'); d2 = make(pages); d2.save(path)

# ================================================================== title page, cover letter, highlights
def build_title_page():
    doc = new_doc(body_size=12)
    p = doc.add_paragraph(style='Title'); p.add_run('Title Page')
    heading(doc, 'Title', 1, bookmark=False); para(doc, mt.TITLE, spacing=1.15, space_after=6)
    heading(doc, 'Authors and affiliations', 1, bookmark=False)
    para(doc, 'Qixin Cai', spacing=1.15)
    para(doc, 'Population Aging Research Center, University of Pennsylvania, Philadelphia, PA, USA', spacing=1.15)
    para(doc, '[Add co-authors, their affiliations, and ORCID iDs, or confirm single authorship]', spacing=1.15, highlight=True, space_after=6)
    heading(doc, 'Corresponding author', 1, bookmark=False)
    para(doc, 'Qixin Cai, Population Aging Research Center, University of Pennsylvania. E-mail: caiqixin1995@gmail.com [replace with institutional e-mail if preferred]. [Add postal address and telephone.]', spacing=1.15, space_after=6)
    heading(doc, 'Running title', 1, bookmark=False); para(doc, 'Birth weight and child development in rural China', spacing=1.15)
    heading(doc, 'Manuscript details', 1, bookmark=False)
    B = mt.build()
    para(doc, f'Abstract: {len(mt.ABSTRACT.split())} words. Main text (Introduction to Conclusion): approximately {body_words(B):,} words. Tables: 6. Figures: 6. Supplementary Appendix: 8 tables and 3 figures.', spacing=1.15)
    heading(doc, 'Keywords', 1, bookmark=False); para(doc, mt.KEYWORDS, spacing=1.15)
    heading(doc, 'Declarations', 1, bookmark=False)
    heading(doc, 'Funding', 2, bookmark=False); para(doc, '[Author to complete]', spacing=1.15, highlight=True)
    heading(doc, 'Declaration of competing interests', 2, bookmark=False); para(doc, '[Author to confirm]', spacing=1.15, highlight=True)
    heading(doc, 'Ethics', 2, bookmark=False); para(doc, 'This study analyzes de-identified data from the Gansu Survey of Children and Families. [Author to confirm approval and data-use terms for the survey release.]', spacing=1.15, highlight=True)
    heading(doc, 'Data availability', 2, bookmark=False); para(doc, 'The GSCF data are available through the survey\'s data release. Analysis code will be deposited upon acceptance.', spacing=1.15)
    heading(doc, 'Declaration of generative AI use', 2, bookmark=False)
    para(doc, 'During the preparation of this work the author used an AI assistant (Claude, Anthropic) to draft analysis code and manuscript text. The author reviewed and edited the content and takes full responsibility for it. [Author to confirm wording against the target journal\'s AI policy.]', spacing=1.15, highlight=True)
    doc.save(os.path.join(MS, 'Title_Page.docx'))

def build_cover_letter():
    doc = new_doc(body_size=12)
    p = doc.add_paragraph(style='Title'); p.add_run('Cover Letter')
    para(doc, datetime.date.today().strftime('%B %d, %Y').replace(' 0', ' '), spacing=1.15, space_after=8)
    para(doc, 'The Editors\nSocial Science & Medicine', spacing=1.15, space_after=8)
    heading(doc, 'Re: Submission of an original research article', 1, bookmark=False)
    body = [
     'Dear Editors,',
     f'Please consider the enclosed manuscript, "{mt.TITLE}", for publication in Social Science & Medicine as an original research article.',
     'The paper asks whether weak birth endowments leave lasting marks on child development in a poor rural population, and whether parents compensate or reinforce. It uses the Gansu Survey of Children and Families, which followed 2,000 rural children from ages 9 to 12 in 2000 through 2009 with standardized tests and a health examination. Maternal reports of birth weight predict adolescent height by 0.17 standard deviations per kilogram, a gradient that holds under wild cluster bootstrap inference, attrition weights, and coefficient stability bounds. Gradients for cognitive and academic scores have the same sign but are smaller and imprecise. Parents invest more in children with stronger endowments, and exploratory interactions link steeper gradients to expectations of old-age support from children.',
     'We believe the paper fits the journal for three reasons. It examines the social patterning of early-life health and its consequences in a low-income setting, it connects the developmental origins literature to the demography of old-age support, and it reports its limits openly, with negative control outcomes, corrections for multiple testing, and a clear separation of confirmatory from exploratory results.',
     'The manuscript has not been published and is not under consideration elsewhere. [Author to confirm.] All authors have approved the submission. [Author to confirm.] The analysis uses de-identified survey data, and the replication code will be shared upon acceptance. Generative AI assistance in drafting is disclosed on the title page.',
     'Suggested reviewers: [Author to supply, with institutional e-mail addresses and no conflicts of interest.]',
     'Thank you for your consideration.',
     'Sincerely,',
     'Qixin Cai\nPopulation Aging Research Center, University of Pennsylvania']
    for t in body:
        para(doc, t, spacing=1.15, space_after=8, highlight=('[Author' in t))
    doc.save(os.path.join(MS, 'Cover_Letter.docx'))

def build_highlights():
    doc = new_doc(body_size=12)
    p = doc.add_paragraph(style='Title'); p.add_run('Highlights')
    heading(doc, 'Highlights (maximum 85 characters each, including spaces)', 1, bookmark=False)
    HL = ['Reported birth weight predicts adolescent height in rural Gansu children',
          'Birth weight gradients in cognitive and academic scores are small and imprecise',
          'Parents reinforce rather than compensate for weaker birth endowments',
          'Old-age support expectations may steepen birth endowment gradients (exploratory)']
    for h in HL:
        assert len(h) <= 85, (len(h), h)
        p = doc.add_paragraph(style='List Bullet'); p.add_run(h)
        p.paragraph_format.line_spacing = 1.5
    heading(doc, 'Character counts', 2, bookmark=False)
    for h in HL: para(doc, f'{len(h)} characters: {h}', spacing=1.15, size=10)
    doc.save(os.path.join(MS, 'Highlights.docx'))

if __name__ == '__main__':
    heads, pages = build_manuscript(); print('manuscript headings', len(heads))
    build_tables(); build_figures(); build_appendix(); build_title_page(); build_cover_letter(); build_highlights()
    print('words (main text):', body_words(mt.build()))
    print(sorted(os.listdir(MS)))
