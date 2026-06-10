# Quantum Queen EA Strategy Analysis Plan

## Goal

Analyze the Quantum Queen MT5 backtest report together with historical XAUUSD M1/M15 candles to infer approximate information about the EA's embedded strategies, focusing first on:

- **A. Descriptive analysis:** trading sessions, trade/basket behavior, market context, order-management patterns.
- **B. Rule-inference analysis:** approximate, explainable candidate logic for each discovered strategy family.

A later phase may attempt **C. behavioral replication**, but C is explicitly out of scope for the first pass.

## Source Files

- `QuantumQueen_backtest_report.xlsx`
  - MT5 backtest report containing detailed trade records.
- `xauusd_m1_2016_2026.csv`
  - XAUUSD 1-minute candles.
- `xauusd_m15_2016_2025.csv`
  - XAUUSD 15-minute candles.

## Important User-Provided Domain Constraints

1. The EA runs on the **M15 timeframe**.
2. New entries are opened when conditions are met on **M15 bars**.
3. Close/add-on management is evaluated **every minute** after entry.
   - Example: if opened at `00:15`, then conditions may be checked at `00:16`, `00:17`, etc.
   - This should be verified against M1 data.
4. Entry frequency is low.
   - In the last two weeks, the EA opened very few positions.
5. The first project phase should be **A + B**:
   - descriptive analysis and approximate rule inference.
   - potential replication comes later.

## Known Product Context from MQL5 Page

Quantum Queen MT5 is described as:

- A MetaTrader 5 Expert Advisor for XAUUSD / GOLD.
- A low-frequency, high-quality setup system rather than a high-frequency EA.
- A trend-following grid-style trading system.
- An EA with 12 embedded strategies according to product description.
- Designed for hedging accounts.
- Recommended for ECN/RAW/low-spread brokers with 2-decimal XAUUSD quotes.
- Requiring VPS operation for 24/5 management.

Version/page details observed:

- Current version on page: `3.70`.
- Published: `21 June 2024`.
- Updated: `8 June 2026`.
- Version history mentions broker presets, strategy count changes, grid closure improvements, risk-level adjustments, holiday filters, Friday night close behavior, and spread/quote restrictions.

## Analysis Principles

- Do not assume the 12 true internal strategies are directly observable.
- Without source code, conclusions must be expressed as **candidate strategy families** with confidence levels.
- Separate **entry strategy** from **shared position/basket management**.
- Prefer evidence from explicit report fields, if available:
  - Magic number
  - Comment
  - Position ID
  - Order/Deal IDs
  - Strategy-specific labels
- If explicit identifiers are absent, infer strategy families through behavior clustering and explainable features.
- Time alignment between MT5 report and CSV candles must be validated before interpreting sessions.

## Phase 0 — Environment and Data Audit

**Status:** complete

Objectives:

1. Confirm Python analysis environment works.
2. Read Excel workbook sheet names and sample rows.
3. Identify report structure and fields.
4. Confirm whether report contains explicit strategy identifiers:
   - Magic
   - Comment
   - Position ID
   - Deal/Order IDs
5. Confirm symbol, timeframe, date range, number of trades/deals/orders.
6. Confirm M1/M15 CSV date ranges, row counts, missing bars, duplicates, and timezone.

Expected outputs:

- `outputs/data_audit_report.md`
- `outputs/raw_schema_summary.json`

## Phase 1 — Trade Reconstruction and Time Alignment

**Status:** complete

Objectives:

1. Normalize raw report into deal-level records.
2. Reconstruct position-level records.
3. Reconstruct basket/cycle-level records.
4. Detect whether MT5 report timestamps are UTC or broker/server time.
5. Match trade prices to M1 candles under candidate time offsets.
6. Choose and document the best timestamp alignment.

Key checks:

- Does each entry price fall inside nearby M1 high/low?
- Is a constant offset sufficient?
- Is DST-like switching required?
- Are trade times mostly aligned to M15 bars for entries?
- Are closes/add-ons aligned to arbitrary M1 timestamps?

Expected outputs:

- `outputs/trades_normalized.parquet`
- `outputs/positions.parquet`
- `outputs/baskets.parquet`
- `outputs/time_alignment_report.md`

## Phase 2 — Feature Engineering

**Status:** complete

Objectives:

Compute features at deal, position, and basket levels.

### Time/session features

- Entry hour/day/session.
- Exit hour/day/session.
- Weekday.
- Month.
- Friday-specific behavior.
- London, New York, Asia, and overlap sessions.

### Order/basket structure features

- Direction.
- Basket order count.
- Add-on count.
- First entry time and last exit time.
- Holding duration.
- Add-on spacing in price, points, and ATR units.
- Lot sequence and lot growth pattern.
- Basket-level realized PnL.
- MAE/MFE in price and ATR units.
- Whether positions close together or individually.

### Market-context features

Using M15 as primary entry-context timeframe and M1 for management behavior:

- M15 candle shape at/near entry.
- Lookback momentum over 1, 2, 4, 8, 16, and 32 M15 bars.
- ATR / volatility percentile.
- EMA slope and price distance to EMA families.
- Breakout relation to recent highs/lows.
- Pullback relation to trend filters.
- RSI/ADX/MACD-style features, if useful.
- M1 post-entry path for close/add-on verification.
- Spread and tick-volume context.

