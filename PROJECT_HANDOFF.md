# PagaFacil Project Handoff

**Prepared:** 2026-11-20  
**For:** Luciano  
**Repository:** `Najhid/Paga-F-cil-`  
**Purpose:** Continue the financial-model and evidence work from VS Code without treating unsupported assumptions as verified facts.

## 1. Current status

PagaFacil is an academic BNPL prototype for a fintech partnered with a bank. The prototype simulates checkout, merchant payout records and installment tracking. It does not establish which party lends, owns or funds the receivable, receives interest, bears losses, or pays PagaFacil.

The previous `deployment-docs` pull request, [#17](https://github.com/Najhid/Paga-F-cil-/pull/17), is already merged. The current workbook, documentation and tests contain additional uncommitted changes. They need a new pull request to `main`; do not reopen #17.

The financial workbook now separates:

- **Portfolio scenarios:** modeled borrower interest, merchant fee, funding sensitivity, loss proxy and servicing assumption before bank settlement.
- **PagaFacil company economics:** calculated only from the bank-partner compensation and cost allocations in `Bank Partner Economics`.

The company P&L, EBITDA, company break-even and valuation are intentionally pending. Empty contract fields mean unknown, not zero. Enter `0` only when the executed agreement or written evidence confirms there is no charge or allocation.

## 2. Work completed in this change set

| File | Work completed |
|---|---|
| `PagaFacil_Financial_Model.xlsx` | Added `Bank Partner Economics` and `Funding Benchmarks`; connected PagaFacil P&L revenue, variable cost, partner/legal costs, contribution, EBITDA and status to explicit contract inputs; left outputs pending where required inputs are absent; documented every formula. |
| `src/tests/test_financial_model.py` | Updated workbook expectations and added a populated-input case that checks the contract-linked company P&L. |
| `SPEC.md` | Clarified the bank-partner model, portfolio-versus-company economics, market evidence, competitor limitations and evidence gaps. Removed a DPL News URL that redirected to an unrelated story. |
| `README.md` | Explained which outputs remain pending and how to interpret the bank-partner workbook inputs. |
| `DECISIONS.md` | Recorded the current bank-partner model and evidence-gated company P&L as the latest decisions; earlier items remain historical. |
| `BITACORA.md` | Recorded the work and validation status. |

Validation completed: `python -m pytest -q` returned **70 passed**; `git diff --check` returned no errors. Workbook formula tests evaluate formulas in memory. Open the workbook in Excel and refresh calculations to update displayed cached values.

### A local edit to review separately

`src/pricing.py` has a pre-existing, unstaged edit that removes an inline `TODO-verify` and clarifies that the displayed rate is an effective annual rate, not CAT. It is not included in the handoff change set. Luciano should review the wording and related tests, then decide whether to commit that edit separately. Do not silently discard it.

## 3. Evidence and numbers to preserve

### Enrollment and interviews

- Data Mexico reports **14,693 students for Universidad Panamericana overall in 2022**. It is not a current UP CDMX count.
- The **6,763** figure is associated with Zacatecas / Benito Juarez in the cited profile, not verified as UP CDMX enrollment.
- No current official UP CDMX population figure was confirmed in the sources used. Do not present 14,693 or 6,763 as UP CDMX population, TAM, eligible borrowers or demand.
- The project has **25 real questionnaires**: 13 Finance and 12 Law students, all in semesters 3 to 5. This is a convenience sample, not a representative demand estimate.
- Survey results recorded in the project: 48% reported no own formal credit history; 88% accepted a Buró consultation; 76% accepted interest if total cost was transparent; 92% preferred 3- or 6-month terms; 88% preferred SPEI or automatic debit. Preserve the wording and denominator when reporting these percentages.

### Ticket, pricing and portfolio example

- **MXN 2,500** is the central planning ticket. **MXN 2,500 to 4,000** is a design and sensitivity range, not a measured average or merchant-sales statistic.
- Pricing is flat interest of 4% of original ticket per month of term. For MXN 2,500 over six months: interest is MXN 600, total repayment is MXN 3,100, and the equal installment is about MXN 516.67.
- The merchant fee is 4% of the purchase. At MXN 2,500, the simulated merchant payout is MXN 2,400.
- The app should call the displayed rate an **effective annual rate**, not CAT, until the calculation and disclosure requirements are verified.

At MXN 2,500 for six months, the workbook's portfolio scenario computes:

| Item | MXN |
|---|---:|
| Borrower interest | 600 |
| Merchant fee | 100 |
| Funding cost at the 10% planning assumption | 70 |
| Simplified full-loss proxy at 7% of ticket | 175 |
| Servicing assumption | 40 |
| Portfolio contribution before CAC and bank settlement | 415 |

The MXN 415 is **not PagaFacil company contribution or profit**. The contract may assign interest, merchant fee, funding cost, losses, servicing and settlement differently.

### External context and competitor limits

- Banxico references recorded for 2026-11-19: CETES 28-day 6.19%, TIIE de fondeo one day 6.26%, and TIIE 28-day 6.5147%. These are market reference rates, not a bank quote or PagaFacil cost of funds. The 10% scenario is a planning sensitivity, not an observed spread.
- ENIGH 2024 and ENSAFI 2023 figures in `SPEC.md` are national household/adult context. They are not student income, ticket, affordability, default or demand data.
- Kueski remains a product/market competitor. Public Kueski personal-loan terms are not automatically Kueski Pay checkout terms; borrower APR/CAT does not reveal Kueski's funding cost or losses.
- Aplazo merchant offers vary by store. A store-specific no-customer-commission plan does not prove there is no merchant fee.
- The reported 2.9%-3.5% bank consumer IMOR range was excluded because the supplied material did not identify a precise CNBV table, portfolio definition and observation date.

See the source list and qualifications in `SPEC.md`; recheck date-sensitive pages before making new claims.

## 4. Inputs and evidence still missing

### Bank agreement and settlement

The `Bank Partner Economics` sheet expects eight monetary inputs in `B5:B12`. They must come from the executed agreement or written quotes, not from market averages:

1. PagaFacil gross contracted compensation per funded loan.
2. Funding cost passed through to PagaFacil per funded loan.
3. Credit-loss or first-loss allocation to PagaFacil per loan.
4. PagaFacil servicing, credit-check and payout cost per funded loan.
5. Bank setup and settlement fees for Year 1.
6. Bank recurring fees for Years 2 to 5.
7. PagaFacil legal and compliance costs for Year 1.
8. PagaFacil recurring legal and compliance costs for Years 2 to 5.

Also document the contractual answers in the sheet: lender of record, owner of the receivable, party supplying principal and merchant settlement, party receiving borrower interest and merchant fee, party bearing fraud/charge-offs/recoveries, and the settlement waterfall, timing, reserves and reconciliation.

**Questions for the bank partner and Luciano**

- Who is named as creditor in the borrower agreement, and who books/owns the receivable?
- Who provides loan principal and pays the merchant? What is the settlement timing?
- Who receives borrower interest and the merchant fee? What exact formula determines PagaFacil compensation?
- Which party bears funding charges, fraud, defaults, recoveries and any first-loss exposure?
- What setup, per-loan, recurring, reserve, reconciliation or settlement charges apply? Are taxes or minimum-volume commitments specified?
- Who performs servicing, payment-status handling, complaints and any credit or identity checks? What is the price per event or funded loan?
- Which legal, privacy, compliance and reporting responsibilities are assigned to each party? Ask qualified counsel to confirm obligations; do not infer them from the partner's role or another lender's status.
- Are fees withheld from merchant payout, netted from collections, invoiced separately or settled another way?

### Operating and market evidence

| Missing evidence | Best evidence to obtain | Why it matters |
|---|---|---|
| Current UP CDMX enrollment and eligible population | Official UP student/campus record with year, campus and denominator; if unavailable, keep the limitation explicit | Prevents use of university-wide or unrelated-campus counts as a campus market size. |
| Actual purchase distribution | Anonymized bookstore/merchant transaction file with dates, ticket amounts, count and frequency | Tests the MXN 2,500 central ticket and MXN 2,500-4,000 range. |
| Merchant fee | Written merchant quote or agreement | Confirms whether the 4% merchant fee is feasible and who pays it. |
| Survey audit trail | Original questionnaire, exact question wording, anonymized responses and denominator per question | Makes percentages reproducible and helps identify missing responses or ambiguous questions. |
| Customer acquisition cost | Documented campaign spend divided by funded customers, with period and channel | Replaces the MXN 200 planning assumption. |
| Per-loan servicing costs | Written provider quotes plus internal time/cost by activity | Replaces the MXN 40 portfolio assumption and determines PagaFacil's allocation. |
| Credit performance | Anonymized loan-level vintages with balance, days past due, cures, charge-offs, recoveries and observation window | Needed to estimate PD, LGD and EAD; the 7% proxy is not a measured default/loss rate. |
| Repeat use | Anonymized account-level funded-loan counts and time between loans | Tests the one-loan-per-year, four-year lifetime assumption. |
| Fixed legal/compliance and partner costs | Written quotes and executed agreement, with scope, year, renewal and responsible party | Completes company operating costs without reusing SOFOM-specific estimates. |

## 5. Active TODOs versus historical TODO notes

### Active items to resolve before presenting a CAT or company forecast as complete

1. **CAT method and disclosure:** `SPEC.md` retains `TODO-verify` for whether the effective annual calculation and user-facing disclosure meet the applicable CAT requirements. Keep the screen label as effective annual rate until confirmed against current primary rules and qualified advice.
2. **Applicable obligations in the bank-partner model:** `SPEC.md` retains `TODO-verify` asking counsel which obligations apply to PagaFacil under the actual operating and contractual arrangement. The prototype does not resolve legal roles.
3. **Possible rule changes:** verify the final status and text of any Circular 21/2009 changes before describing the screen value as CAT.
4. **Bank-partner allocations and quotes:** all company economics listed above remain missing until supported by contract or written quotes.
5. **Current campus and merchant evidence:** do not fill the UP CDMX population or ticket distribution with an estimate presented as observed data.

### Historical notes that are not active TODOs

- The selected `TODO` in the older `BITACORA.md` entry about the initial README skeleton records that run commands were TODO at that time. The README now has run instructions; the log is historical and should not be rewritten.
- Older entries in `DECISIONS.md` and the `SPEC.md` changelog mention the 2% rate, SOFOM structure, proposed SOFOM fee, 60/40 funding split, 16,500 student estimate and older valuation assumptions. They are historical and superseded by later entries. Do not copy those numbers into the active model.
- The old SOFOM technical-opinion fee and SOFOM-specific legal/compliance estimates are not PagaFacil bank-partner costs. Use them only if counsel confirms applicability to a defined structure.

## 6. Recommended next steps for Luciano

1. In VS Code, fetch `origin` and check out the new handoff branch. Confirm the branch is based on the latest `main` and review the pull request diff before merging.
2. Run `python -m pytest -q` from the repository root and confirm all 70 tests pass. Run `git diff --check`.
3. Open `PagaFacil_Financial_Model.xlsx`. Review `Bank Partner Economics`, `Funding Benchmarks`, `P&L`, `Unit Economics` and `Valuation`. Do not replace blank contract fields with zero or benchmark rates.
4. Review the uncommitted `src/pricing.py` edit separately. Confirm the UI and tests consistently describe the figure as effective annual rate, not CAT.
5. Ask the bank partner the questions in Section 4. Record answers only from the executed contract or written confirmation.
6. Ask the team to provide the original questionnaire/export, transaction data and any official UP campus figure. Preserve definitions, dates and denominators.
7. Update assumptions only after evidence is obtained. Recalculate affected outputs and tests; do not silently overwrite the planning scenario.
8. Have both partners review the final bank allocations, open TODOs and source dates. Then merge the new pull request into `main`.

## 7. VS Code commands

From the repository root:

```sh
git fetch origin
git switch bank-partner-economics-handoff
git pull --ff-only origin bank-partner-economics-handoff
python -m pytest -q
git diff --check
```

If GitHub has not yet created the branch or pull request, use the repository's Pull Requests view to open a new pull request from `bank-partner-economics-handoff` to `main`. The old PR #17 is already merged.

Do not open, copy, or share `.env` or credential files. No credentials or real personal data are needed for this handoff.
