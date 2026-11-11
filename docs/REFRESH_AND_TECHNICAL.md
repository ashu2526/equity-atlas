# Twice-daily automation and company price–volume surveillance

**Implemented 12 November 2026 (India time), data collection first trial on 11 Nov UTC.** This file supplements `OPERATIONS_RUNBOOK.md`. GitHub and task schedules should be reread before relying on their exact next execution.

## 1. The coordinated 07:00 / 19:00 cycle

| Stage | Asia/Kolkata | UTC for GitHub cron | Mechanism | What changes |
|---|---|---|---|---|
| Source news ingestion | 07:00 and 19:00 | `30 1,13 * * *` | GitHub `.github/workflows/news-radar.yml` | RSS articles, feed success/errors, lexical tone, material-event ranking, archives |
| Market signals ingestion | 07:00 and 19:00 | `30 1 * * *`, `30 13 * * *` | GitHub `.github/workflows/market-signals.yml` | NIFTY index rotation, Polymarket active event odds and history, 22-stock EOD OHLCV technical surveillance |
| AI interpretation | ~07:25 and ~19:25 | ChatGPT task, `RRULE:FREQ=DAILY;BYHOUR=7,19;BYMINUTE=25` | **Equity Atlas AM/PM Market Intelligence**, ID `6af49cd9ea508191b74e1ba35e6f9d69` | Intended source-verified AI morning/evening brief to GitHub, with source timestamps and change log |
| Monthly company valuation review | First day of month, ~07:45 | ChatGPT task, `RRULE:FREQ=MONTHLY;BYMONTHDAY=1;BYHOUR=7;BYMINUTE=45` | **Equity Atlas Monthly Valuation Review**, ID `Automation_a78b745ee3c48191a0e6219a52761360` | Intended new dated valuation review and flags, using filings, Google Sheet research, sector context and technical data |

**Important:** GitHub cron times are targets. Free hosted runners may start later, and the 07:25 research task may start while market-signals is still running. The AI must check actual `generatedAt`, use last successful data, and disclose any lag. The AM run uses overnight developments and prior Indian session; PM run uses full Indian trading-day close when released. Financial markets and RSS publishers are not obligated to release data at these times.

**Automated today:** raw/source-linked RSS capture, mechanical headline climate/ranking, NIFTY index price rotation, Polymarket Gamma quotes, dated company OHLCV and pattern flags. **Still AI-agent-dependent:** full factual event interpretation, company/sector judgement, and updating public AI brief JSON via GitHub, which requires a successful future scheduled connector run. **Still analyst-reviewed:** fair values, company forecast assumptions, sector scores, data corrections and portfolio allocation. Do not silently overwrite valuation models based on a chart breakout.

## 2. Actual sources and refresh boundaries

- `scripts/rss_scan.py`: reads configured publisher/institution RSS feeds; quality/completeness depends on source output.
- `scripts/build_regime_pulse.py`: publisher-balanced title-language climate; **not an equity price/credit regime model**.
- `scripts/build_intelligence_feed.py`: title-level materiality/cluster shortlist; individual news event verification still needed.
- `scripts/sector_rotation.py`: official NSE all-index daily closing files with clearly labelled Yahoo fallback only when required.
- `scripts/polymarket_monitor.py`: public Gamma API, active binary contracts, no wallet, bet placement or secret credentials.
- **New `scripts/stock_price_volume.py`:** source priority (a) keyless TejHQ public NSE-bhavcopy-derived OHLCV, (b) Yahoo Finance chart mirror fallback. Both are THIRD-PARTY redistributions/mirrors, not a licensed exchange quote terminal. Free/public source availability and redistribution terms must be reviewed before commercializing or scaling. Output includes exact source, latest available date and stale markers.

Open/keyless TejHQ docs: https://tejhq.dev/docs ; repo: https://github.com/tejhq/tej-bazaar . Yahoo Finance: https://finance.yahoo.com/ . The NSE main reference: https://www.nseindia.com/all-reports .

Initial source run: 22 tracked NSE stocks returned OHLCV with 11 Nov 2026 latest bars, correctly dated; HDFCBANK and SBIN had 200-DMA reclaim *watch* patterns on that date. These are not observed fund flows or confirmations of a permanent reversal. Previous Yahoo-only data was as-of 9 Nov; alerts were initially withheld because its bars were stale. Source selection and dates determine whether a signal can be called current.

## 3. Company technical watch universe

Editable `data/market-signals/watch-universe.json` lists 22 initial symbols, including YATHARTH, 8 other hospital names, 6 tyre businesses, large banks, IT, NBFC and diversified/energy reference businesses. Data is added by a normal GitHub edit to this JSON; the market-signals workflow is triggered on that path and refreshes new tickers.

This is a **research coverage universe**, not a portfolio, buy list, sector FPI positions or performance-ranked fund.

