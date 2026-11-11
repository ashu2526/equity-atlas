# System architecture, data contracts and information flow

**As of:** 2026-11-11. This is a **static GitHub Pages website** with scheduled GitHub Actions and versioned JSON. Google Sheets is a separate editable research source. A ChatGPT automation is external to GitHub.

## Architecture sketch

```text
Selected publisher and official RSS feeds
  -> scripts/rss_scan.py
  -> data/news/articles.json + scans.json
  -> scripts/build_regime_pulse.py
  -> market-pulse.json + pulse-history.json
  -> scripts/build_intelligence_feed.py
  -> ranked-feed.json + ranked-feed-history.json
  -> market-desk.html and news-radar.html

NSE daily all-index close CSV (~120-day window)
  -> scripts/sector_rotation.py
  -> data/market-signals/index-history.json + sector-rotation.json
  -> signals.html

Polymarket public Gamma events (top activity, read-only)
  -> scripts/polymarket_monitor.py
  -> data/market-signals/polymarket.json + polymarket-history.json
  -> signals.html

Research analyst / ChatGPT scheduled agent
  <- news JSON, flow ledger, market signals, external verified sources
  -> data/news/daily-briefings.json (append-only, dated)
  -> sometimes data/news/ai-reviews.json (fortnightly review)
  -> optionally data/news/flows.json (verified updates only)
  -> market-desk.html / news-radar.html

Google Sheets (editable sector/quarterly research)
  -> public Google gviz CSV browser fetch where permitted
  -> index.html and sector-intelligence.html
  -> embedded HTML fallback otherwise
  -> separately curated published data/news/editorial.json (not live Sheet export)

GitHub main -> Pages deployment -> public HTML and JSON.
```

## Website and UI ownership

| File | Views / purpose | Data |
|---|---|---|
| `index.html` | Overview, Sector Radar, Financials, Valuation, Signals, History, Sources | Embedded company baseline, `db`, Google Sheet CSV when readable; some headline widgets from `data/news` |
| `sector-intelligence.html` | Thesis, Plays, Metrics, Peers, Scoring, History | Embedded `research-db` fallback + browser `gviz/tq?out:csv&sheet=...` for sector Sheet tabs |
| `market-desk.html` | Morning Intelligence, ranked News, Smart-Money Flows, Sectors, Risks, Archive, Coverage | `data/news/daily-briefings.json`, `ranked-feed.json`, `flows.json`, `market-pulse.json`, `editorial.json`, `articles.json`, `scans.json`, `ai-reviews.json`, `pulse-history.json` |
| `news-radar.html` | Regime Pulse, Themes, News, Global Risk/CDS, AI reviews, Change Detector, Methodology | Public `data/news/*.json` with raw.githubusercontent fallback |
| `signals.html` | Sector Rotation, Polymarket Odds, News × Event Odds, Methodology | `data/market-signals/sector-rotation.json`, `polymarket.json`, `polymarket-history.json`; source-linked `data/news/ranked-feed.json` |
| `sector.html` | Legacy redirect | Links to Sector Radar in `index.html` |

All code is currently authored as single-file static page markup + inline scripts, without a JS build system/package manager.

### Critical navigation regression case

Signal Lab has `<section class="sigview" id="sector|odds|joined|method">`. The click handler MUST toggle `$$(".sigview")`, not `$$(".view")`. If it targets the wrong class, the sidebar changes highlighting but content remains unchanged. This bug was fixed and the GitHub Pages deployment verified on 2026-11-11. Regression-test the entire click sequence, not just CSS state.

## News data contracts

| JSON | Producer / writer | Primary fields and meaning |
|---|---|---|
| `config.json` | Maintainer / editorial | `feeds[]` (15 publisher/institution RSS URLs), `topics[]` (16 macro tags and legacy GDELT queries), retention/limits/matching metadata |
| `articles.json` | `rss_scan.py` | `articles[]` with stable link hash, title, URL, publisher domain, published/discovered timestamps, topic tags, crude headline-tone label. Up to 6,000 entries and 120-day retention. A source headline is **unverified** |
| `scans.json` | `rss_scan.py` | `scans[]`: UTC scan time, per-feed success/errors, new count, retained count, coverage warnings, feed count. Up to 120 latest runs |
| `market-pulse.json` | `build_regime_pulse.py` | 14-day headline language/index, publisher balance, topic attention and news-only risk categories, data sufficiency |
| `pulse-history.json` | `build_regime_pulse.py` | One per date, up to 180 daily headline-climate snapshots |
| `ranked-feed.json` | `build_intelligence_feed.py` | Up to 80 clustered/ranked RSS title events with score, sources, topic/geo tags and editorial economic transmission hypotheses |
| `ranked-feed-history.json` | `build_intelligence_feed.py` | One daily summary of ranked source event coverage, up to 365 |
| `editorial.json` | Research/Google Sheet curated copy | `themes[]`, `events[]`, `riskWatch[]`, `methodology[]`, `watchCandidates[]`. Baseline dated 11 Nov 2026, NOT live synchronized |
| `flows.json` | Analyst/ChatGPT only after verifying dated figures | Observations with geography, periodStart/end, frequency, unit, value, data tier, source and official registry; 7 monitoring sources; null value when unverified |
| `daily-briefings.json` | ChatGPT interactive baseline + scheduled agent intended | `briefs[]` newest first: full date/author/status, executive summary, `regime`, `stories[]`, `keyNumbers`, `watchNow`, `cooling`, `risks`, `whatChanged`, sources |
| `ai-reviews.json` | ChatGPT deeper research | `reviews[]` archived dated regime audits/sector hypotheses, 11 Nov baseline; scheduled future append intended |

