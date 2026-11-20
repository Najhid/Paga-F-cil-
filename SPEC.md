# SPEC: PagaFácil

Last updated: 2026-11-20 · Owners: Angel Najhid Flores Cartagena + Luciano Yitani Chapa

## Problem
University students in Mexico often have no credit card and a thin credit history, so they
cannot split a large one-off purchase (textbooks and school supplies at the start of the
semester) into payments. Today they either pay all at once, borrow from family, or use
informal credit. PagaFácil is a BNPL fintech with a bank partnership. The prototype
simulates the checkout, merchant payout and installment tracking; it does not establish
which party is the lender of record, owns the receivable, funds the loan, receives interest,
or bears credit losses. Do not present the simulated gross loan economics as PagaFácil's
standalone revenue or cost of funds.

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
- **User:** name, declared monthly income (León: $6,000 MXN, invented), initial credit limit of $6,500 MXN (invented).
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
- `formulas[excel]==1.3.4` for workbook formula tests; its `excel` extra supplies `openpyxl`, which those tests use to inspect and prepare workbook copies. These are development/test dependencies, not Flask runtime features.

## Out of scope this semester
- Real payments, real KYC, real credit bureau queries
- Native mobile app; more than one user role or more than one merchant
- Late fees and collections process (default is modeled only as an assumption)
- Savings, deposits, yield or investment features (PagaFácil never holds client money)
- SOFOM E.N.R. registration or operation; PagaFácil's stated model is a bank partnership.
  The partner's contractual role and each party's economic and compliance responsibilities
  are not modeled or legally verified.

## Unit economics and break-even
These are assumption-based portfolio-level planning estimates, not verified operating
results or PagaFácil standalone financials. The calculations below are generated in the
`PagaFacil_Financial_Model.xlsx` workbook. They assume the modeled loan portfolio retains
the listed interest and merchant-fee revenue and bears the listed funding cost and loss
proxy. The bank-partner contract may allocate each item differently.

### Inputs and definitions
- Base planning ticket: $2,500 MXN. Ticket planning range: $2,500 to $4,000 MXN.
  The range reflects the team's final design scenario and is consistent with the upper
  purchase bands reported by the 25 interviews. It is not a measured average, a bookstore
  sales average or a market estimate. $2,500 remains the central five-year P&L ticket.
- Pricing: flat interest of 4% of original ticket per month of term.
- Merchant fee: 4% of ticket; the funded merchant payout is 96% of ticket.
- Portfolio cost of funds: 10% annual in the planning case, applied monthly to the declining
  funded payout balance, assuming equal principal repayment. Banxico published TIIE at
  28 days of 6.5147% on 2026-11-19. The 10% case is 3.4853 percentage points above that
  public reference, not a quoted bank rate or a measured fintech borrowing spread. If the
  bank partner owns and funds the receivable, this expense belongs in the bank's portfolio
  economics unless the contract passes some or all of it through to PagaFácil.
- Delinquency/loss proxy: 7% of balances in arrears. For this simplified model only, apply
  7% to the original ticket as a full, unrecovered loss per loan. This is not equivalent
  to a statistically measured probability of default or loss rate; actual default loss
  requires the balance definition, observation period, cure rate and recoveries.
- Portfolio operating and credit-check cost: $40 per loan; PagaFácil's share is unverified.
- CAC: $200 per acquired customer.
- Conservative customer activity case: 1 loan per year for 4 years, or 4 lifetime loans per
  customer. This is a team-selected planning assumption, not measured repeat behavior.
- Team-estimated internal costs are $120,000 in Year 1: $25,000 personnel, $45,000 one-time
  technology setup, $25,000 recurring technology, and $25,000 office costs. Personnel,
  office and recurring technology are held constant in Years 2 to 5. These are team estimates,
  not quotes. SOFOM-specific technical-opinion fees and the previous SOFOM legal/compliance
  estimates have been removed from the current bank-partner case. The workbook's
  `Bank Partner Economics` sheet collects PagaFácil's contracted compensation and allocated
  funding, loss, servicing, partner, legal and compliance costs. Its company P&L, EBITDA and
  break-even stay blank until these required inputs are supported by the executed agreement
  or written quotes. A confirmed zero must be entered as zero; blank means unknown.

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
CAC allocation, lifetime contribution, LTV/CAC, payback, ARPU and break-even values are not
PagaFácil company metrics until the bank agreement defines the revenue and cost allocation.
The workbook's acquisition and repeat-use inputs remain planning scenarios, not observed
performance.

