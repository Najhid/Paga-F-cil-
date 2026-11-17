# SPEC: PagaFácil

Last updated: 2026-11-16 · Owners: Angel Najhid Flores Cartagena + Luciano Yitani Chapa

## Problem
University students in Mexico often have no credit card and a thin credit history, so they
cannot split a large one-off purchase (textbooks and school supplies at the start of the
semester) into payments. Today they either pay all at once, borrow from family, or use
informal credit. PagaFácil is a Buy Now, Pay Later (BNPL) lender: it pays the merchant
and the student repays PagaFácil in monthly installments with interest.

## User
León Lara, 21, a university student who has just started working part-time, has no credit
card and no credit history. He needs to buy textbooks and supplies at the campus bookstore
at the start of the semester and can only afford them in 3 to 12 monthly payments.

## Core flow (the MVP)
The single flow that must work end to end at Demo Day:

1. León checks out at the campus bookstore (single fake merchant) with a cart total and
   chooses a term: 3, 6, 9 or 12 months.
2. The app shows the full cost before he accepts: interest, total to repay, installment
   amount and schedule.
3. A simple rule-based check approves or rejects the loan only if the requested amount is
   within his initial credit limit of $6,500 MXN and the monthly installment is no more
   than 30% of his declared monthly income. For example, a $2,500 loan over 6 months has
   a monthly installment of about $516.67 MXN under the 4%-per-month-of-term pricing
   (total repayment $3,100 MXN). This requires declared monthly income of at least
   $1,722.24 MXN ($516.67 / 0.30, rounded up to cents), or $1,723 MXN if income is stated
   in whole pesos. These are product-design assumptions, not regulatory requirements.
4. If approved, the app records the payout to the merchant (price minus the 4% merchant
   fee) and creates the installment schedule; León can mark an installment as paid or late
   and see his updated balance.

## Data model (plain words)
User has Loans; Merchant has Loans; each Loan has Installments.
- **User:** name, declared monthly income (León: $12,000 MXN, invented), initial credit limit of $6,500 MXN (invented).
- **Merchant:** name, merchant fee rate (4%).
- **Loan:** user, merchant, price, term in months, merchant fee, funded amount (price minus
  fee), total interest, total to repay, status (approved / active / paid / defaulted).
- **Installment:** loan, number, due date, amount, status (pending / paid / late / defaulted),
  paid date.

Pricing rule: flat interest of 4% per month of term on the original price (3 months = 12%,
6 = 24%, 9 = 36%, 12 = 48%). The quote screen must also show the effective annual rate
(about 98% to 116% at this pricing), because a flat "4% per month" looks much cheaper than
it is.

Approval rule: both conditions must be met: requested amount <= the user's credit limit
(initially $6,500 MXN) and monthly installment <= 30% of declared monthly income. The 30%
threshold and initial credit limit are product-design assumptions, not regulatory
requirements.

Late and default rule: an installment is late when it is unpaid after its due date. If it
remains unpaid for more than 45 calendar days past due (more than three quincenas), its
status changes from late to defaulted and the associated loan becomes defaulted. The
45-day threshold is our own design assumption. Default is only a status used to measure
the 5% default assumption; late fees and collections stay out of scope.

## Test environment and security

The app uses invented data created by `python -m src.seed`. The merchant payout is recorded
in the database but no money moves; credit approval is our own rule, not a bureau query;
payments are marked manually. The app does not perform KYC or identity verification.

- Sign-in uses usernames and hashed passwords. `SECRET_KEY` is read from the environment,
  never stored in the repository.
- Two invented accounts support the demo: León, with no initial loans, and Ana, with
  seeded loan history for demonstrating default and user isolation. Test passwords belong
  in the Blackboard submission, never the repository.
- Every loan page and installment action verifies that the loan belongs to the signed-in
  user; otherwise it returns 404.
- Every form carries a CSRF token. Loan amounts and approval are recalculated on the server.
- The checkout cart can be changed to demonstrate approval and rejection. Inputs must be
  greater than zero and at most $100,000 MXN.
- An installment cannot be marked late before its due date. A defaulted installment cannot
  be changed because collections are out of scope.

## Dependencies (closed list)
Anything not on this list needs both partners plus a bitacora entry.

- Python 3 standard library (includes SQLite)
- Flask
- pytest

## Out of scope this semester
- Real payments, real KYC, real credit bureau queries
- Native mobile app; more than one user role or more than one merchant
- Late fees and collections process (default is modeled only as an assumption)
- Savings, deposits, yield or investment features (PagaFácil never holds client money)
- Real regulatory registration (SOFOM E.N.R. is analyzed, not implemented)

