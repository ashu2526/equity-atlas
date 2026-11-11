# Equity Atlas — Yatharth research website

A free, responsive, static investment research dashboard for GitHub Pages.

## 1. Google Sheet source

Your editable spreadsheet is:
https://docs.google.com/spreadsheets/d/1oDLBXjciL8zRmoe4ueYxsZCs33nzO_LXUKRoK6el9Ug/edit

Tabs: Companies, Quarterly, Forecasts, Decisions, Milestones, Sources, Settings.

**Privacy:** Do not publish your private investments, contact details, credentials, or personal finance information. This site connects to a Google Sheet without login, so the relevant Sheet tabs must be publicly readable for direct browser sync.

For data sync: in Google Sheets select **File → Share → Publish to web** (or configure anyone-with-link View access where Google's CSV endpoint permits), publish the spreadsheet, and press **Sync Sheet** in the website. If publication is disabled or CSV access fails, the site displays a bundled Q2 FY27 baseline rather than fake live data. The data is not automatically written back from the website; make edits in Google Sheets.

## 2. GitHub Pages hosting — free

1. Sign in to GitHub as `ashu2526`.
2. The public repository `ashu2526/equity-atlas` has already been created.
3. `index.html` and `README.md` are deployed to the repository root.
4. Open repository **Settings → Pages → Build and deployment → Deploy from a branch**, select `main` and `/ (root)`, then **Save**.
5. Your site URL should be `https://ashu2526.github.io/equity-atlas/` after deployment. This is an expected pattern, **not verified as live**.

## Quarterly workflow

- After results, add an entire new row to the **Quarterly** tab. Do not overwrite the old quarter.
- Add a dated row in **Decisions** explaining the previous and new view.
- Update **Forecasts** with a new version/date, retaining historical assumptions separately.
- Site reloads published Sheet data when **Sync Sheet** is pressed.
- Use the valuation sliders to explore scenario sensitivity; these changes are temporary and do not edit Sheet values.

## Model integrity

Scenario equity value per share is `(EBITDA × EV/EBITDA − net debt + unspent equity cash) / diluted shares`.

**Never double-count acquisitions:** if the forecast EBITDA includes companies acquired with equity proceeds, reduce unspent cash for the purchase. Transaction proceeds are conditional until the securities are funded.

## Limitations

- The original dashboard contains source conflicts and preliminary numbers. Some data is labelled derived or secondary.
- No live market quote service, brokerage trading, authentication or secure editing backend is included.
- Published GitHub Pages sites and published Sheets should be assumed public.
- Only Yatharth is populated; later companies need new rows and company-selector support.

## Sector Radar (added 11 November 2026)

- **Sector Universe** tab in the Google Sheet is the editable source for ranked hospital and tyre-sector research candidates. Ranking numbers are qualitative **research priority**, not buy recommendations.
- The live site includes a bundled snapshot of the 15 company profiles, so it works before the Sheet is published for anonymous reading.
- Profile fields include competitive edge, main risk, dated trailing P/E, evidence URL, business archetype and deep-dive status.
- Select **Sector Radar** in the navigation, switch between **Hospitals** and **Tyres**, select a company for the quick view, and use **Shortlist for Deep Dive**.
- The shortlist is saved in `localStorage` of your own browser only; it does **not** automatically update Google Sheets or sync between devices. Export the shortlist as JSON or copy a research prompt.
- To update the site from the Sheet later, share/publish the research-only tab for anonymous reading. Do not publish personal holdings, private trade information, API keys or personal details. GitHub Pages itself is public.
- Research order can differ from portfolio allocation decisions: **BKT** is an off-highway specialist whereas **MRF / Apollo Tyres** are larger diversified businesses. Never infer a fixed portfolio weight from the ranking.

## Market Regime & News Radar — 11 November 2026

Open [Market & News Radar](https://ashu2526.github.io/equity-atlas/news-radar.html) from the main dashboard.

**What is already built**
- User-selected 7/14/30-day or custom date windows with the **equal-length preceding period** shown as a comparator.
- 13 macro theme maps showing first-order sector effects, second-order/proxy opportunities, what would confirm the theme and what would invalidate it.
- Curated, source-linked 11 Nov 2026 initial events and a separate source/provenance methodology.
- Global risk board covering **sovereign/mega-company CDS headlines, credit stress proxies, elections, trade wars, conflict, energy shipping, weather and policy**. **No issuer or sovereign live CDS spreads.** US HY OAS may help as a stress proxy, not a CDS substitute.
- A daily GitHub Actions RSS scanner and durable JSON storage in `data/news/articles.json` and `data/news/scans.json`. Source config: `data/news/config.json`. Schedule: 02:21 UTC daily (07:51 IST). Manual starts are possible on the workflow's **Actions → Run workflow** page.
- First successful RSS scan: **11 Nov 2026 UTC**. It fetched 14 of 15 publisher/institution feeds, deduplicated 138 relevant headline links, and recorded the failed UN feed. The observed headline coverage is partial, not comprehensive.
- Changing dates does **not** initiate a historical web crawl: it filters existing archived links. Publisher feeds don't expose every older article.
- Headline `positive/negative/neutral` tone is a simple disclosed lexical count, *not* full-text sentiment or a recommendation. Topic-count changes are *attention signals*, not confirmed market regimes.
- Compare `Since the previous archived scan` for newly discovered headlines. Matched-window regime comparison is flagged insufficient until sufficient actual continuously collected coverage exists.

**Architecture and privacy:** GitHub Pages hosts static HTML; the page reads public JSON from the repository's `main` branch. Scheduled GitHub Actions commits public RSS metadata and scan histories. Google Sheets stores the manually curated thematic exposures and editorial source log; the GitHub `editorial.json` is its published, dated copy. Edits to the Sheet do **not** automatically flow into this news website. Never publish personal holdings, secrets or confidential notes. The site is public.

**Limitations:** Publisher source availability, RSS headline length, keyword tagging, duplicate reporting and incomplete coverage create sampling biases. Coverage does not include full CDS pricing, an exhaustive global election calendar, verified company-wide credit spread moves, an authenticated sentiment model or automated cross-asset confirmation. Confirm major investment decisions with official filings, credit releases, central banks, exchange reports and market data.

## Closed-loop Market Intelligence (added 11 November 2026)

1. **Daily collection:** [Market Regime Radar GitHub Action](https://github.com/ashu2526/equity-atlas/actions/workflows/news-radar.yml) queries 15 configured RSS/official feeds and archives publisher-linked headlines, dated events and source failures.
2. **Daily observation:** `scripts/build_regime_pulse.py` converts the archive into `data/news/market-pulse.json` (source-balanced **headline-language** index, topic attention and sector proxy mapping). `data/news/pulse-history.json` retains snapshots. It does **not** calculate actual market-price sentiment or confirm economic regime changes; no CDS prices are inferred.
3. **Fortnightly AI interpretation:** A ChatGPT scheduled task has been created for **every other Wednesday, first 25 November 2026, 09:00 Asia/Kolkata**. It is **not** part of GitHub Actions and does **not** use GitHub Models (the service retired in July 2026). The task researches source-linked changes, assesses investment themes, compares older reports, and **attempts** to update `data/news/ai-reviews.json` using the connected GitHub app. If GitHub writing is unavailable it will provide the report in ChatGPT and disclose that the site was not changed; no unattended publishing is guaranteed without a successful connector write.
4. **Website:** [Market & News Radar](https://ashu2526.github.io/equity-atlas/news-radar.html) displays current news climate and separately dated AI-reviewed interpretations; [homepage](https://ashu2526.github.io/equity-atlas/) displays both summaries. The AI archive is versioned; an initial provisional assessment is seeded as of 11 Nov 2026.
5. **Cost and safety:** This design requires no paid LLM API key and makes no GitHub Models calls. It does use GitHub Actions minutes and a ChatGPT automation (subject to plan and platform limits); public GitHub Pages and repository JSON expose published research. Do not put credentials, private holdings or sensitive data in the archive. RSS/metadata use and news source availability are subject to upstream conditions.
6. **Validation:** AI conclusions must distinguish signal from speculation, source timestamps from discovery timestamps, news attention from cross-asset market regime evidence, and source-confirmed data from model-generated hypotheses.

## NIFTY Sector Rotation and Polymarket — added 11 Nov 2026

Live page: [Sector Rotation × Polymarket](https://ashu2526.github.io/equity-atlas/signals.html) — linked directly from the home page, Sector Intelligence and Market Intelligence Desk.

### Sector leadership / momentum
- [NSE official All Reports](https://www.nseindia.com/all-reports) contains daily **All Indices Daily Close** CSV files (`ind_close_all_DDMMYYYY.csv`). `scripts/sector_rotation.py` reconstructs approximately 120 calendar days of index closes, caching source series and updating recent sessions.
- Coverage includes **NIFTY 50** plus 19 sector/industry indices (banks, PSU banks, private banks, media, metals, pharma, FMCG, auto, healthcare, consumer durables, etc.).
- Calculates **7-day**, **30-day** and **91-day** price returns, sector vs NIFTY 50 three-month relative return (in *percentage points*), and **monthly momentum acceleration** (latest 30d price return minus preceding 30d). Returns use matched/as-available historical close dates, and the chart plots sector/NIFTY 50 common trading dates rebased to 100.
- Ranks are **relative price leadership** only. Rising index values cannot establish where FPI/DII money actually flowed; use NSDL FPI sector data and NSE FII/DII turnover separately. Price indices exclude dividends, and index methodology/weights can change.
- Source fallback to Yahoo Finance public chart is explicitly tagged for any instrument where NSE cannot supply sufficient history. Never fill missing historical price points with guesses. See `data/market-signals/sector-rotation.json` and `index-history.json`.

### Polymarket public global-event market data
- Official reference: [Polymarket Agent Skills / Market Data](https://github.com/Polymarket/agent-skills/blob/main/market-data.md). Discovery is through Polymarket's **unauthenticated, read-only Gamma API** (`https://gamma-api.polymarket.com/events`). We intentionally avoid wallet/trading/credential SDKs: the older official `py-clob-client` repository was archived during 2026.
- `scripts/polymarket_monitor.py` samples active events ordered by reported trading activity; screens unresolved **binary YES/NO contracts** by relevance to interest rates, elections, trade policy, conflict, AI, energy and system risk; removes obviously unrelated sports/entertainment events.
- The dashboard shows exact market question, outcome YES quote as a percentage, 24-hour trading volume, reported market liquidity, expiry, link to the actual contract and the economic sectors potentially exposed. It adds probability-change comparisons only between previously archived quote snapshots.
- The **News × Event Odds** view associates specific macro-tagged news via conservative title-keyword overlap. These are *related stories*, not a certification that the article validates that contract's payout conditions.
- Markets may be speculative, thinly traded or manipulated. YES quoted prices are **market-implied contract values**, not rigorously calibrated odds, certainty, verified news or investor flow. Polymarket trading volume is not equity fund flow. No betting or wallet functions are used.
- Source data: `data/market-signals/polymarket.json` and `polymarket-history.json`.

### Refresh / reliability
- The independent GitHub Action `.github/workflows/market-signals.yml` refreshes twice daily (03:35 and 15:15 UTC, i.e. about 09:05 and 20:45 IST) and supports manual runs. Runs can be inspected under **Actions**.
- The **daily ChatGPT morning intelligence task** has been updated to review both datasets, check important global Polymarket odds and 3-month sector price leadership, and distinguish that from verified institutional sector/country fund flows.
- Public GitHub Pages fetches the latest committed JSON; it does not call the trading venue from the user's browser.

## Maintainer documentation and full-source handoff (11 Nov 2026)

The project's reusable **repository-local maintainer skill** is [`.agents/skills/equity-atlas/SKILL.md`](.agents/skills/equity-atlas/SKILL.md), with [`AGENTS.md`](AGENTS.md) as an entry point. This is a version-controlled development skill, **not** an account-level ChatGPT plugin or a replacement for project source code.

- [Current implementation and project progress](docs/PROJECT_STATUS.md)
- [Architecture, pages, data contracts and Google Sheets](docs/ARCHITECTURE_AND_DATA.md)
- [Quantitative methodology, source quality and important caveats](docs/METHODOLOGY_AND_GUARDRAILS.md)
- [Operations, schedules, manual reruns and incident recovery](docs/OPERATIONS_RUNBOOK.md)
- [Roadmap, known defects and regression checklist](docs/ROADMAP_AND_QA.md)
- [Asset inventory and source ZIP guide](docs/ASSET_INVENTORY.md)

To produce an up-to-date **whole-repository source/data archive**, run the `Equity Atlas Source & Documentation Backup` workflow under GitHub Actions. It exports all working HTML pages, Python scripts, public JSON datasets, workflows, documentation and the local skill, plus source commit/hash manifest. The linked Google Sheet remains external and is **not** uploaded to this public repository; an owner-only expanded ZIP can include a private Excel export separately.

**Honest status:** At the 11 November 2026 handoff, both RSS and market-signals GitHub collectors had succeeded with real data, and the Signal Lab sidebar selector bug was fixed and Pages-deployed. The first automated ChatGPT 09:15 IST **AI-reviewed report write-back** had not yet occurred and should not be claimed as verified.