The workbook separates portfolio scenarios from company economics. `Unit Economics` and
`Funding Benchmarks` show portfolio-level planning figures before bank settlement.
`Bank Partner Economics` is the evidence-gated input sheet, and `P&L` calculates PagaFácil
results only from those contractual compensation and cost-allocation inputs. Public APRs,
benchmark interest rates and competitors' legal structures are not substitutes for those
inputs.

At the $2,500 ticket, 7% simplified loss proxy and current pricing, the following is a
portfolio-level scenario before CAC and before any settlement with the bank partner:

| Term | Total interest | Effective annual rate (approx.) | Merchant fee | Cost of funds at 10% | Simplified loss proxy | Servicing assumption | Portfolio contribution before CAC and partner settlement |
|---|---:|---:|---:|---:|---:|---:|---:|
| 3 months | $300 | ~98% | $100 | $40 | $175 | $40 | $145 |
| 6 months | $600 | ~113% | $100 | $70 | $175 | $40 | $415 |
| 9 months | $900 | ~116% | $100 | $100 | $175 | $40 | $685 |
| 12 months | $1,200 | ~116% | $100 | $130 | $175 | $40 | $955 |

These are not revenues or profits attributable to PagaFácil. If the bank retains the loan
asset and funds it, the partner may retain interest revenue, bear funding costs and credit
losses, and pay PagaFácil a contractually defined fee. The workbook therefore leaves
company valuation and break-even pending rather than assigning a fictitious revenue share.

### Default/delinquency sensitivity
The following scenarios use the same simplified full-loss proxy on original ticket,
but show only portfolio contribution before CAC and before bank-partner settlement. They
are sensitivity cases, not observed default rates or PagaFácil loss forecasts.

| Term | 5% proxy | 7% proxy | 10% proxy | 13% proxy |
|---|---:|---:|---:|---:|
| 3 months | $195 | $145 | $70 | -$5 |
| 6 months | $465 | $415 | $340 | $265 |
| 9 months | $735 | $685 | $610 | $535 |
| 12 months | $1,005 | $955 | $880 | $805 |

### Ticket sensitivity at 6 months and 7% proxy
The $1,500 and $4,000 tickets are illustrative scenarios, not measured low/high averages.

| Ticket | Portfolio contribution before CAC and partner settlement |
|---:|---:|
| $1,500 | $233 |
| $2,500 | $415 |
| $4,000 | $688 |

- Effective annual rate: the annual rate at which the present value of equal monthly
  installments equals the price financed (a monthly IRR compounded to one year). Banxico
  Circular 21/2009 defines CAT as the annual rate that equates the present value of credit
  disbursements and payments (source below). This estimate uses monthly periods and no IVA.
  Label it "effective annual rate" in the UI until exact CAT rules are confirmed.
  TODO-verify CAT calculation and disclosure rules with Condusef, including whether the
  Banxico draft changes published in November 2025 are in force.

Validation status of the inputs (updated 2026-11-20; values remain assumptions unless a
specific source and matching definition are documented):

