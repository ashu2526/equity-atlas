# Operations, updates, incidents and restoration

Version: 2026-11-11. **Read `docs/PROJECT_STATUS.md` and `AGENTS.md` before editing.**

## 1. Repository and deployment

- GitHub repository: https://github.com/ashu2526/equity-atlas
- Main public site: https://ashu2526.github.io/equity-atlas/
- GitHub Actions: https://github.com/ashu2526/equity-atlas/actions
- Signal page: https://ashu2526.github.io/equity-atlas/signals.html
- Market desk: https://ashu2526.github.io/equity-atlas/market-desk.html
- Google Sheet: https://docs.google.com/spreadsheets/d/1oDLBXjciL8zRmoe4ueYxsZCs33nzO_LXUKRoK6el9Ug/edit

The HTML pages are static; each page fetches its published JSON from the same repository (or raw.githubusercontent on the News Radar). Pages deployment lags a GitHub commit. Always inspect the build on the newest relevant SHA before telling anyone the website is live.

## 2. Automated workflows (actual configured cron)

| Update | Workflow | UTC | Asia/Kolkata | Inputs | Output |
|---|---|---|---|---|---|
| RSS + lexical climate + ranked feed | `.github/workflows/news-radar.yml` | 02:21 daily | **07:51 IST** | 15 configured RSS feeds and topic rules | `data/news/articles.json`, `scans.json`, `market-pulse.json`, `pulse-history.json`, `ranked-feed.json`, `ranked-feed-history.json` |
| NSE + Polymarket signals | `.github/workflows/market-signals.yml` | 03:35 daily | **09:05 IST** | NSE daily all-index CSV, public Gamma API | `data/market-signals/index-history.json`, `sector-rotation.json`, `polymarket.json`, `polymarket-history.json` |
| NSE + Polymarket signals | Same workflow | 15:15 daily | **20:45 IST** | Same | Same |
| AI Morning Intelligence | **ChatGPT scheduled task, not GitHub Action** | Local task 09:15 IST | **09:15 IST** starting 2026-11-12 | Repo JSON + fresh verified primary/reporting sources | Intended `data/news/daily-briefings.json`, periodic `ai-reviews.json`, verified new flow observations if any |

Task title **Equity Atlas Morning Intelligence**; task ID `6af49cd9ea508191b74e1ba35e6f9d69`. It is enabled and its next scheduled run was 2026-11-12 09:15 Asia/Kolkata at the time of this documentation. Its GitHub write-back behaviour was **not yet tested end to end**. The daily task was instructed to run a deeper fortnightly review approximately every 14 days; future actual reports must be checked.

**Race and timing warning:** The 09:05 signals job may still be running at 09:15. The AI task must inspect `generatedAt`/source timestamps and mention if it analysed the prior signal snapshot. Flexible scheduled tasks can run around their target time, not with guaranteed second-level precision.

### Trigger manually

From GitHub: **Actions → Market Regime Radar - source-linked news scans → Run workflow** (or **NIFTY Sector Rotation and Polymarket Event Odds → Run workflow**). You can also execute scripts locally in the repository root with standard Python 3.12. Scripts primarily use Python standard library, no secrets or API keys.

```bash
python scripts/rss_scan.py
python scripts/build_regime_pulse.py
python scripts/build_intelligence_feed.py
python scripts/sector_rotation.py
python scripts/polymarket_monitor.py
python -m compileall -q scripts
```

Be aware the data-writing scripts mutate public JSON files. Work in a fresh branch or development clone if testing data transformations. Never automatically commit an unverified or truncated source state.

### Normal public data publishing

GitHub Action checks out main, runs collectors, uses `git add`, commits derived JSON, `git pull --rebase origin main` and pushes. The Page build then redeploys. Workflows have `permissions: contents: write`. Signals workflow uses `continue-on-error: true` for each collector so a working source can publish when the other fails, but the workflow fails if **both** collectors fail.

If a GitHub contributor updated files while the job was running, the rebase can still encounter conflicts. Inspect and resolve them; do not force-push or erase verified reports.

### Check whether AI briefing actually published

1. Open `data/news/daily-briefings.json` on **main**.
2. Confirm first `briefs[0]` has today's **Asia/Kolkata** review date, `author`, `publicationStatus`, `createdAt` and source URLs.
3. Inspect Git commit author/message and whether the ChatGPT task genuinely performed verification and GitHub update; a task notification is not proof.
4. Confirm the latest page build completed and that `market-desk.html#morning` shows the new report.
5. If the task failed to commit, retain yesterday's report with its date; show AI research as stale. Do not replace yesterday's evidence with unreviewed RSS sentiment.
6. For the fortnightly deep audit, verify `ai-reviews.json` gained an assessment without deleting older reviews.

This is the highest-priority operational test after 11 November.

## 3. Data / article / predictor validation

