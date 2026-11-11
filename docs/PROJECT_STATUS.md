# Equity Atlas — project status and progress record

**Snapshot:** 11 November 2026 (Asia/Kolkata). **Repository:** https://github.com/ashu2526/equity-atlas . **Public site:** https://ashu2526.github.io/equity-atlas/ . These descriptions refer to actual files present at snapshot time; data values are dated, not live recommendations.

## 1. Why the project exists

The original request was a free personal investment-research interface for Yatharth Hospital with a Google Sheet as the editable research ledger. The project expanded into a **reusable sector and market-intelligence platform**: compare multiple listed companies, understand sector profit engines, follow market narratives and global risks, distinguish price leadership from real investor flows, and make research decisions with records of why/when prior opinions changed.

## 2. Completed work by phase

| Phase | Delivered and presently in repository | Key boundary |
|---|---|---|
| Yatharth investment dashboard | `index.html` Yatharth overview, quarterly and valuation/signal/decision views; Google Sheet-backed or embedded fallback; research sources | Not a broker, audited terminal or live quotation service |
| Sector Radar | Hospitals and tyres competitive shortlist, quick research profiles, quality/risk/valuation angles, browser-local deep-dive queue and JSON export | Qualitative research priority, not a buy ranking or complete numerical scoring |
| Sector Intelligence | `sector-intelligence.html`: six views (Thesis, Plays, Metrics, Peers, Scoring, History), industry profit drivers, distinct hospital/tyre operating stories, KPI library, scoring and evidence-led sector context | Some ratings deliberately unscored; editable Sheet must be correctly shared to sync in-browser |
| Macro themes and editorial research | `data/news/editorial.json` with 13 theme maps, 7 curated events, 8 risk registers, 7 watch sectors, sourced method notes | The 11 Nov 2026 baseline ages unless editorially revalidated |
| Daily RSS discovery and ranked news | 15 selected RSS feeds; daily GitHub pipeline archives source headlines and timestamps; transparent keyword headline tone; clusters/ranks source events, keeps scan and topic history | Sampled headlines only, not full-article verified news; one or more feeds may fail |
| Market Intelligence Desk | `market-desk.html`: AI Morning Intelligence, Market-Moving News, Smart-Money Flows, Sector Opportunities, Global Risk, Historical Regime and Data Coverage | Initial AI morning report is provisional, scheduled publication untested |
| Dated institutional-flow evidence | `data/news/flows.json`: 9 sourced/reported observations and 7 official/source registries | Not a continuous all-country cross-asset flow API; prices are kept separate from flows |
| NIFTY rotation | 19 NSE sector indices + NIFTY 50, 82 official NSE daily price files at baseline, 3m/1m/7d returns, relative performance, 30d acceleration, chart histories | **Price movement only**, not capital flows; total-return/dividend adjustment excluded |
| Polymarket global macro monitor | Read-only Gamma API, 400 active events sampled and 80 macro binary contracts selected at baseline; observed YES prices, volume/liquidity, timestamped odds history and basic news links | Contract quotes not calibrated forecasts, odds history initially short and market-to-news matching heuristic |
| Signal Lab UI and navigation | `signals.html` four views: NIFTY Sector Rotation, Polymarket Odds, News × Event Odds, Methodology; link on homepage | 11 Nov nav bug fixed: panel class must be `.sigview`, not `.view` |
| Scheduled automation | Two GitHub Actions workflows for news and market signals; ChatGPT Morning Intelligence task enabled and scheduled for 09:15 IST | GitHub JSON ingestion tested; scheduled ChatGPT-to-GitHub append **not yet proved in a live run** |

## 3. Current site routes

- [Main dashboard](https://ashu2526.github.io/equity-atlas/index.html) — Yatharth research and Sector Radar.
- [Sector Intelligence](https://ashu2526.github.io/equity-atlas/sector-intelligence.html) — sector playbooks, peer research and scoring.
- [Market Intelligence Desk](https://ashu2526.github.io/equity-atlas/market-desk.html) — reviewed morning report, material event feed, dated money flows, risks, sector watch.
- [Regime and News Archive](https://ashu2526.github.io/equity-atlas/news-radar.html) — custom dates, raw headlines, curated source events, theme transmission and history.
- [Sector Rotation × Polymarket](https://ashu2526.github.io/equity-atlas/signals.html) — 3m relative sector trends and event YES quotes.
- `sector.html` — compatibility redirect (not a separate research database).

Static HTML+CSS+JavaScript works with public JSON under GitHub Pages. There is no dedicated backend, SQL database or authenticated user service.

## 4. What was measured at this snapshot (not live quotes)

- `data/market-signals/sector-rotation.json`: `status=ready`, **19 sectors**, **82 NSE daily reports**, observation date 2026-11-11, no missing indices; benchmark `NIFTY 50`.
- `data/market-signals/polymarket.json`: `dataStatus=ready`, **80 selected contracts** out of **400 sampled events**, snapshot 2026-11-11 17:48 UTC, two odds-history snapshots at snapshot time.
- `data/news/editorial.json`: **13** macro themes, **7** manually curated dated events, **8** risk categories, **7** watch candidates.
- `data/news/flows.json`: **9** dated flow/price observations and **7** source registry entries.
- `data/news/daily-briefings.json`: **one initial provisional** AI morning baseline (not a scheduled run).
- `data/news/ai-reviews.json`: **one initial** deep analysis baseline.
- `data/news/scans.json`: **five** recorded automated RSS scan snapshots at inspection.
- Google Sheet: **19 tabs** across company, sector, macro and watchlist workstreams. See Architecture for names.

Counts will change after scheduled jobs. Avoid quoting the snapshot as today's market data.

## 5. Special care around scores and investment use

Scores and priority are not homogeneous. Peer research priority, relative NIFTY sector strength, RSS materiality score, headline tone, editor-reviewed opportunity confidence and Polymarket YES contract prices are **different metrics**. Do not merge them into a single "best sector" number without calibrated, documented and validated factor weights.

A new theme should only be promoted after (i) clear evidence the event happened, (ii) plausible economic transmission into earnings/funding, (iii) measurable market/flow confirmation where available, (iv) alternatives and invalidation, (v) sector/company valuation assessment, and (vi) dated review.

## 6. Important limitations acknowledged by the implementation

1. The daily ChatGPT automation exists and is enabled; its first future execution must be checked for **actual GitHub write-back and Pages propagation**.
2. RSS feeds are not a comprehensive global news database; headline lexicon and news-query count should not be sold as sophisticated AI market sentiment.
3. CDS spread time series and large-company single-name CDS quotes are **not** integrated. US HY OAS is a proxy, not a replacement.
4. Country-by-country funds/institution allocations are mostly a source registry, not a fully connected numeric series.
5. Contract probabilities can be stale, illiquid, manipulated or settlement-dependent.
6. Browser Google Sheet CSV sync may require public read permissions; the published embedded datasets are otherwise the fallback.
7. Frontend regression tests and deterministic data fixtures are still work to do.

## 7. What to do next

See [ROADMAP_AND_QA.md](ROADMAP_AND_QA.md): secure daily AI write-back reliability, actual capital-flow feeds and validation, data quality monitoring, more meaningful news/event linkage, and automated browser tests.
