# Asset inventory and reproducible snapshots

Snapshot created 2026-11-11. Use `AGENTS.md` and `docs/PROJECT_STATUS.md` for context.

## Included in the canonical source ZIP

The canonical GitHub Assets ZIP is a **repository source/data snapshot**, built via `.github/workflows/documentation-export.yml`:
- `index.html`, `sector.html`, `sector-intelligence.html`, `market-desk.html`, `news-radar.html`, `signals.html`.
- All standard-library Python scripts under `scripts/`.
- Both scheduled GitHub workflows and the source export workflow in `.github/workflows/`.
- Entire `data/news/` and `data/market-signals/` public dated research archives as of the selected commit.
- All `docs/` files plus `README.md`, `AGENTS.md` and `.agents/skills/equity-atlas/SKILL.md`.
- Machine-readable source-path/byte/SHA-256 checksum manifest, plus commit/source-attribution notes.
- Excludes Git history (`.git`), temporary files, private API keys and private Google Sheet export.

The ZIP is a **snapshot**, not a reproducible environment image: no third-party auth, ChatGPT task state, GitHub Action credentials, published Pages cache, live source endpoints or Google Sheet permissions are packaged.

## Expanded private conversation backup

A conversation-download archive may additionally include:
- A separate **Google Sheets workbook export (.xlsx)** of the connected *Equity Research Database — Yatharth & Quarterly Reviews* (19 tabs as of snapshot), for offline editing and continuity. This is intentionally **not committed to public GitHub**.
- Prior Yatharth IC baseline PDF and quarterly monitoring scorecard PDF, if present in the working conversation files.
- Relevant desktop/mobile screenshots and other previous source snapshots, clearly labelled **legacy/older references**.
- The source ZIP as an inner package (so the exact GitHub snapshot is preserved, not a paraphrased reconstruction).

Such a combined private archive is for the owner only; sharing it can disclose the research workbook or personal content. Verify its file manifest after download.

## Asset map

| Where | Content | Update channel |
|---|---|---|
| `index.html` | Main dashboard and Sector Radar | GitHub HTML |
| `sector-intelligence.html` | Hospital and tyre sector frameworks / peer research | GitHub HTML and Google Sheet reads |
| `market-desk.html` | Morning AI reports, ranked source news, flows/risk/history | Public JSON and ChatGPT reviewed writes |
| `news-radar.html` | Dated news archive/regime themes/reviews | Public `data/news/*.json` |
| `signals.html` | NIFTY 3m relative leadership and Polymarket YES odds | Public `data/market-signals/*.json` |
| `scripts/` | RSS collector, lexicon, ranked feed, NSE returns, Gamma odds; legacy GDELT script | GitHub Actions / maintenance |
| `data/news/` | Machine/analyst source evidence and historical snapshots | Daily news Actions, external AI write-back, manual research |
| `data/market-signals/` | Historical sector closes, contract market quotes and snapshots | Twice daily signals Action |
| `.github/workflows/` | Automated schedules, source writing and documentation ZIP | Repository control |
| `docs/` and `.agents/skills/` | Durable project operation/skill context | Maintainer / AI agent |
| Google Sheet | 19 tab curated company and macro research database | Google Drive/Sheets, separate external asset |

## Verifying a snapshot

- Archive should contain the expected latest source files and documentation, not only a README or a stale `yatharth_dashboard.html`.
- Check the embedded `SOURCE_COMMIT.txt` against GitHub Actions run and `SHA256SUMS.txt`; the source ZIP does not automatically track later repository changes.
- Check dated JSON timestamps. "Current as of export" is not "current as of opening the ZIP".
- Confirm private Sheet export is a **separate data artifact** and has not been written into the public repository.

## Future archive hygiene

After major refinements: update this inventory, regenerate source ZIP from a specific commit, export current Sheet privately, and label old screenshots/reports by date. Preserve older analysis in the research history rather than silently altering the narrative.


## 12 November 2026 additions to canonical source ZIP

The current exporter now captures **all six public pages** (Yatharth/company research, Sector Intelligence, Company Price × Volume, Market Desk, News Archive and NIFTY Rotation × Polymarket), the portable root DESIGN.md, and all new assets under assets/:
- equity-ui.css — common lightweight visual tokens and dark/paper themes.
- equity-shell.js — global Research / Markets site navigation and homepage technical research link.
- company-signals.css and company-signals.js — searchable company technical dashboard and shared research shortlist integration.

New source data include watch-universe.json (22 NSE symbols), stock-price-volume.json (dated 20/55-breakout, relative-volume, CMF, OBV and 200-day trend context), and price-volume-history.json (AM/PM snapshots). The Python collector and source/status guards are in scripts/stock_price_volume.py. The new scripts/validate_site.py and quality-gate.yml provide automatic source and UI integrity checks.

Backup automation now runs at **07:00 IST on the first calendar day of each month** and also when the exporter or core documentation/design files change. The ZIP intentionally excludes the private Google Sheet, user account automation definitions, credentials, untracked local working assets and Git history; they are separate external resources.

Source output and formulas are documented by DESIGN.md and docs/REFRESH_AND_TECHNICAL.md.
