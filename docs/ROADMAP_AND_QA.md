# Quality assurance, observed defects and refinement roadmap

Snapshot 2026-11-11. This is a **fact-based gap register**: "built" means code/data exists; "verified" means a specific pipeline or deployment actually succeeded; "planned" means not implemented.

## 1. Acceptance testing — minimum regression checklist

### Site and navigation

- [ ] Homepage opens, Sector Intelligence opens; Sector Intelligence → Home → Sector Intelligence round trip works without custom browser cache resets.
- [ ] `signals.html` tabs: Sector Rotation → Polymarket Odds → News × Event Odds → Methodology → Sector Rotation; each **actual content panel** changes.
- [ ] Signal Lab navigation buttons have `data-view` matching sections `id=sector|odds|joined|method`, all share `class=sigview`, CSS hides inactive sections.
- [ ] Sector sort by relative return, absolute return, 1m, acceleration works; selecting any sector changes detail AND aligned benchmark chart; keyboard activation works where practical.
- [ ] Polymarket category/search/order filters update cards; contract links open correct named markets; refresh reloads data.
- [ ] News archive date-range filters, topic search, attention comparison and AI-review archive work; missing prior coverage shows warning.
- [ ] Market desk seven views work and freshness/status dates appear; source links valid; null flows not rendered as zero.
- [ ] Responsive mobile layout works without overlay, horizontal trap or hidden links.

### Data and research integrity

- [ ] Every `*.json` parses and every HTML embedded `<script>` parses.
- [ ] At least 3 representative NIFTY sector calculated returns match official NSE closes and dates within rounding.
- [ ] The NIFTY 50 benchmark chart uses the same trading dates as selected index; no cherry-picked date alignment.
- [ ] Missing NSE index or stale market data displays unavailable, not a zero or synthetic result.
- [ ] Polymarket YES quotes fall in [0,1], metadata matches the named market question and `endDate` is sensible; odds changes use actual previous snapshots.
- [ ] News source event and publisher/URL/provenance actually correspond; report quote is not inferred from betting volume.
- [ ] RSS feed failure is recorded, histories and prior snapshots survive, and news-climate index discloses lexical-only origin.
- [ ] Institutional-flow observation date, unit, value sign, transaction/holding/price type and source are correct.
- [ ] Sector/peer rating references are dated, source-backed and not fabricated numerical buy rankings.
- [ ] No private credentials, confidential positions, personal financial info or Google Sheet content is accidentally committed to public GitHub.

### Automated deployment

- [ ] Manual news workflow succeeds and commits sensible data.
- [ ] Manual signals workflow succeeds (or marks a source failure), retains old snapshot and publishes new valid date when available.
- [ ] **First scheduled ChatGPT 09:15 IST report** genuinely fetches sources, appends `daily-briefings.json`, retains history, and newest report is displayed on Page.
- [ ] First scheduled fortnightly deep review actually appends `ai-reviews.json` or explicitly reports inability.
- [ ] Latest Pages deployment completes successfully on the SHA containing the fix.
- [ ] Automated ZIP packaging workflow succeeds, ZIP manifest hashes match included paths, no `.git` directory and no credential files.

## 2. Known defects, decisions and lessons

| Date | Incident / discovery | Resolution and remaining test |
|---|---|---|
| 11 Nov 2026 | Sector Intelligence link on homepage was handled like a tab and did not open | Replaced with real anchor plus direct CTA and versioned return; continue round-trip browser testing |
| 11 Nov 2026 | Older homepage cache could be restored after returning from Sector Intelligence | Link hardening; browser-level verification and consistent URL strategy still useful |
| 11 Nov 2026 | GDELT collector received 429/rate limit from GitHub runner | Switched scheduled news collector to source RSS; `scripts/news_scan.py` remains legacy unused by workflow |
| 11 Nov 2026 | Polymarket Gamma returned oversized nested event JSON | Reduced pagination to 50 events per request and removed truncating body read; now published real data |
| 11 Nov 2026 | Signal Lab sidebar highlighted Methodology, but NIFTY content stayed in view | **Fixed** mismatch: `$$(".view")` → `$$(".sigview")`; syntax and successful GitHub Pages deploy verified; full external browser click sequence still should be regression-tested |
| 11 Nov 2026 | Need to distinguish equity price return, foreign trading and contract volume | Added separate flow ledger and distinct labelled NSE / Polymarket metrics; more source connectors still needed |

## 3. Prioritized refinement roadmap

**P0 — trust and daily automatic loop (do next)**
1. Verify first ChatGPT 09:15 morning report **writes an append-only, source-verified JSON item to GitHub** and appears after Pages deploy. Add a status/alert if the task could not publish.
2. Add a safe public research schema validator and CI job checking date/unit/URL, null semantics, odds range, nondecreasing history, HTML nav/panel contract and Python compile before publish. Add browser smoke test using Playwright or similar.
3. Add source freshness dashboards per feed, sector dataset, Polymarket and AI report; do not display "live" if data is stale.
4. Refine news severity with proper independent source verification and avoid near-duplicate headlines. Add a curated exception queue for important low-volume events.
5. Add automated daily briefing cross-check against NIFTY price leadership, FPI flow release windows and Polymarket specific contract movements; never force a summary.