## Unit economics and break-even
These are assumption-based planning estimates, not verified operating results. The
repository snapshot does not contain an `economics.py` calculator; the calculations below
are therefore documented estimates rather than values generated automatically.

### Inputs and definitions
- Average ticket: $2,500 MXN (kept as a planning assumption, not a measured average).
- Pricing: flat interest of 4% of original ticket per month of term.
- Merchant fee: 4% of ticket; the funded merchant payout is 96% of ticket.
- Cost of funds: 10% annual, applied monthly to the declining funded payout balance,
  assuming equal principal repayment.
- Delinquency/loss proxy: 7% of balances in arrears. For this simplified model only, apply
  7% to the original ticket as a full, unrecovered loss per loan. This is not equivalent
  to a statistically measured probability of default or loss rate; actual default loss
  requires the balance definition, observation period, cure rate and recoveries.
- Operating and credit-check cost: $40 per loan.
- CAC: $200 per acquired customer.
- Conservative customer activity case: 1 loan per year for 4 years, or 4 lifetime loans per
  customer. This is a team-selected planning assumption, not measured repeat behavior.
- Year 1 fixed costs before the potential official fee: $120,000 in total: $25,000
  personnel, $45,000 one-time technology setup, $25,000 recurring technology, and $25,000
  office costs. Personnel, office and recurring technology are modeled at the same amounts
  in Years 2 to 5. A potential $34,229.19 official technical-opinion fee is added to Year 1
  for the SOFOM E.N.R. scenario, making modeled Year 1 fixed costs $154,229.19. Legal
  counsel and ongoing regulatory/compliance costs are not included. These are team
  estimates except for the cited official fee. Year 1 includes one-time costs and must not
  be used as a recurring steady-state cost budget. Known recurring costs total $75,000
  annually, excluding unbudgeted legal and regulatory costs.

For ticket `P`, term `n` months, delinquency/loss proxy `d`, and annual cost of funds `r`:
- Interest = `P × 4% × n`.
- Merchant fee = `P × 4%`.
- Cost of funds = `(P × 96%) × (r / 12) × (n + 1) / 2`.
- Simplified expected loss = `P × d`.
- Contribution before CAC = interest + merchant fee - cost of funds - simplified expected
  loss - $40.
- First-year CAC allocated per loan, if each newly acquired customer takes 1 loan in that
  year = `$200 / 1 = $200`.
- Steady-state CAC allocated per loan, if customers take 1 loan per year for 4 years =
  `$200 / 4 = $50`.
- For either horizon, contribution after CAC allocation = contribution before CAC minus
  the applicable CAC per loan.
- Year 1 cost-recovery loans = ceiling(`$154,229.19 / contribution after CAC allocation`).
  There is no finite break-even if contribution after CAC allocation is zero or negative.
  Steady-state break-even is not calculated until legal/regulatory and other unbudgeted
  recurring fixed costs are estimated.
- Lifetime contribution before CAC = contribution before CAC × 4 loans. LTV/CAC is
  lifetime contribution before CAC divided by $200; this excludes fixed costs and should
  not be interpreted as net profit.

The $200 CAC allocation estimates first-year economics when each loan belongs to a newly
acquired customer taking one loan that year. The $50 allocation spreads one customer's CAC
across four assumed lifetime loans. Year 1 cost recovery uses the $154,229.19 budget,
including one-time setup and the potential official fee, and is not a recurring operating
break-even. Steady-state fixed costs are
unknown because legal/regulatory costs are not budgeted separately. The known recurring
personnel, office and technology costs total $75,000 annually, excluding those unbudgeted
costs. Under this case, annual loan volume corresponds to annual customer-loans only if
each customer takes one loan in that year.

At the $2,500 ticket, 7% simplified loss proxy and current 4%-per-month-of-term pricing:

| Term | Total interest | Effective annual rate (approx.) | Merchant fee | Cost of funds | Simplified expected loss | Operating cost | Contribution before CAC | After $200 first-year CAC allocation | First-year cost-recovery loans | After $50 steady-state CAC allocation | Steady-state cost-recovery loans |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 3 months | $300 | ~98% | $100 | $40 | $175 | $40 | $145 | -$55 | none | $95 | pending |
| 6 months | $600 | ~113% | $100 | $70 | $175 | $40 | $415 | $215 | 718 | $365 | pending |
| 9 months | $900 | ~116% | $100 | $100 | $175 | $40 | $685 | $485 | 318 | $635 | pending |
| 12 months | $1,200 | ~116% | $100 | $130 | $175 | $40 | $955 | $755 | 205 | $905 | pending |