Output:
- `data/market-signals/stock-price-volume.json`: latest per-company signals, as-of date, full metadata and last 120 daily OHLCV bars for charts.
- `data/market-signals/price-volume-history.json`: separate AM and PM snapshots of alerts to help avoid repeating unchanged warnings.
- `company-signals.html`: browsable company list, search/filter, chart and only triggered alert explanations; can deep-link via `#YATHARTH`.
- Main `index.html` overview has a small source-date-aware link/summary rendered by shared `assets/equity-shell.js`.

## 4. Technical indicator math and guardrails

For each stock, using consecutive **completed daily sessions** and close C, high H, low L, share volume V:

### Trend and strength
```text
SMA(20, 50, 200): mean closing price over N completed sessions.
20D return: 100 × [C(t) / C(t-20 sessions) - 1].
60D return: 100 × [C(t) / C(t-60 sessions) - 1].
RSI(14): 100 - 100 / (1 + avg positive delta / avg negative delta)
Previous 20-session high: max(H[t-20 ... t-1])  (excludes current)
Previous 55-session high/low: max/min(H/L[t-55 ... t-1])
Relative volume: V(t) / mean(V[t-20 ... t-1])  (excludes current)
```

**Breakout watch**: close > 1.003× prior 20-session high, volume >= 1.30× typical volume, close at least 55% into that day's range. **Strong 55-session breakout**: close >1.003× prior 55-session high, volume >=1.55×, close at least 60% into range, price above 50-DMA. An equivalent heavy-volume 55-session *breakdown* requires close below previous 55-session low, below 50-DMA and weak in the daily range.

**Reversal watch**: potential 200-DMA reclaim/loss across roughly five sessions with >=1.15×/1.30× relative volume, sufficient ~205 sessions of history. Two or more qualifying 20D volume-backed breakouts in the last 15 sessions are cross-checked against the 200-DMA level and its approximate 20-session slope for **countertrend alerting**.

### Accumulation and distribution proxies
```text
Chaikin MF multiplier = (2×close - high - low) / (high - low)
CMF(20) = Σ(multiplier×V) / Σ(V) over last 20 sessions.
OBV proxy = Σ(sign(Δclose)×V) over last 20 sessions,
scaled by (20 × previous 20-session mean V).
```

A price rally accompanied by a negative OBV proxy can trigger a divergence *watch*. High-volume negative CMF can trigger a distribution *watch*. Neither proves institutional purchase or sale. Genuine large-holder flows require exchange delivery, shareholding changes, block deals and other primary transactions; no such actor inference is made by this engine.

### What suppresses signals

- Source failed, stale or only partial historical data.
- Latest OHLCV more than two **weekday trading sessions** behind the India-local run date (holiday calendar not yet independently integrated).
- Recognized recent split or a single-session price gap beyond 38% within the prior month: likely corporate action/data artefact; independent verification required.
- Insufficient previous history for the period calculation.
- Incomplete current-market daily bar (collector discards current date before ~16:00 IST).

The job preserves a prior successfully retrieved observation when providers fail but labels it `fetch_failed_stale_previous_snapshot` and emits **no active alerts**. Dates do not silently advance.

## 5. Correct research workflow for a flagged company

1. Read `company-signals.html#TICKER`; record as-of date, observed price/volume pattern and confidence/coverage state.
2. Compare NIFTY sector rotation over short/medium/long windows; explicitly distinguish index performance from transactions.
3. Search the issuer exchange filings/quarterly results for a real catalyst, capex, funding or risk.
4. Verify whether sales/margins/ROIC/cash flow assumptions change and assess valuation sensitivity.
5. Consider genuine institutional source releases only if dates and measurement scopes align.
6. Write a dated *research note*, including a possible invalidation and alternative cause, instead of "buy on breakout".
7. Reassess one month later or sooner if the investment thesis materially changes.

## 6. UI and future scaling

The common design is in `assets/equity-ui.css`, navigation in `assets/equity-shell.js`, and the price-volume page in `company-signals.html` + `assets/company-signals.css/js`. The **global navigation taxonomy** is explained in `DESIGN.md`.

No heavy chart library. Daily closes and share-volume bars are rendered as simple native SVG, and 20/60/120 bars are selectable. On mobile, the stock list collapses above the detail panel. Paper/dark preference is optional and saved in the browser.

When new firms are added:
- append the NSE symbol to `watch-universe.json`, which triggers the collector;
- add verified company fundamental/valuation research in the Sheet and company research section;
- do **not** interpret auto-collected OHLCV as a valuation;
- if the company has no 200-session history yet, show partial coverage.

## 7. Remaining gaps

- Improve source licensing/terms and add official NSE trading-holiday calendar / corporate action-adjusted price-volume verification.
- Make the monthly valuation review produce a reliably published dated, audit-ready company verdict; never automatically alter an investment thesis from price alone.
- Add actual delivery volume, large block trades, shareholding disclosures, FPI sector allocation and earnings revision breadth—**with dates**, separate from patterns.
- Add test fixtures for breakout math, splits, alert repetition and historical signal precision/false positives.
- Browser smoke tests for every page and interactive tab after each stylesheet or navigation change.
- Scale company research using one shared company detail template instead of duplicating the existing Yatharth page.

No scheduled future AI result is represented as already published.
