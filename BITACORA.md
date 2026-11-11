Bitacora: PagaFácil

One entry per work session. Three lines is enough. This is graded at every entrega and it is your audit trail for the live defense.

Template:

2026-11-03 · Najhid and Luciano
Goal: <what we set out to do>
AI did: <what the agent generated or changed, which tool and model>
We decided: <what we accepted, rejected or changed, and why>
Reviewer flags: <what the reviewer report raised, and what we did about it>
2026-11-03 · Najhid + Luciano
Goal: restart the project with a clean structure: fix the unit economics and write the SPEC and AGENTS files for PagaFácil (BNPL for university students).
AI did: Claude (claude.ai, agent mode an Copilot agent mode) reviewed our deck and the course templates, found inconsistencies in the numbers (payback, ARPU, flat 2% monthly rate), recomputed effective annual rates and contribution per loan, and drafted SPEC.md and AGENTS.md. Copilot suggested the commit message for the SPEC.
We decided: kept the BNPL idea and León Lara as the user; accepted the new assumptions (ticket $2,500, 4% merchant fee, 10% cost of funds, 5% default, $40 servicing, CAC $180, 3 loans per customer); pasted the SPEC directly in GitHub because we could not make the change from VS Code yet; the 3-month plan is still an open decision (almost no margin).
Reviewer flags: none yet, the reviewer is not set up. Regulatory figures in SPEC are marked TODO-verify.

## 2026-11-05 · Najhid + Luciano
- Goal: finish the project's context and configuration files before writing any code (DECISIONS, README skeleton, .gitignore, VS Code settings, reviewer agent).
- AI did: Claude Sonnet 5.5 and Copilot (claude.ai chat, agent mode) drafted DECISIONS.md, a README.md skeleton with the run commands left as TODO because no code exists yet, and a .gitignore that keeps .env out of the repo. It adapted the course templates for .vscode/settings.json (added python3 commands for Mac) and for the reviewer agent (.github/agents/reviewer.agent.md), and walked us through uploading files to GitHub with a branch and a pull request.
- We decided: to add the files through pull requests so both partners approve; Luciano reviewed and approved them today and the files are now in the repo. We will review the open points one by one next (3-month plan, maximum installment-to-income share, CAT disclosure, reviewer file path, the professor's eight rules, and the approval row in SPEC.md).
- Reviewer flags: none, the reviewer has not run yet because there is no code to review.
- Correction to the 2026-11-03 entry: the chat tool was Claude Sonnet 5.5.

## 2026-11-10 · Najhid + Luciano
- Goal: close the repo and tooling items from our review checklist (file names, VS Code settings, reviewer agent) so the project is ready to start building.
- AI did: Claude Sonnet 5.5 guided us step by step: it spotted wrongly named files (Agent.md, Decisions.md, Reviewer.Agent without .md and outside .github/agents/), an unclosed brace in .vscode/settings.json, and reviewer tool names that no longer exist in our VS Code version (codebase, search, changes, findTestFiles); it suggested replacing them with read-only tools (view, grep, glob, rg). GitHub Copilot Code Review commented on settings.json, and Copilot Chat in VS Code (model selector showed "Copilot Fusion, Standard") helped us check the reviewer agent file. The reviewer agent itself ran for the first time on settings.json.
- We decided: renamed the files to AGENTS.md, DECISIONS.md and .github/agents/reviewer.agent.md; closed the missing brace in settings.json; replaced the reviewer's tools with read-only ones, so it still cannot edit files or run commands; applied Copilot's comment that explains "dial position 2 and 3", and did not apply the one that explains how to enable approve-everything, because course policy keeps that OFF on our laptops. Changes go through pull request for Luciano's approval.
- Reviewer flags: the reviewer returned STOP AND TALK because it had no diff to compare, and raised three findings on settings.json: (1) cat and Get-Content were auto-approved and could read .env, against AGENTS.md rule 5; (2) git add, commit, branch and checkout were auto-approved; (3) npm and pnpm test commands were auto-approved. We removed type, cat and Get-Content from the auto-approve list, removed checkout (kept add, commit, branch and restore --staged), and deleted the npm/pnpm line because the project uses Python (pytest stays auto-approved). Open limit: these settings only control terminal commands, so keeping the agent away from .env also depends on the rule in AGENTS.md.

## 2026-11-11 · Najhid + Luciano
- Goal: review the five repo documents for consistency and fix their formatting before we start coding.
- AI did: Claude Sonnet 5.5 and Copilot compared SPEC, DECISIONS, AGENTS, README and BITACORA against each other. It found that four files had lost their Markdown formatting when pasted, a stray upload link on the first line of SPEC.md, and DECISIONS.md still showing the 2% pricing after the SPEC moved to 4%. It recomputed the SPEC's 4% table (matches within about 1%). It regenerated AGENTS.md, DECISIONS.md and README.md with formatting restored, added the professors' working-style rules to AGENTS.md (professional context rewritten for our project) and drafted two DECISIONS lines for the 4% pricing.
- We decided: replaced the three files through a pull request and removed the stray link from SPEC.md; the old 2% line stays in DECISIONS.md because the log is append-only, and the new lines supersede it.
- Reviewer flags: reviewer not run on this change (documentation only). Claude flagged that the 4% price was chosen so every term recovers CAC, and that the 5% default assumption may be too low at about 113% effective annual rate; the sensitivity test in economics.py should vary price and default together. Numeric items stay with Luciano.
- Still open: approval rule (maximum installment share and credit limit), CAT disclosure, regulatory TODO-verify items.