Deferred/fallback extension if current feature set cannot explain `Sxx` behavior well:

- Add moving-average relationship/crossover-style features:
  - `EMA8 > EMA21`, `EMA21 > EMA50`, stacked bullish/bearish alignment, cross-up/cross-down events, bars since cross.
- Expand beyond current EMA/RSI/ADX/MACD/ATR feature set and do not limit the search to the examples below:
  - SMA, EMA, HMA, WMA, Bollinger Bands, CCI, ADX/DMI, RSI, MACD, ATR, volatility bands, and related slope/distance/crossover variants.
  - Consider the broad universe of public technical indicators exposed by `pandas-ta` / compatible libraries; obscure indicators may be relevant if Quantum Queen uses less common filters.
- Use broader parameter grids, not only common defaults.
- For each explicit `Sxx`, search for candidate indicator/parameter combinations that best separate actual initial entries from non-entry/background M15 bars.
- Treat this as a fallback/Phase 4+ parameter-discovery track if the current compact feature set is insufficient for rule inference.

Expected outputs:

- `outputs/basket_features.parquet`
- `outputs/deal_features.parquet`
- `outputs/feature_dictionary.md`
- `outputs/phase2_feature_report.md`

## Phase 3 — Strategy Candidate Discovery

**Status:** complete

Objectives:

1. First attempt explicit grouping by report identifiers.
2. If no reliable identifiers exist, cluster basket-level behavior.
3. Compare natural clustering with forced 12-cluster views.
4. Identify whether 12 embedded strategies are all active in the report.
5. Distinguish entry families from shared grid/basket management.

Candidate methods:

- Explicit grouping by Magic/Comment/Position ID if available.
- HDBSCAN/DBSCAN-style density clustering if installed/available.
- KMeans/Gaussian Mixture with sensitivity checks.
- Hierarchical clustering for interpretability.
- Dimensionality reduction only for visualization, not as proof.

Expected outputs:

- `outputs/strategy_cluster_assignments.parquet`
- `outputs/strategy_clusters_report.md`
- `outputs/cluster_diagnostics/`

## Phase 4 — Approximate Rule Inference

**Status:** initial compact-feature pass complete

Objectives:

For each candidate strategy family:

1. Describe trading session and frequency.
2. Classify likely strategy type:
   - trend breakout
   - trend pullback
   - momentum continuation
   - mean reversion
   - volatility expansion
   - session-specific strategy
   - grid/basket management behavior
3. Infer approximate entry conditions from M15 features.
4. Infer add-on and close behavior from M1 path after entry.
5. Produce confidence levels and list uncertainty.

Candidate explainability tools:

- Decision tree rules to separate one candidate family from others.
- Feature importance from simple tree/forest models.
- Rule tables based on quantiles and distributions.
- Manual visual checks on representative trades.
- If compact features are insufficient, run expanded indicator/parameter discovery per `Sxx`, including MA crossover/stacking and broader SMA/EMA/HMA/WMA/BBands/CCI/ADX parameter grids.

Expected outputs:

- `outputs/strategy_profiles.md`
- `outputs/strategy_profiles.html` if visualization/reporting is practical.
- Representative trade charts under `outputs/charts/`.

## Phase 5 — Validation and Review

**Status:** pending

Objectives:

1. Validate rules across time splits:
   - discovery period
   - validation period
   - latest period
2. Check false positives:
   - How often do inferred conditions appear without EA entry?
3. Check false negatives:
   - How many actual EA entries are not covered by inferred rules?
4. Manually inspect representative examples for each candidate strategy.
5. Prepare a final A+B report suitable for discussion before any replication attempt.

Expected outputs:

- `outputs/final_ab_analysis_report.md`
- `outputs/final_ab_analysis_report.html` if useful.

## Out of Scope for First Pass

- Full EA replication.
- Producing executable trading strategy code.
- Assuming exact 12 strategies can be recovered without evidence.
- Optimizing a new strategy.
- Making investment recommendations.

## Open Questions

1. Does the Excel report contain Magic/Comment/Position ID fields that reveal strategy identity?
2. What is the report timestamp timezone relative to the UTC CSV files?
3. Is the report generated from a single EA version/preset, or does it mix multiple versions/settings?
4. Are entries exactly aligned to M15 bar opens/closes, or can they occur inside the M15 bar after a condition is confirmed?
5. Are basket close/add-on decisions actually observable at M1 granularity as expected?
6. Do all 12 embedded strategies appear in this backtest, or only a subset?

## Error Log

| Time | Error | Attempt | Resolution |
|------|-------|---------|------------|
| 2026-06-10 | Base Python missing pandas/openpyxl | Tried reading Excel with system Python | User approved using uv environment; dependency installation requires proxy. |
| 2026-06-10 | uv install initially attempted without proxy | Direct package resolution/download | Use `HTTP_PROXY`/`HTTPS_PROXY=http://127.0.0.1:7897` for package installs. |
