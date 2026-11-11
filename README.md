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
