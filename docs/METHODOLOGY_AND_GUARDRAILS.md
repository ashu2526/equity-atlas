# Investment-research methods, formulas and non-negotiable interpretation rules

Updated 2026-11-11. This document describes the **implemented calculation semantics** and places where interpretation is provisional. In particular, avoid the false equivalence of "upward index returns = institutional inflows".

## 1. Three-month NSE NIFTY sector rotation

Implementation: `scripts/sector_rotation.py` → `data/market-signals/sector-rotation.json` → `signals.html#sector`.

**Source hierarchy:** official `https://nsearchives.nseindia.com/content/indices/ind_close_all_DDMMYYYY.csv` daily closing-index-value snapshots, parsed by index name; if the series has inadequate historical coverage and an individual index mirror exists, a **separately labelled** Yahoo Finance daily chart fallback is attempted. Unavailable data stays null. The collector keeps local daily histories and tries recent missing days. The initial backfill observed **82 official daily snapshots** and covered **19 sectors**, with no fallback needed.

**Date logic:** look at the latest available index close per series; choose the last close on or before the date approximately 7 / 30 / 60 / 91 calendar days prior; if the match is more than 12 calendar days away, no comparison is produced. This is **not** exactly 5/21/63 trading sessions. On non-trading days the latest preceding close is used. Date mismatch, stale series and index changes may cause a status warning.

For index `i`, last valid close `P_i(t)`, earlier close `P_i(t-n)`:

```text
r7d_i = 100 × (P_i(t) / P_i(t-7 calendar days)  - 1)
r1m_i = 100 × (P_i(t) / P_i(t-30 calendar days) - 1)
r3m_i = 100 × (P_i(t) / P_i(t-91 calendar days) - 1)
rPrev1m_i = 100 × (P_i(t-30) / P_i(t-60) - 1)
relative3mPp_i = r3m_i - r3m_NIFTY50       [percentage points]
relative1mPp_i = r1m_i - r1m_NIFTY50       [percentage points]
momentumAccelerationPp_i = r1m_i - rPrev1m_i
```

A positive 3-month relative return measures **relative price leadership**. A positive acceleration says the **latest price-return window** has improved against the prior window; neither measures actual net inflows, share ownership, valuation attractiveness or earnings revisions. The ranking sorts 3m relative return (with alternative user-selectable sort by 3m absolute, 1m or acceleration).

**Rotation labels** are simple combinations of relative 3m/1m performance and acceleration:
- Leading & accelerating: 3m above benchmark, 1m above benchmark, acceleration positive.
- Leading, momentum cooling: 3m above benchmark, acceleration negative.
- Lagging, early rebound: 3m below benchmark, acceleration positive.
- Lagging benchmark: 3m below benchmark without positive acceleration.
- Otherwise mixed/no clear trend or insufficient history.

Index observations here are **price indices** (cash dividends not reinvested). The NIFTY 50 and selected sector paths are displayed rebased to 100 on aligned dates; they do not share starting nominal price. Index-methodology changes and survivorship must be considered for deep studies.

### Sample snapshot, not a future forecast

For the close dated 11 Nov 2026: `NIFTY 50 r3m=+3.35%`, `NIFTY Media +9.55% (+6.20pp relative)`, `NIFTY Private Bank +9.26% (+5.91pp)`, `NIFTY Pharma +7.53% (+4.18pp)`, `NIFTY Bank +5.02% (+1.67pp)`, `NIFTY Auto -2.86% (-6.21pp)`. These are **dated price calculations**, not today's prices or investments. See the JSON for all 19 sectors and per-index source.

### How to responsibly use the trend

Use momentum to **generate research hypotheses**:
1. Compare 3m relative leadership against latest 1m/7d direction.
2. Check breadth (constituents making new highs, percentage beating benchmark) — **not yet implemented**.
3. Compare lagged NSDL sector FPI transactions, domestic fund holdings, genuine corporate flows — **mostly not yet automated**.
4. Investigate actual earnings revisions, realised sector profit drivers, and valuation dispersion — **not yet systematically integrated**.
5. Separate structural sector growth from temporary price enthusiasm. Strong momentum alone is not a buy instruction.