**Do not conflate** `daily-briefings.json` (reviewed interpretation) with `market-pulse.json` (algorithmic headline lexicon), or `ranked-feed.json` (automated title triage).

## Market signals data contracts

| JSON | Producer | Notes |
|---|---|---|
| `index-history.json` | NSE collector | Official daily all-index close values, any separately tagged Yahoo mirror series, prior days retained for continuity |
| `sector-rotation.json` | NSE collector | `status`, `asOf`, benchmark NIFTY 50, `benchmarkPath[]`, `sectors[]`, explicit source and missing indices; per sector `r7d`, `r1m`, `rPrev1m`, `r3m`, `relative3mPp`, `relative1mPp`, `momentumAccelerationPp`, `rotationState`, price path, rank |
| `polymarket.json` | Gamma read-only collector | `markets[]`: exact binary YES question, contract/event IDs, event URL, YES quote, impliedYesPercent, 24h/total volume, liquidity, latest UTC snapshot, change vs prior successful snapshot, category/exposures; `dataStatus` and fetch errors |
| `polymarket-history.json` | Gamma read-only collector | `snapshots[]`, UTC time and observed per-market quotes for ~180 snapshots. Initial 2 snapshots, inadequate for long trends |

`sector-rotation.json` is a *price-return* product. `polymarket.json` is a *prediction-contract market price* product. Neither measures institutional stock purchases.

## Google Sheets (editable source, exported privately if requested)

ID: `1oDLBXjciL8zRmoe4ueYxsZCs33nzO_LXUKRoK6el9Ug`  
URL: https://docs.google.com/spreadsheets/d/1oDLBXjciL8zRmoe4ueYxsZCs33nzO_LXUKRoK6el9Ug/edit

19 tabs observed:
- Company research: `Companies`, `Quarterly`, `Forecasts`, `Decisions`, `Milestones`, `Sources`, `Settings`.
- Peer radar: `Sector Universe` (15 companies across hospitals/tyres).
- Sector context and scoring: `Sector Context`, `Sector Plays`, `Sector KPI Library`, `Sector Scoring`, `Sector Reviews`, `Peer Metric Evidence`.
- Macro research: `Macro Theme Map`, `News Events Curated`, `Macro Risk Watch`, `News Methodology`, `Regime Sector Watch`.

Google Sheets CSV fetch occurs **in the browser** and succeeds only if public-readable at publication time. The embedded HTML datasets are a fallback. Sheet curation does **not** automatically update all published `editorial.json` values or new scheduled AI conclusions; reconciling those is a separate operation. Do not publish the full private Sheet export to this public repository without authorization.

## Research and source provenance tiers

1. Primary transaction/fund/issuer/official filing observation, with date, value, currency and scope.
2. High-quality dated secondary reporting explicitly attributing official data; label "reported".
3. Source-linked archival headline / prediction event; label "unverified headline" or "market quote".
4. Analytical hypothesis or sector/earnings interpretation; label "analyst inference", with a falsification test.
5. Unknown, blocked, missing, incompatible time series; leave unavailable.

## Deployment architecture and ownership

- GitHub Pages deploys public static files from `main`. Each commit can trigger a new site build.
- Two repo Actions write back derived data to `main` with `contents:write`, commit and rebase. Another GitHub Pages run serves the result.
- The external ChatGPT automation has no source code running on GitHub; its schedule and prompt are configured in ChatGPT. A JSON report becomes "published" only when the connector commit is verified.
- Data is globally readable once in public repo. **Never commit passwords, private notes, API keys or user finances**.

For operations and recovery see [OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md).


## 12 November 2026 — new architecture additions

- Root DESIGN.md and assets/equity-ui.css define the shared appearance; assets/equity-shell.js injects grouped page navigation and optional paper/dark preference.
- company-signals.html, assets/company-signals.css and assets/company-signals.js form a lightweight technical surveillance page for additional company research.
- data/market-signals/watch-universe.json lists NSE symbols. Price-history collector scripts/stock_price_volume.py writes stock-price-volume.json (company metadata, last close, OHLCV, 20/50/200-day trend, volume, CMF, OBV, RSI and interpreted mechanical alerts with tests) and price-volume-history.json (AM/PM snapshots).
- The signals Action runs the price-volume script after NSE and Polymarket collection and stages the new data. The independent news Action also runs twice daily. Both target 07:00 and 19:00 IST.
- ChatGPT's AI AM/PM interpretation and monthly valuation review are external schedules; they require actual connector permission and a successful GitHub/Sheet write, distinct from GitHub Actions.
- scripts/validate_site.py and .github/workflows/quality-gate.yml are the reusable code/data/UI validation gate.
- See docs/REFRESH_AND_TECHNICAL.md and DESIGN.md for the exact contracts.

The six-page taxonomy now groups Company Research, Sector Intelligence and Price × Volume under RESEARCH; Morning Intelligence, Rotation × Odds and News Archive under MARKETS. A future truly generic company research route should replace hard-coded Yatharth-specific pages gradually, not destroy baseline financial history.