At the 6-month base term, estimated lifetime contribution before CAC is `$415 × 4 =
$1,660` per customer, and LTV/CAC is `$1,660 / $200 = 8.3x`, before fixed costs. With one
loan per newly acquired customer in year one, the Year 1 cost-recovery estimate is 718
six-month loans. Steady-state cost-recovery is pending because legal/regulatory costs are
not budgeted. The Year 1 $154,229.19 total includes $45,000 of one-time technology setup
and a potential official fee, so its recovery volume is not a recurring operating target.

### Default/delinquency sensitivity
The following scenarios use the same simplified full-loss proxy on original ticket,
allocate $200 CAC per first-year loan, and hold Year 1 fixed costs at $154,229.19,
including the potential official fee. They are
scenarios, not observed default rates. The word "none" means no finite break-even under
the assumptions.

| Term | 5% proxy | 7% proxy | 10% proxy | 13% proxy |
|---|---:|---:|---:|---:|
| 3 months | none | none | none | none |
| 6 months | 582 loans | 718 loans | 1,102 loans | 2,373 loans |
| 9 months | 289 loans | 318 loans | 377 loans | 461 loans |
| 12 months | 192 loans | 205 loans | 227 loans | 256 loans |

### Ticket sensitivity at 6 months and 7% proxy
The $1,500 and $4,000 tickets are illustrative scenarios, not measured low/high averages.

| Ticket | Contribution before CAC | After $200 first-year CAC allocation | First-year break-even loans |
|---:|---:|---:|---:|
| $1,500 | $233 | $33 | 4,674 |
| $2,500 | $415 | $215 | 718 |
| $4,000 | $688 | $488 | 317 |

- Effective annual rate: the annual rate at which the present value of equal monthly
  installments equals the price financed (a monthly IRR compounded to one year). Banxico
  Circular 21/2009 defines CAT as the annual rate that equates the present value of credit
  disbursements and payments (source below). This estimate uses monthly periods and no IVA.
  Label it "effective annual rate" in the UI until exact CAT rules are confirmed.
  TODO-verify CAT calculation and disclosure rules with Condusef, including whether the
  Banxico draft changes published in November 2025 are in force.

Validation status of the inputs (updated 2026-11-16; values remain assumptions unless a
specific source and matching definition are documented):

| Input | Current value | Status / source fit |
|---|---:|---|
| Average ticket | $2,500 | Assumption. Expansion reports Kueski/Amazon purchases from $299 to $5,000; this supports a possible market range, not a $2,500 average. |
| Delinquency/loss proxy | 7% of balances | User-provided modeling assumption. The cited sources do not establish this as PagaFácil's default or net loss rate; proxy treatment is deliberately simplified and must be replaced with comparable portfolio data and recovery rates. |
| Loans per customer | 4 lifetime, modeled as 1 per year for 4 years | Team-selected conservative assumption; actual repeat frequency is unknown. |
| Customer lifetime | 4 years in this scenario | Implied by the 1-loan-per-year, 4-year planning case; actual retention is unknown. |
| CAC | $200 per customer | Assumption; requires actual acquisition spending divided by new acquired customers. |
| Customer acquisition forecast | About 100 new students in Year 1; 25 new students per year in Years 2 to 5 | Team-approved planning scenario, not a market forecast. At the assumed $200 CAC, acquisition expense is $20,000 in Year 1 and $5,000 per year in Years 2 to 5. This totals 200 new customers and $40,000 of acquisition expense over five years. |
| Loan origination timing | 50% in January and 50% in August | Team-approved planning scenario for the cash model. With six-month loans and installments starting one month after origination, Year 1 collects 11/12 of its originations' contractual repayments; later years collect 11/12 of current-year and 1/12 of prior-year originations. These are scheduled amounts before missed-payment effects, not dated payment data. |
| Funding mix | 60% debt; 40% equity | Team-approved illustrative split of required capital. Debt interest, term, fees, repayment schedule, and financing availability are not modeled, so this is not a validated funding plan. |
| Operating and credit-check cost | $40 per loan | Assumption; obtain actual provider quotes and servicing cost breakdown. |
| Fixed costs | $154,229.19 Year 1: $120,000 team estimates plus $34,229.19 potential official fee | The 2026 fee schedule lists $34,229.19 for LFD Article 29 XXVI; CNBV's FAQ associates that fraction with the AML technical-opinion procedure but shows an outdated 2016 amount. Verify applicability and renewal frequency. Legal counsel and ongoing compliance costs remain unbudgeted. |
| Cost of funds | 10% annual | Assumption; prior reference was 28-day TIIE at 6.5147% on 2026-11-06 (Banxico, DOF), not a lender quote. |