## 2. "Smart money": six very different things

| Indicator | What it really measures | Required caveat |
|---|---|---|
| NSE provisional daily FII/DII | Daily **aggregate** cash-market net institutional buying or selling | Cannot reveal same-day sector purchases |
| NSDL fortnightly FPI sector data | Sector-wise foreign portfolio transactions/holdings within published period | Dated with lag; do not conflate with latest daily cash transactions or index returns |
| AMFI monthly flows | Mutual-fund subscriptions/redemptions in relevant categories | Not directly fund-by-fund stock or sector purchases |
| US Treasury TIC | Cross-border securities flow/position estimates, often monthly and methodology-specific | Not identical to country ETF net flows or domestic sector capital |
| CFTC COT | Participant categories' futures positions, generally weekly | Futures positioning is not equity-sector cash buying |
| Sector index/ETF price | Market price return and relative leadership | **Not a flow measure at all** |

A 10% NIFTY sector price rise neither proves ₹X of inflows nor proves foreign ownership increased. Institutional capital can sell into rising prices, and companies can rally through earnings, short covering or small marginal flows.

The `flows.json` schema requires each claim to include `geography`, `scope`, `segment`, `periodStart`, `periodEnd`, `frequency`, `unit`, `value`, `direction`, `dataTier`, `interpretation`, `sourceUrl` and `primarySourceUrl`. Leave `value:null` when a precise amount was not independently checked.

The initial nine observations are illustrative, not a continuously current global smart-money terminal. More sophisticated flow conclusions need holdings, normalized funds-in/out and jurisdiction/FX treatment.

## 3. RSS title-only sentiment vs actual market regime

Implementation: `scripts/rss_scan.py` + `scripts/build_regime_pulse.py`.

Selected public RSS sources yield **headlines and article links**, not verified article full text. The current monitor has 15 configured feeds and 16 topic regex families, with high-risk credit/large-company tags requiring credit/debt context (not simply mentioning "JPMorgan" or "Nvidia"). Link URLs are hashed for deduplication; multiple topic tags may apply.

Title tone uses a small transparent list of **positive/negative words**. Let each title score (v) be +1, −1 or 0 based on positive vs negative tokens. In a 14-day window the pulse computes:

```text
For publisher domain d:    μ_d = mean(title scores for items at d)
Headline language index = round(100 × mean(μ_d over publisher domains), 1)
```

This source-balancing reduces domination by prolific publishers but **does not produce a statistically calibrated equity market sentiment score**. It ignores sarcasm, article meaning, bad-news-is-good-news rate expectations, semantic polarity of oil prices, language bias and price/earnings evidence.

A category label is issued only with at least 8 headlines, at least 3 publisher domains and no source above 75% of titles. Otherwise **"Insufficient observations"**. For eligible coverage:
- above +17: "Mostly positive headline language"
- below −17: "Mostly negative headline language"
- between: "Mixed headline language"

**A real market regime** would instead need sustained confirmation from price leadership/breadth, central-bank/credit spreads, earnings revisions, actual flows, volatility and commodities, as well as source-verified events. The current `marketRegime` field explicitly says **unconfirmed** in the mechanical data. A separate dated AI reviewed assessment can say "selectively constructive" with its own confidence and contradictions.

Comparison to a previous 14 days is withheld until coverage and scan history exist. An old publication date appearing in a newly fetched RSS item **does not prove that the archive captured all prior news**.

## 4. Automated high-impact headline feed

Implementation: `scripts/build_intelligence_feed.py` → `data/news/ranked-feed.json`.

The heuristic scores headlines by:
- keyword materiality (e.g. actual default, geopolitical conflict, policy, tariffs, earnings, energy, institutional flows);
- monitored topic tags (credit/India/trade given extra attention);
- small publisher-source bonus;
- recency (within 24h, 48h, 4d, 7d, older);
- limited cross-publisher cluster reinforcement.