| Input | Current value | Status / source fit |
|---|---:|---|
| Average ticket | $2,500 base; $2,500–$4,000 planning range | Planning scenario. Expansion reports Kueski/Amazon purchases from $299 to $5,000, but this does not validate a university average. The 25 interviews support $2,500–$4,000 as a product-design range, not as a statistical mean. |
| UP CDMX student population | No verified 2026 UP CDMX count is available | Data México reports 14,693 enrollments for Universidad Panamericana overall in 2022 and 6,763 associated with Zacatecas / Benito Juárez, not the UP CDMX campus. Use neither figure as campus enrollment or TAM. |
| Student interviews | 25 real interviews: 13 Finance and 12 Law | Recorded in the field questionnaire for 3rd to 5th semester students. The sample is a convenience sample, not representative demand evidence for the full UP student population. |
| Delinquency/loss proxy | 7% of original ticket in the final planning scenario | Simplified portfolio sensitivity only. It is not a PD, LGD or measured PagaFácil loss rate and must not be presented as observed portfolio performance. |
| Loans per customer | 4 lifetime, modeled as 1 per year for 4 years | Team-selected conservative assumption; actual repeat frequency is unknown. |
| Customer lifetime | 4 years in this scenario | Implied by the 1-loan-per-year, 4-year planning case; actual retention is unknown. |
| CAC | $200 per customer | Assumption; requires actual PagaFácil acquisition spending divided by new PagaFácil-acquired customers approved and funded. |
| Customer acquisition forecast | About 100 new students in Year 1; 25 new students per year in Years 2 to 5 | Team-approved planning scenario, not a market forecast. At the assumed $200 CAC, acquisition expense is $20,000 in Year 1 and $5,000 per year in Years 2 to 5. This totals 200 new customers and $40,000 of acquisition expense over five years. |
| Loan origination timing | 50% in January and 50% in August | Team-approved planning scenario for the cash model. With six-month loans and installments starting one month after origination, Year 1 collects 11/12 of its originations' contractual repayments; later years collect 11/12 of current-year and 1/12 of prior-year originations. These are scheduled amounts before missed-payment effects, not dated payment data. |
| Funding mix / partner settlement | Not set | The 60% debt / 40% equity split was a prior standalone financing illustration and is superseded. The bank contract must define lender of record, receivable ownership, funds flow, fee sharing and loss allocation. |
| Operating and credit-check cost | $40 per portfolio loan | Assumption; obtain actual provider quotes and confirm whether PagaFácil or the bank bears each cost. |
| Fixed costs | $120,000 preliminary internal-cost estimate | Team estimates for personnel, technology and office only. The prior SOFOM technical-opinion fee and SOFOM legal/compliance estimates are excluded. Bank implementation, servicing, legal, compliance and settlement costs are unquoted; standalone P&L and break-even remain incomplete. |
| Cost of funds | 10% annual portfolio scenario | Banxico's TIIE at 28 days was 6.5147% on 2026-11-19; 10% is 3.4853 percentage points higher. It is an uncontracted portfolio scenario, not PagaFácil's borrowing cost. If the bank owns and funds the loans, the bank's contract determines whether any funding cost is charged through to PagaFácil. |

### Public household, risk and funding context

The supplied source compilation reports from INEGI's 2024 ENIGH an average quarterly
household current income of $77,864 MXN and quarterly household education and recreation
spending of $4,593 MXN, equivalent to about $1,531 per month for that combined category.
These are national household averages, not student income, discretionary income, campus
spending or a purchase-ticket estimate. They do not validate the $2,500-$4,000 planning
range.

CONDUSEF/INEGI's ENSAFI 2023 reports that 36.2% of adults had some form of debt, 17.1%
described their debt level as high or excessive, the average amount adults said they could
pay toward debt monthly without compromising their assets was $2,777 MXN, and 38.8%
reported being very worried when asking for a loan. These nationwide adult figures are
context for affordability and borrower risk, not estimates for UP students or PagaFácil
defaults. They caution against reading stated interest in a survey as demonstrated
repayment capacity.

For funding context as of 2026-11-19, Banxico reported CETES at 28 days of 6.19%, TIIE
de fondeo at one day of 6.26%, and TIIE at 28 days of 6.5147%. These are sovereign or
interbank reference rates, not a quoted BNPL credit facility. A commercial rate may also
reflect spread, fees, term, utilization, collateral, servicing and risk allocation. The
10% case is a team-selected sensitivity, not a verified spread over TIIE. The workbook
shows the portfolio contribution sensitivity at the public rate benchmarks and at the
10% and 12% planning cases.

The supplied compilation also cites a 2.9%-3.5% bank consumer-credit IMOR range, but does
not identify one exact CNBV table, portfolio definition and observation date for that
range. It is not adopted as a verified benchmark. Even a correctly sourced sector IMOR
would not be comparable to PagaFácil's 7% simplified loss proxy or a thin-file student
portfolio.

### Final evidence gap register

The project is complete as an academic prototype. The following items remain required evidence if PagaFácil were to move beyond the prototype stage. They must not be described as verified project data.