## Regulatory notes
Checked on 2026-11-11 against the public pages listed under Sources. Only the search
snippets of these pages were read, not the full legal text, so a fintech lawyer should
still confirm them.

Sourced:
## Regulatory notes
Checked on 2026-11-15. The text of LGOAAC articles 56, 87-B and 87-P was read in full
(Camara de Diputados text, last reform DOF 2025-11-14, read through the mLey.mx mirror).
Banxico Circular 21/2009 was identified from the DOF and Banxico pages. A fintech lawyer
should still confirm all of this.

Sourced:
- LGOAAC art. 87-B, first paragraph: granting credit habitually and professionally does not
  require authorization from the federal government. Only a corporation (S.A.) with a valid
  CONDUSEF registration is considered a SOFOM. Registering as a SOFOM E.N.R. is therefore a
  legal status, not a precondition to lend. TODO-verify with a lawyer which other obligations
  (for example AML) would apply if the company did not register.
- LGOAAC art. 87-B item IV and art. 87-P: a SOFOM E.N.R. must obtain from the CNBV, before
  registering, a favorable technical opinion on its AML/PLD program. The request includes the
  internal AML policies, the designation of compliance areas and a sworn statement that it has
  an automated system. If the CNBV does not resolve within its deadlines, the request is deemed
  approved.
- LGOAAC art. 56, second paragraph: the CNBV inspects a SOFOM E.N.R. exclusively to verify
  compliance with article 95 Bis and the rules derived from it.
- Banxico Circular 21/2009 (DOF 2009-09-04) sets the CAT methodology and applies, among
  others, to regulated and non-regulated SOFOMs and to companies that habitually grant credit.
  It was amended by Circulars 27/2009, 9/2015 and 15/2015. Banxico's report to Congress of
  September 2026 mentions a public consultation to modify it. TODO-verify the final text
  before calling any figure on screen "CAT".
- CNBV FAQ for SOFOM E.N.R. associates LFD article 29, fraction XXVI with the AML
  technical-opinion procedure, but its displayed $21,292 MXN fee is for fiscal year 2016
  and is outdated. The official 2026 update of amounts lists $34,229.19 for that fraction.
  The model treats this as a potential Year 1 application fee; TODO-verify applicability
  and renewal frequency with legal counsel.

Not verified (no official source found; these stay as assumptions, TODO-verify with a
fintech lawyer):
- Registration timeline (3 to 4 months) and legal cost range ($40,000 to $80,000 MXN).
- AML/PLD compliance cost ($20,000 to $40,000 MXN per year).

## Sources
Existing regulatory and market references:
- CONDUSEF, SIPRES: https://webapps.condusef.gob.mx/SIPRES/jsp/index.jsp
- CONDUSEF, Sofomes booklet: https://www.condusef.gob.mx/documentos/111134_CUADERNOSYVIDEOS-SOFOMES.pdf
- gob.mx, Sofomes No Reguladas: https://www.gob.mx/cms/uploads/attachment/file/109296/Sofomes_No_Reguladas.pdf
- CNBV, FAQ SOFOM E.N.R.: https://www.cnbv.gob.mx/PrevencionDeLavadoDeDinero/Preguntas-Frecuentes/Paginas/PF-Sofomes.aspx
- Cámara de Diputados, Ley Federal de Derechos, 2026 update of amounts (Anexo 19):
  https://www.diputados.gob.mx/LeyesBiblio/ref/lfd/LFD_cant24_28dic25.doc
- Cámara de Diputados, legislative history for the Ley Federal de Derechos:
  https://www.diputados.gob.mx/LeyesBiblio/ref/lfd.htm
- Banxico, Circular 21/2009 (CAT), DOF 2009-09-04: https://dof.gob.mx/nota_detalle.php?codigo=5108217&fecha=04/09/2009
- Banxico, TIIE of 2026-11-06 (DOF): https://sidof.segob.gob.mx/notas/docFuente/5803287
- Expansion, 2026-08-27, delinquency (CNBV IMORA): https://expansion.mx/economia/2026/08/27/mexicanos-gastaron-mundial-tarjeta-morosidad

