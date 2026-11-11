---
name: equity-atlas
description: Maintain and extend the Equity Atlas Indian-equity, sector-rotation and global market-intelligence research platform. Use for website updates, data sourcing, risk/event monitoring, company/sector research, daily AI briefs and research handoffs.
---

# Equity Atlas project skill (maintainer edition)

Use this repository-local skill for work on `ashu2526/equity-atlas`. It is **version-controlled instructions for coding/research agents**, not a claim that a ChatGPT account-level skill was installed or modified.

## Project goals

Provide a public, free-to-read investment-research website that shows:
- Company-level fundamental analysis, valuation scenarios and decision history (first case: Yatharth Hospital).
- Sector-specific economics, competitors, KPIs, playbooks and evidence-gated opportunity ranking.
- Source-linked daily macro/market news, AI-reviewed briefing, transparent headline climate and historical regime assessments.
- Actual dated institutional-flow observations with provenance and data-quality distinctions.
- Three-month NSE NIFTY sector price leadership and momentum vs NIFTY 50.
- Relevant global prediction-market YES contracts with precise terms, liquidity, source and historical quote changes.

Do **not** turn the site into a headline-count leaderboard pretending to predict returns or a flow terminal inventing subscriptions/positions.

## First files to read

1. `AGENTS.md`, `docs/PROJECT_STATUS.md`, `docs/ARCHITECTURE_AND_DATA.md`.
2. `docs/METHODOLOGY_AND_GUARDRAILS.md` before touching calculations, financial reporting, scoring or prediction markets.
3. `docs/OPERATIONS_RUNBOOK.md` before touching GitHub Actions, ChatGPT schedules or publishing.
4. `docs/ROADMAP_AND_QA.md` before user-interface changes.
5. Live code and data, especially `signals.html`, `market-desk.html`, `scripts/`, `data/news/`, `data/market-signals/`.

## Implementation map

| Need | Code / data / page |
|---|---|
| Main Yatharth research + Sector Radar | `index.html`, `sector.html` redirect |
| Sector playbooks + company research priority | `sector-intelligence.html`, published embedded fallback, Google Sheet |
| AI briefing / money-flow ledger / ranked event feed | `market-desk.html`, `data/news/daily-briefings.json`, `flows.json`, `ranked-feed.json` |
| Raw news, source review, time-window comparison | `news-radar.html`, `data/news/*` |
| NSE sector returns and Polymarket event research | `signals.html`, `data/market-signals/*` |
| News ingest/rank/lexical index | `scripts/rss_scan.py`, `build_intelligence_feed.py`, `build_regime_pulse.py` |
| NSE and Polymarket feeds | `scripts/sector_rotation.py`, `polymarket_monitor.py` |
| Automation | `.github/workflows/news-radar.yml`, `market-signals.yml`; separate ChatGPT automation |

## Required development loop

1. **Inspect** the main-branch file and actual dataset before proposing a change. Source files can change between conversations. Avoid using an earlier local `index.html` copy.
2. **Ground** all numerical facts in date/unit/source and distinguish primary releases from secondary reporting. If sources conflict, surface the conflict.
3. **Preserve schema/history**: prefer append or upsert by stable ID/date. Do not reset news, odds, snapshots or reviewed reports. Keep `data/news/editorial.json` dated rather than silently renewing its authority.
4. **Handle partial failure**: API rate limits, blocked feed, missing NSE archive, expired contract, unsupported Google Sheet public CSV access must produce an honest visible coverage state and retain last good data.
5. **Use read-only APIs** for Polymarket. Never connect a wallet, call order endpoints, or assume contract price/volume predicts an equity market move.
6. **Validate UI**: parse embedded scripts, ensure all `document.querySelector` targets exist, verify all nav `data-view` values correspond to actual panels and **test changing between tabs**, selectors, search, cards and hash deep links in a browser if available.
7. **Validate Python/JSON**: compile scripts, parse every JSON, check cross-file fields, sanity-check ranges and source dates (no fabricated returns/odds).
8. **Publish** changes and check a successful Pages Actions deployment for the latest relevant SHA. Never promise untested end-to-end scheduled AI publication.
9. **Document** behaviour changes in the relevant `docs/*.md` plus README changelog. Keep this skill aligned with reality.