| Evidence needed | Required source or format | Definitive use |
|---|---|---|
| UP CDMX enrollment and eligibility | Official 2026 student or campus record; exact year, campus and denominator | Define the campus population and eligible borrower count |
| Merchant transaction distribution | Anonymized CSV/XLSX with ticket, count, frequency and merchant | Replace the MXN 2,500 central ticket and validate the MXN 2,500–4,000 range |
| Merchant fees | Written MDR quote | Separate merchant economics from student interest and funding cost |
| Bank-partner economics | Executed term sheet/contract showing lender of record, receivable owner, settlement, compensation, pass-through funding/loss costs and fees | Replace portfolio-only assumptions with PagaFácil revenue, expenses and funding allocation |
| Origination, credit and payout costs | Provider quotes plus internal servicing time and cost | Replace the MXN 40 per-loan assumption |
| CAC | Acquisition spend divided by approved and funded customers | Replace the MXN 200 CAC assumption |
| Actual credit performance | Anonymized loan-level CSV by vintage, with 30+/90+ days past due, recoveries and terminations | Estimate PD, LGD and EAD by vintage |
| Repeat use | Account-level loan count and time between loans | Replace the four-loan lifetime assumption |
| Fixed legal and compliance costs | Bank agreement and written counsel/provider quotes; responsibility, scope and renewal period | Replace missing PagaFácil legal, compliance, servicing and partner-cost inputs |

### Reported population and interview evidence