Additional sources provided for market context (they do not independently verify all
financial-model inputs above):
- Expansion, 2024-02-15, Kueski/Amazon payment options and reported purchase range
  ($299-$5,000): https://expansion.mx/economia/2024/02/15/kueski-meses-sin-intereses-amazon
- CONDUSEF, ENSAFI 2023 summary: https://www.gob.mx/condusef/prensa/encuesta-nacional-sobre-salud-financiera-ensafi-2023
- INEGI, ENSAFI 2023 results presentation (PDF):
  https://www.inegi.org.mx/contenidos/programas/ensafi/2023/doc/ensafi_2023_presentacion_resultados.pdf
- Kueski, company information (company-published):
  https://www.kueski.com/sobre-nosotros
- DPL News link provided for the Kueski/Amazon BNPL item:
  https://dplnews.com/kueski-llega-3-millones-bnpl-amazon/
  The URL currently opens an unrelated Nu customer-growth article; verify/correct the
  link before treating it as evidence.

The Expansion article gives a reported transaction range, not an observed $2,500 average
ticket. ENSAFI provides population-level financial-health context, not PagaFácil borrower
default data. Kueski's own site is company-reported information. None of these sources
substantiates the 7% delinquency/loss proxy, four lifetime loans, customer-acquisition
scenario, $200 CAC, $40 operating cost or team fixed-cost estimates; those remain planning
inputs. The official fee amount does not establish private legal or ongoing compliance
costs.

### Public BNPL valuation references screened on 2026-11-16

Two listed lenders were screened as public-market context, not selected as valuation
comparables:

| Company | Estimated equity market capitalization | TTM reported revenue | Equity market capitalization / TTM revenue |
|---|---:|---:|---:|
| Affirm | USD 21,259.6 million | USD 4,590.0 million | 4.63x |
| Sezzle | USD 5,470.2 million | USD 581.6 million | 9.41x |

Market capitalization is estimated as the November 16, 2026 Nasdaq closing price times
the latest common-share count reported in the filings. TTM revenue is calculated from
reported periods: Affirm, USD 4,261.082 million FY2026 revenue plus USD 1,262.216 million
for the September 2026 quarter minus USD 933.337 million for the September 2025 quarter;
Sezzle, USD 450.279 million FY2025 revenue plus USD 451.725 million for the nine months
ended September 2026 minus USD 320.410 million for the comparable 2025 period.

These are equity market capitalization-to-revenue observations, not enterprise
value-to-revenue multiples. The companies are established public U.S. lenders with
different scale, geography, customer base, product mix, reported revenue definitions and
operating history. PagaFácil is a Mexican student-lending prototype without validated
originations or revenue. The workbook's revenue-multiple and terminal-value inputs
therefore remain blank; these observations must not be copied into them. Discount rates,
the VC return hurdle and terminal assumptions also require explicit team agreement and
are not supplied by these comparables.

Primary sources:
- Affirm FY2026 Form 10-K:
  https://www.sec.gov/Archives/edgar/data/1820953/000162828026059279/afrm-20260630.htm
- Affirm Q1 FY2027 Form 10-Q:
  https://www.sec.gov/Archives/edgar/data/1820953/000162828026071153/afrm-20260930.htm
- Sezzle FY2025 Form 10-K:
  https://www.sec.gov/Archives/edgar/data/1662991/000166299126000016/szl-20251231.htm
- Sezzle Q3 2026 Form 10-Q:
  https://www.sec.gov/Archives/edgar/data/1662991/000166299126000171/szl-20260930.htm
- Nasdaq historical closing prices on 2026-11-16:
  https://api.nasdaq.com/api/quote/AFRM/historical?assetclass=stocks&fromdate=2026-11-16&todate=2026-11-17&limit=2
  https://api.nasdaq.com/api/quote/SEZL/historical?assetclass=stocks&fromdate=2026-11-16&todate=2026-11-17&limit=2

