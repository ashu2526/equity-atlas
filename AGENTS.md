# Equity Atlas — agent / maintainer entry point

**Read before changing this repository.** Current project documentation and reusable skill live at:

- [.agents/skills/equity-atlas/SKILL.md](.agents/skills/equity-atlas/SKILL.md): project-specific agent skill and safe development workflow
- [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md): features, completed work and what is NOT yet complete
- [docs/ARCHITECTURE_AND_DATA.md](docs/ARCHITECTURE_AND_DATA.md): pages, pipelines, Google Sheet, storage contracts
- [docs/METHODOLOGY_AND_GUARDRAILS.md](docs/METHODOLOGY_AND_GUARDRAILS.md): precise formulae and evidence tiers
- [docs/OPERATIONS_RUNBOOK.md](docs/OPERATIONS_RUNBOOK.md): operating, publishing, troubleshooting, restoring
- [docs/ROADMAP_AND_QA.md](docs/ROADMAP_AND_QA.md): testing checklist, known defects and future priorities
- [docs/ASSET_INVENTORY.md](docs/ASSET_INVENTORY.md): snapshot/package guidance

The public site is https://ashu2526.github.io/equity-atlas/ and main branch source is https://github.com/ashu2526/equity-atlas .

## Non-negotiable project rules
1. **Money flows are not momentum.** NSE NIFTY sector index returns are PRICE returns. Do not label them as flows, FPI purchases or "smart-money" allocations.
2. **A Polymarket YES price is a contract quote, not objective probability; Polymarket volume is betting-market volume, not equity investment.** The integration is read-only.
3. **Headline tone is not actual market sentiment.** RSS titles and topic clustering are statistical signals; deeper interpretation must be AI-reviewed, dated, attributable and cross-checked.
4. **Never invent CDS prices, capital flows, analyst revisions, company earnings or market prices.** Missing observations remain null/unavailable.
5. **Preserve historical snapshots and prior AI reviews.** Do not erase prior assessments when a narrative changes. Every research item needs an observation/review date.
6. **Protect public GitHub.** Do not upload financial holdings, email addresses, secrets, credentials, private Google Sheet exports or personal information.
7. **Verify every browser tab actually changes the content.** Matching sidebar highlight is insufficient; a prior bug used `.view` instead of `.sigview` in `signals.html`.

## Editing approach
Read source and JSON schemas first, edit the minimal necessary files, run syntax/data validation, publish to GitHub and verify GitHub Pages deployment. If a scheduled AI action has not run successfully, do not say its GitHub write-back is proven.

Updated: 2026-11-11. This is an agent guidance file, not an installed ChatGPT system skill.