### RSS and news
- Check `scans[0].queriesSucceeded`, `queriesTotal`, `queriesFailed` and `newUniqueArticles`. Baseline: 14 of 15 selected feeds succeeded at initial successful run; one feed had parsing trouble. The current exact number may differ.
- Check `articles.json.updatedAt` and source dates. A published old article discovered today is *not* an event from today.
- Verify ranked story URL/domain/title; source headline is not the same as verified full text.
- Ensure `market-pulse.json.model = RULES_V1_SOURCE_BALANCED_NO_LLM` and market regime is marked unconfirmed unless an independent data layer is added.

### NSE
- Check `sector-rotation.json.status=ready`, `asOf`, `sourceDiagnostics.nseDailyFiles`, `missingIndices`, and exact `priceSource` for each sector.
- Valid 3m returns need comparable historic close; `null` means unavailable, not flat.
- If NSE blocks requests, inspect `nseErrorExamples` and tagged fallback indices. A fallback source must be visible in UI.
- Compare a few indices against NSE historical data. Correct index aliases, date alignment and outliers before public claims.

### Polymarket
- Check `polymarket.json.dataStatus` and `lastAttemptAt` vs `generatedAt`; first may show failed update with a preserved older snapshot.
- If large Gamma JSON payloads truncate or fail, split queries or remove premature `read(n)` limits; collector has already needed this fix once.
- Check exact question, YES outcome, market expiry, volume/liquidity, active/closed status, market URL; do not assume all event outcomes are binary.
- Check `polymarket-history.json` before calling any difference a trend. Delta uses actual previous successful snapshots, not fixed clock time.
- No wallets, trading keys, order client or betting operations.

## 4. Common website incidents and tested remedies

**Sidebar selects new item but old content remains:** `signals.html` must toggle `$$(".sigview")` when clicking `#nav button`. The older `.view` selector was the exact bug fixed 2026-11-11. Verify actual panel content switch and CSS display state.

**Home → Sector Intelligence fails after return:** Use plain `<a href="./sector-intelligence.html">` links, not dynamic tab controls that overwrite link handlers; a prior cache/navigation issue required replacing a button with a real anchor and versioned return link. Verify round trip.

**Site 404 or old page after push:** Check Pages build status / SHA; the browser may cache old HTML. Test with versioned URL query (e.g., `signals.html?v=<commit>`) and Ctrl+Shift+R. Version strings do not cause the server to use a different git file; they bypass a cache.

**All news/odds/sector values disappear:** Open browser DevTools Network/Console. Check JSON 200 response and parseability. Confirm `dataStatus`, last commit, GitHub Actions logs. Display "unavailable" with last good date if fetch failed.

**Google Sheet sync not updating research page:** `index.html` and `sector-intelligence.html` call `docs.google.com/spreadsheets/d/.../gviz/tq?out:csv` from the browser. Public-readable Sheets permissions may be required. The embedded fallback data may still render; do not mistake this for successful synchronization. Do not make the private workbook public without owner consent.

**GitHub Action new data isn't on site:** Check if the scanner actually committed JSON, if the Pages build completed, and the browser fetch query/no-store. If still stale, inspect exact public JSON response and timestamps.

**External AI task missed a briefing:** Search the task history and GitHub commits. The AI job must explain failure without representing old `daily-briefings.json` as newly published. Consider an independent GitHub Actions watchdog and verified alert in roadmap.

## 5. Maintenance safety and change procedure

- Before editing: inspect `main` via GitHub API or clone; never base edits on older local scratch files.
- Always preserve older `articles.json` / `scans.json` / odds history / research reports and original sources; use unique IDs.
- For GitHub connector file updates: `fetch_file` → edit full UTF-8 content → `update_file` with **exact current blob SHA**; on conflict, refetch and merge.
- Do not publish a private Google Sheet export to the public repo just because it is available through a connector.
- After UI change: parse embedded JS, validate selectors and nav IDs, click all tabs/filters/selectors and return paths (manual or browser automation).
- After workflow change: verify YAML, workflow dispatch result, job logs and commit, then latest Pages build.
- After source change: verify licence/terms, source dates/units and provider availability. No scraping bypass or unauthorized trading.

## 6. Recovery / rollback

- Prefer a **revert commit** of the specific broken change, not a `git reset --hard` on shared `main`.
- For a broken collector, keep the last correct JSON and visibly mark data stale. Do not overwrite with empty arrays and claim a market crash.
- For broken UI, restore the last known successful HTML and keep the source archive untouched.
- Use the project ZIP backup as a **snapshot**. It does not include a Git `.git` folder/commit ancestry, secrets, user account automations, or a guaranteed current external spreadsheet after export. GitHub remains the authoritative repo history.
- Before restoring old data, check whether newer scanner or AI reports need preserving.

## 7. Documentation and export policy

A clean full-source ZIP can be created by `.github/workflows/documentation-export.yml` after docs are committed; the ZIP includes repository code, static HTML, workflows, data and local skill instructions. A conversation-level expanded archive can additionally include private, user-supplied research reports and an exported workbook **without** uploading them into public GitHub. Mark these extras as dated reference snapshots, not runtime source of truth.
