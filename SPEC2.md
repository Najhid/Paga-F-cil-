[SPEC (1).md](https://github.com/user-attachments/files/34704461/SPEC.1.md)

# SPEC: PagaFácil

Last updated: 2026-11-11 · Owners: Angel Najhid Flores Cartagena + Luciano Yitani Chapa

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
   amount, schedule and the effective annual rate (computed in code; see Unit economics).
3. A simple rule-based check approves or rejects the loan (requested amount within his
   credit limit; installment at most 30% of his declared monthly income).
4. If approved, the app records the payout to the merchant (price minus the 4% merchant
   fee) and creates the installment schedule; León can mark an installment as paid or late
   and see his updated balance.

## Data model (plain words)
User has Loans; Merchant has Loans; each Loan has Installments.
- **User:** name, declared monthly income, credit limit (initial limit $6,500; all invented).
- **Merchant:** name, merchant fee rate (4%).
- **Loan:** user, merchant, price, term in months, merchant fee, funded amount (price minus
  fee), total interest, total to repay, status (approved / active / paid / defaulted).
- **Installment:** loan, number, due date, amount, status (pending / paid / late), paid date.

Pricing rule: flat interest of 4% per month of term on the original price (3 months = 12%,
6 = 24%, 9 = 36%, 12 = 48%). The quote screen must also show the effective annual rate
(about 98% to 116% at this pricing), because a flat "4% per month" looks much cheaper than
it is.

Approval rule: approve the loan only if the requested amount (the price) is at most the
user's credit limit AND the monthly installment is at most 30% of the user's declared
monthly income; otherwise reject. Example: a $2,500 loan over 6 months has an installment
of about $517, so it needs a declared income of at least about $1,722. The 30% cap and the
$6,500 initial limit are our own design assumptions, not a regulatory standard.

Late and default rule: an installment is late when it is unpaid after its due date. A loan
becomes defaulted when any of its installments is more than 30 days past due and still
unpaid. Default is only a status used to measure the 5% default assumption; late fees and
collections stay out of scope. The 30-day threshold is our own design assumption.

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

## Unit economics the model must show
All values are our own assumptions and must be computed from the data model
(`economics.py`), not typed in by hand.

Assumptions: average ticket $2,500 MXN; merchant fee 4%; cost of funds 10% annual; default
rate 5% of loan amount; servicing and credit-check cost $40 per loan; CAC $180; 3 loans per
customer over their university life; year-1 fixed costs about $120,000 (legal and
incorporation, PLD/AML compliance, other; TODO-verify with a fintech lawyer).

Contribution per loan = interest + merchant fee − cost of funds − expected default loss −
servicing cost. Base case is the 6-month plan:

| Term | Total interest | Effective annual rate (approx.) | Contribution per loan |
|---|---|---|---|
| 3 months | 12% | ~98% | ~$193 |
| 6 months | 24% | ~113% | ~$462 |
| 9 months | 36% | ~116% | ~$731 |
| 12 months | 48% | ~116% | ~$1,000 |

- LTV (6-month base) = $462 × 3 loans ≈ $1,390; LTV ÷ CAC ≈ 7.7x.
- Payback: CAC is recovered within the first loan for every term (first loan contributes
  $193 to $1,000 vs CAC $180; the 3-month plan is the tightest case).
- Break-even: about 260 loans per year in the 6-month base case (about 130 customers at 2
  loans per year). Worst case, if every customer chose the 3-month plan: about 620 loans
  per year (about 310 customers at 2 loans per year).
- Open decision: keep or drop the 3-month plan (it now recovers CAC but is still the
  lowest margin).
- Risk: the 5% default rate is an assumption that may rise with higher prices. Sensitivity
  (contribution per loan at 8% / 11.3% / 15% default): 3 months ~$118 / ~$36 / -$57;
  6 months ~$387 / ~$304 / ~$212. The 3-month plan stops recovering CAC above about 5.5%
  default and loses money above about 12.7%; the 6-month plan recovers CAC up to about
  16%. Run this sensitivity in `economics.py`, varying price and default together.
- Effective annual rate: the annual rate at which the present value of the equal monthly
  installments equals the price financed (a monthly IRR compounded to one year), calculated
  in code. Banxico Circular 21/2009 defines the CAT as the annual rate
  that equates the present value of the credit's disbursements and payments (source below).
  Our figure approximates it with monthly periods and no IVA. Label it "effective annual
  rate" in the UI until the exact CAT rules are confirmed. TODO-verify the CAT calculation
  and disclosure rules with Condusef, including whether the Banxico draft changes to the
  CAT published in November 2025 are in force.

Validation status of the assumptions (checked 2026-11-11; all remain our own assumptions):

| Assumption | Value | Status |
|---|---|---|
| Average ticket | $2,500 | Not verified. Validate with a typical start-of-semester cart at the campus bookstore |
| Default rate | 5% of loan amount | Not verified, probably low. Reference, not directly comparable (it measures overdue plus written-off consumer loans over the portfolio): CNBV adjusted delinquency index (IMORA) in June 2026 was 11.31% for consumer credit and 13.70% for credit cards (reported by Expansion) |
| Servicing and credit check | $40 per loan | Not verified. No public price for a lender's bureau query found (only consumer report fees of about $35). Ask Circulo de Credito or Buro de Credito for a quote |
| CAC | $180 | Not verified. Needs a breakdown: referral bonus plus campus advertising, divided by approved customers |
| Loans per customer | 3 | Not verified. Depends on semesters left per student and how often they would buy in installments |
| Year-1 fixed costs | about $120,000 | Not verified. Depends on the regulatory costs below, which have no official source |
| Cost of funds | 10% annual | Reference: 28-day TIIE was 6.5147% on 2026-11-06 (Banxico, DOF). 10% implies a spread of about 3.5 points over TIIE; the spread is our assumption |

## Regulatory notes
Checked on 2026-11-11 against the public pages listed under Sources. Only the search
snippets of these pages were read, not the full legal text, so a fintech lawyer should still
confirm them.

Sourced:
- Vehicle considered: SOFOM E.N.R. The registration is made with CONDUSEF in its registry
  of financial service providers (SIPRES), and the company does not need SHCP authorization
  to be constituted (CONDUSEF).
- Before registering, a new SOFOM E.N.R. must obtain from the CNBV a technical opinion
  (dictamen tecnico) on its AML/PLD program (CNBV FAQ for SOFOM E.N.R.).
- The CNBV supervises a SOFOM E.N.R. only for AML/PLD, under articles 56 and 95 Bis of the
  LGOAAC (CONDUSEF and gob.mx publications on SOFOM E.N.R.).

Not verified (no official source found; these stay as assumptions, TODO-verify with a
fintech lawyer):
- Registration timeline (3 to 4 months) and cost range ($40,000 to $80,000 MXN).
- AML/PLD compliance cost ($20,000 to $40,000 MXN per year).

## Sources (checked 2026-11-11)
- CONDUSEF, SIPRES: https://webapps.condusef.gob.mx/SIPRES/jsp/index.jsp
- CONDUSEF, Sofomes booklet: https://www.condusef.gob.mx/documentos/111134_CUADERNOSYVIDEOS-SOFOMES.pdf
- gob.mx, Sofomes No Reguladas: https://www.gob.mx/cms/uploads/attachment/file/109296/Sofomes_No_Reguladas.pdf
- CNBV, FAQ SOFOM E.N.R.: https://www.cnbv.gob.mx/PrevencionDeLavadoDeDinero/Preguntas-Frecuentes/Paginas/PF-Sofomes.aspx
- Banxico, Circular 21/2009 (CAT), DOF 2009-09-04: https://dof.gob.mx/nota_detalle.php?codigo=5108217&fecha=04/09/2009
- Banxico, TIIE of 2026-11-06 (DOF): https://sidof.segob.gob.mx/notas/docFuente/5803287
- Expansion, 2026-08-27, delinquency (CNBV IMORA): https://expansion.mx/economia/2026/08/27/mexicanos-gastaron-mundial-tarjeta-morosidad

## Changelog
| Date | Change | Why | Approved by |
|---|---|---|---|
| 2026-11-03 | Initial SPEC drafted | Project restarted with corrected unit economics | Najhid + Luciano|
| 2026-11-06 | Flat interest raised from 2% to 4% per month of term; economics table, LTV, payback and break-even recomputed | Every term must recover CAC in the first loan and lower the break-even volume | Najhid + Luciano  |
| 2026-11-11 | Approval rule made concrete: installment at most 30% of declared monthly income; initial credit limit $6,500 | The code agent cannot implement the credit check without numbers; both values are design assumptions | Pending |
| 2026-11-11 | Default rule (30 days past due), effective annual rate shown on the quote screen, regulatory notes split into sourced and not verified, validation status of the unit economics assumptions, default sensitivity | Close review items 3 to 6 | Pending |
