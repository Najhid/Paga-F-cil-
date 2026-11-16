# SPEC: PagaFácil

Last updated: 2026-11-14 · Owners: Angel Najhid Flores Cartagena + Luciano Yitani Chapa

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
- **User:** name, declared monthly income, initial credit limit of $6,500 MXN (invented).
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
- Customer activity: 4 loans per year for 6 years, or 24 lifetime loans per customer.
- Fixed costs: approximately $120,000 for year one, retained from the prior planning
  assumption. It remains unverified and mixes setup and recurring expenses; separate
  these before treating the result as a steady-state annual break-even.

For ticket `P`, term `n` months, delinquency/loss proxy `d`, and annual cost of funds `r`:
- Interest = `P × 4% × n`.
- Merchant fee = `P × 4%`.
- Cost of funds = `(P × 96%) × (r / 12) × (n + 1) / 2`.
- Simplified expected loss = `P × d`.
- Contribution before CAC = interest + merchant fee - cost of funds - simplified expected
  loss - $40.
- First-year CAC allocated per loan, if those loans come from newly acquired customers =
  `$200 / 4 = $50`.
- Steady-state CAC allocated per loan, if customers generate 4 loans/year for 6 years =
  `$200 / 24 = $8.33`.
- For either horizon, contribution after CAC allocation = contribution before CAC minus
  the applicable CAC per loan.
- Cost-recovery loans = ceiling(`$120,000 / contribution after CAC allocation`). There is
  no finite break-even if contribution after CAC allocation is zero or negative.
- Lifetime contribution before CAC = contribution before CAC × 24 loans. LTV/CAC is
  lifetime contribution before CAC divided by $200; this excludes fixed costs and should
  not be interpreted as net profit.

The $50 CAC allocation estimates first-year economics when each loan in the calculation
belongs to a newly acquired customer who takes four loans that year. The $8.33 allocation
spreads one customer's CAC across all 24 assumed lifetime loans and is the illustrative
steady-state case. The $120,000 budget mixes setup and recurring expenses, so neither
volume is a confirmed operating break-even. Dividing annual loan volume by four gives
customer-equivalents only if each customer actually takes four loans in that year.

At the $2,500 ticket, 7% simplified loss proxy and current 4%-per-month-of-term pricing:

| Term | Total interest | Effective annual rate (approx.) | Merchant fee | Cost of funds | Simplified expected loss | Operating cost | Contribution before CAC | After $50 first-year CAC allocation | First-year cost-recovery loans | After $8.33 steady-state CAC allocation | Steady-state cost-recovery loans |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 3 months | $300 | ~98% | $100 | $40 | $175 | $40 | $145 | $95 | 1,264 | $136.67 | 879 |
| 6 months | $600 | ~113% | $100 | $70 | $175 | $40 | $415 | $365 | 329 | $406.67 | 296 |
| 9 months | $900 | ~116% | $100 | $100 | $175 | $40 | $685 | $635 | 189 | $676.67 | 178 |
| 12 months | $1,200 | ~116% | $100 | $130 | $175 | $40 | $955 | $905 | 133 | $946.67 | 127 |

At the 6-month base term, estimated lifetime contribution before CAC is `$415 × 24 =
$9,960` per customer, and LTV/CAC is `$9,960 / $200 = 49.8x`, before fixed costs.
The first-year break-even estimate is 329 six-month loan-equivalents; with whole customers
acquired and four loans per customer that year, 83 customers would originate 332 loans.
The steady-state estimate is 296 six-month loans (about 74 active customer-equivalents at
four loans/year, with CAC amortized over the assumed six-year life). The $120,000 fixed
cost figure includes unverified setup and recurring costs, so neither figure is yet a
reliable operating target.

### Default/delinquency sensitivity
The following scenarios use the same simplified full-loss proxy on original ticket,
allocate $50 CAC per first-year loan, and hold fixed costs at $120,000. They are scenarios,
not observed default rates. The word "none" means no finite break-even under the assumptions.

| Term | 5% proxy | 7% proxy | 10% proxy | 13% proxy |
|---|---:|---:|---:|---:|
| 3 months | 828 loans | 1,264 loans | 6,000 loans | none |
| 6 months | 290 loans | 329 loans | 414 loans | 559 loans |
| 9 months | 176 loans | 189 loans | 215 loans | 248 loans |
| 12 months | 126 loans | 133 loans | 145 loans | 159 loans |

### Ticket sensitivity at 6 months and 7% proxy
The $1,500 and $4,000 tickets are illustrative scenarios, not measured low/high averages.

| Ticket | Contribution before CAC | After $50 first-year CAC allocation | First-year break-even loans |
|---:|---:|---:|---:|
| $1,500 | $233 | $183 | 656 |
| $2,500 | $415 | $365 | 329 |
| $4,000 | $688 | $638 | 189 |