## Research-assessment contract

For each substantive AI market briefing report: timestamp, session, observed news/evidence, *why* economics shift, first-order affected sectors, second-order proxies, what actual institutional data show, alternative explanations, contradiction, falsification/confirmation tests, risk catalysts, confidence and exact sources.

For each sector evaluation: distinguish industry attractiveness, company quality, valuation, market cycle and research priority. No unsupported numerical scores. For price momentum use 7/30/91-calendar-day comparison closes and show sample staleness. Polymarket estimates must cite contract question and market timestamp.

For forecasts: distinguish management guidance, sell-side estimates, scenario assumptions, and observed fundamentals. No buy calls without valuation/risks; education/research framing.

## Source priorities

- NSE index close historical files; NSE reported provisional daily FII/DII cash market data.
- NSDL fortnightly sector-wise FPI flows (different time unit/population).
- AMFI monthly domestic fund subscription/redemptions; RBI and relevant national central banks.
- US Treasury TIC, CFTC COT and credit-stress references; source/licensing limits apply.
- Official company exchange filings, investor decks, audited statements and primary policy publications.
- Publisher/institution RSS for headline discovery, **not full-article fact checking**.
- Polymarket official unauthenticated Gamma API / official reference docs for read-only YES quotes.
- Google Sheets for editable sector/quarterly curation; public repo JSON as the published snapshots.

## Most important unfinished areas

- First live automatic ChatGPT morning brief **write-back** has not been end-to-end verified as of 2026-11-11; scheduled for 2026-11-12 09:15 IST.
- Institutional capital flows need systematic authenticated numeric source connectors and international flow coverage.
- News feed remains selected RSS titles; no exhaustive full-text global event verification.
- CDS issuer / sovereign price feed, cross-asset risk regime and consensus earnings revisions are not integrated.
- Some screens still depend on embedded fallback data, and Google Sheets public CSV permissions may block browser sync.
- Market and Polymarket signals need a more rigorous event matching / causal verification layer.
- Automated regression/browser testing is limited; last Signal Lab bug was fixed on 2026-11-11.

See `docs/ROADMAP_AND_QA.md` for prioritized work.


## Updated working design and automation contract (12 November 2026)

Before building new pages, read root DESIGN.md and docs/REFRESH_AND_TECHNICAL.md. The site has a unified RESEARCH / MARKETS navigation with six sections: Company Research, Sector Intelligence, Price × Volume, Morning Intelligence, Rotation × Odds, and News Archive.

Use assets/equity-ui.css semantic tokens and assets/equity-shell.js navigation; do not reimplement each page header with incompatible links. The default appearance is restrained dark and the optional user-local Paper mode is intended for readability. No external fonts, charting framework or dependency-heavy frontend. Future companies should use data-driven research templates.

Update markets and source data at 07:00 and 19:00 IST through existing GitHub Actions; source-verified AI interpretation follows at about 07:25 and 19:25. A separate monthly task reviews valuation theses and filings. Never assert a future AI write has succeeded without verifying the committed report, as-of timestamp and Pages deployment.

Stock technical engine: scripts/stock_price_volume.py consumes data/market-signals/watch-universe.json, uses a labelled free NSE-derived source with labelled Yahoo fallback, and emits stock-price-volume.json plus price-volume-history.json. It computes price relative to 20/50/200 SMAs, 20/55-session high/low, 20-session relative share volume, CMF20, OBV proxy, RSI14 and watch alerts for abnormal-volume breaks and short/long trend conflict. All signals require corroboration by actual disclosed corporate data and valuation. Stale or split-affected data must not produce current alerts. New company dashboard is company-signals.html, which links to fundamentals and sector analysis.

Quality-gate workflow runs scripts/validate_site.py across source JSON, website tab IDs, JS parsing and active cron; always inspect workflow results after edits.