**P1 — actual capital allocation, risk and investment rigor**
1. Source and ingest validated **NSE daily FII/DII**, **NSDL fortnightly sector FPI**, **AMFI monthly** numeric series with immutable as-of periods and primary-source/format checks; show revisions and calendar lags. Current `flows.json` is largely curated.
2. Add reliable global cross-border/country flow series where licensed or openly available; separate Treasury TIC, ETF/fund creations/redemptions and CFTC futures positioning.
3. Add NSE index constituents/sector breadth, 1/3/6-month industry comparison, drawdowns and volatility, valuation percentile and 1/3-month earnings revision breadth.
4. Add verified credit spreads and sovereign/issuer credit-event history; do not fabricate CDS quotes. Licensed single-name CDS may be infeasible without subscriptions.
5. Build an auditable composite **regime change framework** that requires aligned price/flows/earnings/risk evidence and grades causal confidence. Maintain backtests, avoid overfitting narrative hindsight.

**P2 — sector, company and interpretation depth**
1. Head-to-head hospital and tyre peer scoring with common measurement dates, operating-model differences, company fundamentals, valuation scenarios and downside.
2. Expand economic sector playbooks beyond hospitals/tyres, including capex, banks, chemicals, renewables, autos, defence and energy.
3. Replace simplistic RSS lexicon with transparent, independently evaluated event impact/NLP, source credibility, region and issuer linkage. Prefer no signal to misleading signal.
4. Add probability market contract matching based on exact resolution condition, event identity, question semantics and live quote; evaluate reliability and closing dynamics. Avoid treating event contracts as a substitute for official statistics.
5. Track past "watch now", "cooling" and "regime change" hypotheses and **measure ex-post outcome vs declared horizon**; include decision audit trail and false signals.

**P3 — usability and product quality**
1. Split single-file inline HTML into maintainable components/testable modules without breaking static Pages.
2. Better mobile accessibility: keyboard focus, semantic roles, row hit targets, sticky headers and charts with text alternatives.
3. Export source-backed sector scorecards/research notes to PDF/CSV, user-controlled optional watchlists, risk alerts and saved comparisons.
4. Add a consolidated economic calendar for central banks, elections, tariffs, major earnings, data releases and expiry of prediction markets.
5. Define licence/redistribution policy and rate/usage budgets for feeds.

## 4. Change-review template for future refinements

Every feature PR should answer:
- **User research question:** What decision does this help?
- **Evidence:** Which primary/secondary sources, exact date/unit, known delay?
- **Calculation:** Formula, window, data gaps, ambiguity and examples.
- **Economic mechanism:** What changes costs, volumes, funding or valuation?
- **Alternatives:** What if story, price and real flows disagree?
- **UI state:** What is visible during loading, stale, missing or error?
- **History:** How will prior states be preserved and compared?
- **Tests:** Data and browser interaction tests + Pages run.
- **User disclosure:** Is it verified fact, source headline, market quote or hypothesis?

## 5. Definition of done

A feature is **complete** only if its code is committed, data can be reproduced/validated, browser controls work, sources/units/freshness are transparent, failure states are honest, GitHub Pages deploys, and the relevant maintainer documentation is updated. Scheduling a future agent run is not proof of successful publication.


## 12 November 2026 — new completed items and acceptance tests

- [x] Source collection scheduled at 07:00 and 19:00 IST (GitHub news, NSE rotation, Polymarket and stock technicals).
- [x] AI AM/PM review scheduled at ~07:25 / ~19:25 IST, with future actual publishing verification still pending.
- [x] First-of-month valuation research task scheduled at ~07:45 IST, future review/output verification pending.
- [x] Stock OHLCV collector ran successfully: 22/22 NSE symbols as of 11 Nov 2026 using source-prioritized public historical data, preserving source, unit and freshness flags.
- [x] New company technical dashboard with source-backed 20/55-session breakout/breakdown, CMF, OBV, SMA and 200-day reversal watch evidence.
- [x] OpenDesign-informed shared root DESIGN.md, six-page Research/Markets navigation, accessible focus, compact paper/dark display and no heavy runtime dependencies.
- [x] GitHub no-dependency quality-gate workflow executed successfully on its initial run.
- [ ] Verify cross-page links and every tab, filter, input, chart selection and color mode in a live graphical browser on desktop and mobile; static JS tests alone do not prove browser UX works.
- [ ] Verify scheduled AI morning AND evening publication each committed the correct session to daily-briefings.json and survived GitHub Pages deployment.
- [ ] Verify a completed monthly valuation note actually updates appropriate Sheet research history, with source time alignment.
- [ ] Verify NSE-derived third-party redistribution/licensing constraints and corporate-action-adjusted OHLCV against official exchange records, including a real Indian holiday calendar.
- [ ] Add unit tests using frozen OHLCV fixtures for confirmed/failed breakout, duplicate breakouts, stale historical bars, splits, and 200-day cross logic.
- [ ] Extend actual ownership/flow data so institutional accumulation can be separated from price-volume proxy and creator narratives.
- [ ] Generalize company research page beyond the initial Yatharth baseline while retaining all prior valuation history.

This section supersedes the earlier 11 November pending roadmap entries when they refer to features now implemented; see docs/REFRESH_AND_TECHNICAL.md for definitions.