- Effective annual rate: the annual rate at which the present value of equal monthly
  installments equals the price financed (a monthly IRR compounded to one year). Banxico
  Circular 21/2009 defines CAT as the annual rate that equates the present value of credit
  disbursements and payments (source below). This estimate uses monthly periods and no IVA.
  Label it "effective annual rate" in the UI until exact CAT rules are confirmed.
  TODO-verify CAT calculation and disclosure rules with Condusef, including whether the
  Banxico draft changes published in November 2025 are in force.

Validation status of the inputs (updated 2026-11-14; values remain assumptions unless a
specific source and matching definition are documented):

| Input | Current value | Status / source fit |
|---|---:|---|
| Average ticket | $2,500 | Assumption. Expansion reports Kueski/Amazon purchases from $299 to $5,000; this supports a possible market range, not a $2,500 average. |
| Delinquency/loss proxy | 7% of balances | User-provided modeling assumption. The cited sources do not establish this as PagaFácil's default or net loss rate; proxy treatment is deliberately simplified and must be replaced with comparable portfolio data and recovery rates. |
| Loans per customer | 4 per year | Assumption; supplied sources do not establish PagaFácil repeat frequency. |
| Customer lifetime | 6 years | Assumption; supplied sources do not verify retention or active lifespan. |
| CAC | $200 per customer | Assumption; requires actual acquisition spending divided by new acquired customers. |
| Operating and credit-check cost | $40 per loan | Assumption; obtain actual provider quotes and servicing cost breakdown. |
| Fixed costs | ~$120,000 year one | Retained planning assumption, not verified. Separate one-time setup from recurring annual costs. |
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
- CNBV FAQ for SOFOM E.N.R.: the fee for the technical opinion was $21,292 MXN for fiscal
  year 2016 (outdated). TODO-verify the current fee in the Ley Federal de Derechos.

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
substantiates the 7% delinquency/loss proxy, four loans per year, six-year customer life,
$200 CAC, $40 operating cost or $120,000 fixed-cost budget; those remain planning inputs.

## Changelog
| Date | Change | Why | Approved by |
|---|---|---|---|
| 2026-11-03 | Initial SPEC drafted | Project restarted with corrected unit economics | Najhid + Luciano|
| 2026-11-06 | Flat interest raised from 2% to 4% per month of term; economics table, LTV, payback and break-even recomputed | Every term must recover CAC in the first loan and lower the break-even volume | Najhid + Luciano  |
| 2026-11-11 | Defined loan approval limits: monthly installment <= 30% of declared income and initial credit limit of $6,500 MXN | Approved by Najhid and Luciano to make the MVP approval rule measurable; both values are product-design assumptions, not regulatory requirements | Najhid + Luciano |
| 2026-11-12 | Corrected the six-month affordability example to match the current 4%-per-month-of-term pricing | The previous $467 installment example used an earlier rate; the current $2,500 example is $516.67 per month and requires at least $1,722.24 monthly income | Najhid + Luciano |
| 2026-11-14 | Changed the late-to-default threshold from 30 to more than 45 calendar days past due (more than three quincenas); the installment and associated loan become defaulted | Defines the delinquency rule for the MVP; the 45-day threshold is our design assumption | Najhid + Luciano |
| 2026-11-14 | Rebased unit economics to 7% delinquency-balance proxy, $2,500 ticket, 4 loans/year for 6 years, $200 CAC and $40 operating cost; recalculated term margins, LTV and annual break-even | Replaces the prior 5%/3-loan/CAC $180 assumptions. Under the current 4% pricing, the 6-month contribution is about $415 before CAC, lifetime LTV about $9,960, LTV/CAC about 49.8x and first-year cost-recovery volume about 329 loans; the 7% proxy is not a measured default/loss rate | Najhid + Luciano |
- LGOAAC, official text: https://www.diputados.gob.mx/LeyesBiblio/pdf/LGOAAC.pdf
- Banxico, Circular 21/2009 (CAT): https://www.banxico.org.mx/marco-normativo/normativa-emitida-por-el-banco-de-mexico/circular-21-2009/costo-anual-total-disposicion.html
- Banxico report to Congress, 2026-09-14: https://gaceta.diputados.gob.mx/PDF/66/2026/sep/Banxico-20260914.pdf

| 2026-11-15 | Regulatory notes rewritten after reading LGOAAC arts. 56, 87-B and 87-P and identifying the Banxico CAT circular; effective annual rate shown on the quote screen as a reference figure | Closes review item 5 for the sourced claims; timeline and cost figures remain unverified | Najhid + Luciano |