Short titles are grouped into approximate event clusters by topic intersection, within four days, and word-set Jaccard similarity ≥ 0.53. Each event card displays **why it may matter** and direct/second-order exposures from the *dated* editorial theme map.

The ranking is **machine triage of unverified title links**, not an analyst-certified severity score. Grouping can miss synonyms, combine adjacent but distinct developments or reflect repeated coverage by one outlet. Metadata from related events is not evidence that all reports describe the exact same economic fact. No capital flow is inferred.

## 5. Polymarket read-only global event signals

Implementation: `scripts/polymarket_monitor.py` → `data/market-signals/polymarket.json`, `polymarket-history.json` → `signals.html#odds`.

**Source:** public unauthenticated Polymarket Gamma API:
`https://gamma-api.polymarket.com/events?active=true&closed=false&order=volume24hr&ascending=false&limit=50&offset=...`
with up to 400 top-volume events sampled, limited to macro/policy/rates/war/oil/AI/credit regex topics. Sports/entertainment are filtered out. An event may contain multiple markets; the collector selects only active unresolved **binary YES/NO** markets with plausible `outcomePrices`. Total/24h volume thresholds currently require at least $250 in 24h or $10,000 lifetime where available; outputs are capped at 80 selected contracts. Input cases that don't parse or lack a reliable YES outcome are skipped.

```text
impliedYesPercent = 100 × YES outcome price
changeSinceLastSnapshotPp = 100 × (today YES price − prior saved YES price)
```

That quote is **not** guaranteed to be a well-calibrated probability of the real event. Liquidity, spreads, contract wording, settlement source, fees, manipulation and selection all matter. Previous-snapshot change is not the same as exactly 24-hour change (the run gap varies). Related events can overlap: summing probabilities across markets is invalid without explicit mutually exclusive outcomes.

The market activity figure here is **prediction-contract trading**, not corporate debt, equity or fund allocation. There is **no wallet, trading bot, authentication or execution integration**. Refuse to turn this into an investment recommendation by itself.

**News × Event Odds** joins title/topic overlap from the ranked news archive to the category of a Polymarket contract, not semantic full-event validation. If the title cannot be matched, display no relation. A false thematic match is a research lead, not a factual link.

## 6. Company and sector analysis

**Original Yatharth dashboard:** quarterly values and forward scenarios from dated inputs. Keep observed results separate from consensus, research assumptions and scenarios; document EBITDA margin, capex/unit economics, dilution, earnings vs cashflow, hospital operating-bed ramp, ARPOB, occupancy, case mix and ROIC.

**Sector intelligence:** hospitals and tyres require different profit engines:
- Hospitals: maturity of hospitals/bed ramp, occupancy, ARPOB, specialty mix, doctor costs, payer/tariffs, insurance, EBITDA per operating bed, cash returns and valuation relative to unit maturity.
- Tyres: OEM versus replacement and export mix, natural/synthetic rubber, carbon black/oil linkage, product specialist vs scale player, channel inventory, currency, pricing lag, working capital and installed capacity.

A sector-specific **research score** can prioritize questions but is not automatically an investable return forecast. For a head-to-head thesis, demand a common period and correct peer business-model comparison, then rank quality, economics, balance sheet, valuation and *risk-adjusted* upside with sources.

## 7. Failure, uncertainty and change policy

- API failed: preserve last snapshot and show `dataStatus`/time; don't turn errors into zero price.
- Stale snapshot: show published time and suppress "live" language.
- Missing issuer CDS spreads: show "not connected" and an explicitly different FRED HY OAS proxy if helpful.
- Unverified story: link source and label title-only until fact-checked.
- Forecast/event/flow conflicts: show both dates/definitions, not a fake reconciliation.
- Research updates: append or replace only the same-day same-ID item; preserve past opinions to evaluate prediction quality.
- Sector ranking: do not declare "smart money moved" solely because a rotation chart has a green line.

Source URLs are stored in the JSON alongside each relevant observation. External web content remains untrusted.