The initial geography is the Universidad Panamericana campus in Ciudad de México. The official
[UP campus page](https://www.up.edu.mx/campus-up/cdmx/) confirms the location, but does not
publish an enrollment count. The official [Data México profile](https://www.economia.gob.mx/datamexico/es/profile/institution/universidad-panamericana)
reports 14,693 matriculated students for Universidad Panamericana overall in 2022. The same
profile associates 6,763 matriculated students with Zacatecas and the municipality of Benito
Juárez, which is not a UP CDMX campus count. No 2026 UP CDMX enrollment figure has been
published in the source used for the project.

The workbook does not use 6,763 or 16,500 as a market ceiling. It retains 14,693 only as
an institution-wide 2022 context scenario. A hypothetical 100% adoption case is conditional
portfolio volume and revenue before partner allocation:

- Hypothetical annual financed volume = `14,693 × $2,500 × 1 loan = $36,732,500 MXN`.
- Gross revenue per six-month loan = `$2,500 × 4% × 6 months + $2,500 × 4% merchant fee = $700 MXN`.
- Hypothetical gross annual revenue = `14,693 × $700 = $10,285,100 MXN`.

These outputs are not PagaFácil company revenue, TAM, SAM, eligible-borrower counts, demand
forecasts or market-share claims. They exclude UP CDMX eligibility, income, purchase
frequency, partner revenue allocation, borrowing interest, approval and merchant
participation.

The supplied source compilation also notes a 2024 UP-wide count of 16,967 (12,180
undergraduate and 4,787 postgraduate), an undated historical mobile-site count of 7,550
for CDMX, and an estimated 5,700–5,800 CDMX undergraduate students obtained by applying a
2019 share of new entrants to the 2024 UP-wide undergraduate total. None is used as the
current CDMX population: the first combines campuses, the second has no date, and the
third applies an admissions flow share to a total enrollment stock. ANUIES provides an
interactive historical enrollment query by institution, campus, year and level, but the
current campus-level count was not confirmed in a publicly consolidated result.

The real field evidence consists of 25 completed questionnaires: 13 Finance students and
12 Law students, all in 3rd to 5th semester. This is a small convenience sample and may
inform product design, but it does not estimate demand for the full UP population.

Observed survey results include:

- 48% reported no own formal credit history.
- 88% accepted a Buró of Crédito consultation.
- 76% accepted interest if the total cost was transparent.
- 92% preferred a 3-month or 6-month term.
- 88% preferred SPEI or automatic debit for payment.
- 36% reported a typical purchase of $1,500 to $2,499 and 24% reported $2,500 to $3,999.

The $2,500 central planning ticket is consistent with the survey distribution. The full
scenario range is $2,500 to $4,000 MXN. It is selected for sensitivity and product
design, not calculated as the arithmetic average of all interview answers.

The five-year forecast's active customers of 100, 125, 150, 175 and 100 correspond to
approximately 0.68%, 0.85%, 1.02%, 1.19% and 0.68% of the 14,693 institution-wide context
scenario, respectively. These ratios are a planning comparison, not penetration, market share
or verified UP CDMX demand.

The 25 real interviews comprise 13 Finance and 12 Law students in 3rd to 5th semester.
Their results support product hypotheses: thin-file origin, 3/6-month terms and digital
payment channels. The sample is a convenience sample and cannot establish demand,
representativeness or product-market fit for the full UP population.

### Public competitor reference

Kueski Pay and Aplazo remain competitors because they solve a similar customer and
merchant financing problem. Their entity structure can differ from PagaFácil's bank
partnership, so they are product and market benchmarks, not direct funding-cost or
portfolio-risk comparables.

| Comparator | Publicly verified reference | Final PagaFácil use |
|---|---|---|
| Kueski Pay / Kueski | Kueski's official terms identify Kueski, S.A.P.I. de C.V., SOFOM E.N.R. Its current consumer-loan disclosure lists MXN 60–26,500, 99–180 days and 0%–486% APR. A disclosed example is MXN 1,000 repaid as MXN 1,101.87, including VAT on interest, over five fortnights; its CAT of 153.31% is dated 2026-03-02. Those terms describe Kueski credit, not necessarily every Kueski Pay checkout offer. Kueski Pay's current site is promotion-led; selected promotions display minimum baskets such as MXN 1,500. | Retain Kueski as a competitor and use public offers to compare product access, basket thresholds and user-facing cost. Keep Kueski personal-loan terms separate from Kueski Pay BNPL offers. Never use its APR/CAT as PagaFácil pricing or its entity form as a funding-cost proxy. |
| Kueski Pay / Amazon | A secondary 2024 report described purchases of MXN 299–5,000 and installment options at Amazon. It is historical and does not establish a current universal limit or average purchase. | Ecommerce price-range context only. It does not validate UP student purchases or the MXN 2,500–4,000 planning scenario. |
| Aplazo | Its current merchant directory shows store-specific plans; examples include 1–5 payments with no customer commission. The page does not establish one universal plan, a general MXN 5,000 threshold, or a merchant MDR. | Compare actual checkout terms by merchant. Do not generalize a featured store offer, copy a fee, or treat "sin comisión" as no merchant cost. |
| Mercado Pago / Mercado Crédito | Public pages reviewed do not provide one universal BNPL ticket, merchant discount rate or user cost comparable to this prototype. | Do not use card-processing fees or generic Mercado Pago terms as PagaFácil MDR or user cost. |

The Kueski public product disclosures reviewed do not provide a verifiable funding rate,
unit-economics statement or vintage loss table. The user APR/CAT is the price charged to
borrowers, not Kueski's cost of funds. Do not infer cost of capital, PD, LGD or EAD from
those consumer terms. The CNBV consumer-credit IMOR range in the supplied compilation is
excluded until its exact table, portfolio and date are cited; it would still be sector
context rather than Kueski or PagaFácil performance.

The $2,500–$4,000 university purchase range is a team planning scenario. The 25
interviews support product design and upper purchase bands, but they are a convenience
sample and do not calculate a market average.

## Regulatory notes
PagaFácil's current stated plan is a fintech working with a bank, not a SOFOM E.N.R.
The SOFOM-specific material below is retained only as historical background. It does not
determine the bank partner's legal role, responsibilities, or PagaFácil's obligations.
Those require review of the actual agreement and qualified counsel; this is not legal advice.

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
  This fee has been removed from the current bank-partner financial model. Do not include
  it as a PagaFácil cost unless counsel confirms a specific applicable process.

SOFOM registration timeline, SOFOM-specific legal costs and AML/PLD costs are not inputs
to the current plan. Bank partnership implementation, allocation of compliance
responsibilities and any partner charges remain subject to the actual contract and quotes.

## Sources
Existing regulatory and market references:
- Secretaría de Economía, Data México, Universidad Panamericana profile (14,693 university-wide enrollments in 2022; not a current campus-specific count):
  https://www.economia.gob.mx/datamexico/en/profile/institution/universidad-panamericana
- ANUIES, Historical Higher Education Statistical Yearbook query:
  https://anuario.anuies.mx/
- Universidad Panamericana, CDMX campus locations:
  https://www.up.edu.mx/campus-up/cdmx/
- INEGI, ENIGH 2024:
  https://www.inegi.org.mx/programas/enigh/nc/2024/
- CONDUSEF/INEGI, ENSAFI 2023 summary:
  https://www.gob.mx/condusef/prensa/encuesta-nacional-sobre-salud-financiera-ensafi-2023
- Banco de México, SIE TIIE and TIIE de fondeo:
  https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?sector=18&accion=consultarCuadro&idCuadro=CF111&locale=es
- Banco de México, SIE CETES auctions:
  https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?sector=22&accion=consultarCuadro&idCuadro=CF107&locale=es
- Kueski Pay, current offers:
  https://www.kueskipay.com/
- Kueski, current terms and consumer-loan disclosure:
  https://www.kueskipay.com/tyc
- Aplazo, merchant-specific plans:
  https://aplazo.mx/comercios
- CNBV, Portafolio de Información:
  https://www.cnbv.gob.mx/Paginas/Informacion-Estadistica.aspx
- Buró de Crédito:
  https://www.burodecredito.com.mx/
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
- INEGI, ENSAFI 2023 results presentation (PDF):
  https://www.inegi.org.mx/contenidos/programas/ensafi/2023/doc/ensafi_2023_presentacion_resultados.pdf
- Kueski, company information (company-published):
  https://www.kueski.com/sobre-nosotros
The Expansion article gives a reported transaction range, not an observed $2,500 average
ticket. ENIGH and ENSAFI provide household- or adult-population context, not student-specific
income, spending or PagaFácil borrower performance. Kueski's own site is company-reported
product information; it does not disclose its funding rate or vintage loss table in the
sources reviewed. None of these sources substantiates the 7% delinquency/loss proxy, four
lifetime loans, customer-acquisition scenario, $200 CAC, $40 operating cost or team fixed-cost
estimates; those remain planning inputs. The official SOFOM fee amount does not establish
PagaFácil's bank-partner legal, settlement or compliance costs.

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
originations or revenue. The 1.0x revenue and terminal multiples, 35% annual discount
rate and 50% VC target annual return remain illustrative workbook inputs only; they are
not market-derived assumptions or fair-market valuation. The earlier outputs, including
the approximately $15,611 MXN revenue-multiple result and negative VC/EBITDA-DCF results,
are superseded and must not be presented as PagaFácil valuation. The bank-partner contract
does not yet define PagaFácil net revenue, partner settlement or required capital, so
valuation outputs are pending. The workbook's earlier 60% debt / 40% equity funding split
is also superseded. The simplified EBITDA method is not a full DCF.

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
| 2026-11-20 | Connected the company P&L to explicit bank-partner compensation and cost-allocation inputs | The workbook separates portfolio scenarios from PagaFácil economics and leaves company outputs blank until contract terms and written cost quotes are available |
- LGOAAC, official text: https://www.diputados.gob.mx/LeyesBiblio/pdf/LGOAAC.pdf
- Banxico, Circular 21/2009 (CAT): https://www.banxico.org.mx/marco-normativo/normativa-emitida-por-el-banco-de-mexico/circular-21-2009/costo-anual-total-disposicion.html
- Banxico report to Congress, 2026-09-14: https://gaceta.diputados.gob.mx/PDF/66/2026/sep/Banxico-20260914.pdf

| 2026-11-15 | Regulatory notes rewritten after reading LGOAAC arts. 56, 87-B and 87-P and identifying the Banxico CAT circular; effective annual rate shown on the quote screen as a reference figure | Closes review item 5 for the sourced claims; timeline and cost figures remain unverified | Najhid + Luciano |
| 2026-11-16 | Replaced the 24-loan lifetime case with a conservative 4-loan lifetime case, modeled as 1 loan/year for 4 years; recalculated CAC allocation, LTV/CAC and break-even sensitivities | The earlier repeat-use assumption was unsupported and overstated 6-month LTV/CAC (49.8x); the selected case gives $1,660 lifetime contribution before CAC and 8.3x LTV/CAC | Najhid + Luciano |
| 2026-11-16 | Changed León's invented declared monthly income from $12,000 to $6,000 MXN | Makes the 30% affordability rule demonstrable in the checkout while preserving the $6,500 credit limit; product-design assumption, not a regulatory threshold | Najhid + Luciano |
| 2026-11-16 | Added a workbook planning scenario of $60,000 one-time private legal counsel in Year 1 and $30,000 annual ongoing compliance in Years 1 to 5; recalculated fixed costs and break-even sensitivities | Uses midpoints of unverified ranges already disclosed in the SPEC; these amounts are assumptions, not quotes, and remain TODO-verify. The scenario raises Year 1 modeled costs to $244,229.19 and recurring costs to $105,000 | Najhid + Luciano |
| 2026-11-16 | Added a 16,500-student upper-bound campus scenario, interview limitations, and an illustrative valuation with sensitivities; corrected ownership calculations to use required equity funding | The enrollment estimate and valuation inputs are explicitly unverified or illustrative, not official enrollment, demand, market multiples or fair value. Sensitivity tests passed; the market ceiling assumes 100% adoption and is not TAM/SAM | Najhid + Luciano |
