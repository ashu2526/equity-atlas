---
name: Equity Atlas
version: 2026-11-12
design_reference:
  - https://open-design.ai/plugins/example-trading-analysis-dashboard-template/
  - https://open-design.ai/plugins/design-system-dashboard/
  - https://open-design.ai/design-system/
purpose: Lightweight, extensible, evidence-first investment-research interface
visual_style: Calm financial research desk, rich data without noise
colors:
  background: "#09131d"
  surface: "#112331"
  raised: "#173145"
  border: "#2d4b5e"
  text: "#eef6f9"
  muted: "#a9c2cf"
  accent: "#5ce0bf"
  warning: "#f4c77b"
layout:
  navigation: Grouped Research / Markets top bar + contextual sidebar
  density: Compact
  rhythm: 4/8/12/16/24 px
  radius: 9/13/18 px
  max_content_width: 1680 px
type:
  body: System UI, no network font
  body_size: 14 px
  section_heading: 18-24 px
  page_title: 29-43 px
---

# Equity Atlas — product design system

## Source and decision

We reviewed the OpenDesign trading-analysis dashboard template, the OpenDesign dashboard design-system reference and its reusable DESIGN.md methodology. Those references prioritize information density, consistent component tokens, real chart interactions, a simple sidebar, and light/dark selection. **Equity Atlas uses an original implementation** inspired by those principles. We did not copy the template or introduce Electron, frameworks, heavy chart libraries or remote fonts. The site stays static HTML+CSS+JavaScript, with machine-readable public JSON snapshots.

Reference pages:
- https://open-design.ai/plugins/example-trading-analysis-dashboard-template/
- https://open-design.ai/plugins/design-system-dashboard/
- https://open-design.ai/design-system/

## User journey and page taxonomy

Think like a research analyst rather than a day trader. Use an information hierarchy: **What changed? → Is the signal real? → Which sectors benefit? → Which company economics follow? → What price/valuation is justified?**

**RESEARCH**
- **Company Research** — `index.html`, existing Yatharth baseline, financial/forecast/decision views; later generalized company route.
- **Sector Intelligence** — `sector-intelligence.html`, unit economics, sector-specific playbooks, peers, scoring and valuation evidence.
- **Price × Volume** — `company-signals.html`, 22-company technical watch, only source-backed abnormal-volume / trend-reversal events; links back to valuation research.

**MARKETS**
- **Morning Intelligence** — `market-desk.html`, sourced AI-reviewed 07:25/19:25 update, money flows vs price, risks and opportunities.
- **Rotation × Odds** — `signals.html`, 1/3-month Indian NIFTY relative price performance plus Polymarket read-only binary event quotes.
- **News Archive** — `news-radar.html`, historical source events, coverage comparisons, theme transmission and regime methodology.

A universal top navigation is injected by `assets/equity-shell.js` and all pages import `assets/equity-ui.css`. Contextual sidebars keep local sub-tabs. The top nav provides plain `<a href>` links (no fake buttons) so navigation stays reliable after returning home. Future page additions require adding one entry to `PAGES` and following shared styling.

## Visual hierarchy

1. **Top global nav:** Grouped Research/Markets links, active-state semantics and data-collection refresh targets. Compact even on small screens.
2. **Page title + published timestamp:** Legible purpose, last source date, and scope. A stale review cannot silently look like today's.
3. **Few high-value KPIs:** 3–4 counters summarizing *verified* coverage. A number needs units/source/period.
4. **Primary research area:** Searchable detailed table/list plus context panel; one click changes content; chart shows period and comparison baseline.
5. **Alerts, not decorations:** Surface unusual breakout+volume, distribution and long-run conflict only after rules trigger; show evidence, confirm and invalidate.
6. **Details on demand:** Additional indicators, reference sources and full methodology are available without overwhelming the opening screen.

Use dark neutrals and aqua accent for research focus, amber for caution, muted steel for supporting information. Avoid bright success green as a blanket buy signal. Keep the background restrained; no meaningless 3D effects, hero image downloads, animated tickers or flash banners.

## Typography and motion

- Use device system fonts. No Google Fonts download.
- 14px regular text and 11–12px source metadata; financial values use tabular numerals.
- Headings 18–24px for sections; 29–43px page heading. Avoid gratuitous giant headings.
- Use an 8px-based spatial rhythm where possible. Borders and grouping establish hierarchy, not excessive shadows.
- No background motion. Small :hover transitions are decorative only. Respect `prefers-reduced-motion`.

## Colors and dark/paper modes

Shared tokens live in `assets/equity-ui.css`: `--ea-bg`, `--ea-surface`, `--ea-raised`, `--ea-border`, `--ea-ink`, `--ea-subtle`, `--ea-accent`, `--ea-focus`.

An optional **Paper** mode changes known legacy dark panels to light backgrounds using `html[data-atlas-theme=paper]`. It is user-local and saved with `localStorage('equity-atlas-theme')`. Dark is the default. Future panels must use shared semantic tokens for both themes rather than hard-code text colors.

## Tables and charts

- Rows should permit quick scanning and sort/filter only where it adds decisions.
- Show *source as-of* and methodology next to rank, not buried at bottom.
- NIFTY rotation: show relative price return vs NIFTY 50 and the contrast with recent 1m acceleration. No smart-money claim from price alone.
- Company technical: combine daily close line and daily traded share-volume bars in one SVG; current SMA reference levels, short/medium/long selection (20/60/120 bars).
- Polymarket: exact question and event link must come before YES contract price; volume and liquidity are betting-market values.
- Financial/hospital valuation: compare scenarios/peers on correct fiscal time frame, show enterprise/equity distinction and sourcing.

Native SVG and HTML replace heavy chart libraries for current scope. Avoid adding multiple animation/tooltips frameworks; use native `<title>` descriptions or light JS if truly needed.

## Accessibility and mobile

- Every global navigation item is a real anchor; active page uses `aria-current=page`.
- Add skip link and strong `:focus-visible` outlines; do not rely only on color.
- Resize or horizontally scroll dense tables without clipping the main page.
- Hide excessive secondary metadata under 620px while retaining source/status and essential controls.
- Clicks on module sidebar must change the **actual content section**, not just active CSS. Regression test the Signal Lab .sigview class mismatch.
- Avoid "live" badges when GitHub data files have older source dates or an AI task missed publication.

## Lightweight performance contract

- Pure static assets: one shared <10KB CSS layer, one <6KB cross-page nav script, and focused page-specific code.
- No npm runtime, Webpack, React, external web fonts, external stock tickers loaded in browser or Polymarket trading wallets.
- Data collection occurs on GitHub Actions twice daily, not individually for each website visitor.
- The browser uses versioned cache-bypass JSON fetches when the user explicitly refreshes; the normal page loads a single snapshot.
- Keep mobile navigation responsive; lazy-load new expensive charts when future modules increase.

## Future scaling pattern

Each additional company should extend:
1. the editable company/peer research rows and review ownership;
2. `data/market-signals/watch-universe.json` for automated technical surveillance;
3. independently sourced valuation assumptions and quarterly history;
4. optional company-specific narrative/alert screens;
5. monthly review accountability.

Avoid creating one new giant copied HTML file for every company. A future data-driven company-detail route should reuse the same component contract and support `?ticker=SYMBOL` or hash deep links.

## Caution

The visual layer must never mislead the investor about evidence. A Polymarket quote, source article headline, relative NIFTY index price return, volume spike and audited company cash flow are five distinct observations. The UI should make that distinction intuitively obvious.