## Changelog
| Date | Change | Why | Approved by |
|---|---|---|---|
| 2026-11-03 | Initial SPEC drafted | Project restarted with corrected unit economics | Najhid + Luciano|
| 2026-11-06 | Flat interest raised from 2% to 4% per month of term; economics table, LTV, payback and break-even recomputed | Every term must recover CAC in the first loan and lower the break-even volume | Najhid + Luciano  |
| 2026-11-11 | Defined loan approval limits: monthly installment <= 30% of declared income and initial credit limit of $6,500 MXN | Approved by Najhid and Luciano to make the MVP approval rule measurable; both values are product-design assumptions, not regulatory requirements | Najhid + Luciano |
| 2026-11-12 | Corrected the six-month affordability example to match the current 4%-per-month-of-term pricing | The previous $467 installment example used an earlier rate; the current $2,500 example is $516.67 per month and requires at least $1,722.24 monthly income | Najhid + Luciano |
| 2026-11-14 | Changed the late-to-default threshold from 30 to more than 45 calendar days past due (more than three quincenas); the installment and associated loan become defaulted | Defines the delinquency rule for the MVP; the 45-day threshold is our design assumption | Najhid + Luciano |
| 2026-11-14 | Rebased unit economics to 7% delinquency-balance proxy, $2,500 ticket, 4 loans/year for 6 years, $200 CAC and $40 operating cost; recalculated term margins, LTV and annual break-even | Replaces the prior 5%/3-loan/CAC $180 assumptions. Under the current 4% pricing, the 6-month contribution is about $415 before CAC, lifetime LTV about $9,960, LTV/CAC about 49.8x and first-year cost-recovery volume about 329 loans; the 7% proxy is not a measured default/loss rate | Najhid + Luciano |
| 2026-11-16 | Revised Year 1 costs to $130,000: $30,000 personnel, $45,000 one-time technology, $25,000 recurring technology and $30,000 office; recalculated Year 1 break-even and marked steady-state break-even pending | Team estimates supersede the prior $120,000 and 25%/50%/25% allocation. Legal/regulatory costs are not separately budgeted; recurring personnel and office costs remain unknown | Najhid + Luciano |
| 2026-11-16 | Superseded the $130,000 draft with a $120,000 Year 1 fixed-cost budget: $25,000 personnel, $45,000 one-time technology, $25,000 recurring technology and $25,000 office; modeled personnel, office and recurring technology through Years 2 to 5 | Reconciles the approved categories to the retained $120,000 total. Legal/regulatory costs remain unbudgeted, so steady-state break-even is pending | Najhid + Luciano |
| 2026-11-16 | Added a potential $34,229.19 one-time Year 1 technical-opinion fee from the official 2026 LFD amount update; recalculated Year 1 cost recovery using total fixed costs of $154,229.19 | CNBV FAQ associates LFD article 29, fraction XXVI with the AML technical-opinion process but displays an outdated 2016 amount. Applicability and renewal frequency are TODO-verify; private legal and ongoing compliance costs remain unbudgeted | Najhid + Luciano |
| 2026-11-16 | Added the approved 50% January and 50% August origination scenario to the six-month cash model | Calculates annual scheduled collections while carrying the final August installment into the following year; missed-payment effects and intra-year liquidity remain simplified | Najhid + Luciano |
| 2026-11-16 | Set the illustrative funding split to 60% debt and 40% equity | Allocates the required raise by source only; debt service and financing terms remain unmodeled, so the split is not a financing plan | Najhid + Luciano |
| 2026-11-16 | Screened Affirm and Sezzle public-market data but left workbook valuation multiples and rates blank | Their market-capitalization/revenue ratios are not direct comparables for the Mexican student prototype and do not match the workbook's enterprise-value-like formula basis | Najhid + Luciano |
- LGOAAC, official text: https://www.diputados.gob.mx/LeyesBiblio/pdf/LGOAAC.pdf
- Banxico, Circular 21/2009 (CAT): https://www.banxico.org.mx/marco-normativo/normativa-emitida-por-el-banco-de-mexico/circular-21-2009/costo-anual-total-disposicion.html
- Banxico report to Congress, 2026-09-14: https://gaceta.diputados.gob.mx/PDF/66/2026/sep/Banxico-20260914.pdf

| 2026-11-15 | Regulatory notes rewritten after reading LGOAAC arts. 56, 87-B and 87-P and identifying the Banxico CAT circular; effective annual rate shown on the quote screen as a reference figure | Closes review item 5 for the sourced claims; timeline and cost figures remain unverified | Najhid + Luciano |
| 2026-11-16 | Replaced the 24-loan lifetime case with a conservative 4-loan lifetime case, modeled as 1 loan/year for 4 years; recalculated CAC allocation, LTV/CAC and break-even sensitivities | The earlier repeat-use assumption was unsupported and overstated 6-month LTV/CAC (49.8x); the selected case gives $1,660 lifetime contribution before CAC and 8.3x LTV/CAC | Najhid + Luciano |
