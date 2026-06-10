# Quantum Queen EA Analysis Findings

## Project Files

Current project root contains:

- `QuantumQueen_backtest_report.xlsx` — about 2.2 MB.
- `xauusd_m1_2016_2026.csv` — about 236 MB.
- `xauusd_m15_2016_2025.csv` — about 16 MB.

## CSV Schema

Both CSV files have this schema:

```text
time, open, high, low, close, tick_volume, spread, real_volume
```

Sample timestamp format:

```text
2016-01-04 01:00:00+00:00
```

The CSV candle times are timezone-aware UTC strings.

## MQL5 Product Page Findings

Observed page:

```text
https://www.mql5.com/en/market/product/118805?source=External
```

Product:

- Name: `Quantum Queen MT5`
- Platform/category: MetaTrader 5 Expert Advisor.
- Price observed: `1 999.99 USD`.
- Rating observed: `4.98`.
- Author: `Bogdan Ion Puscasu`.
- Product page version: `3.70`.
- Updated: `8 June 2026`.
- Published: `21 June 2024`.
- Activations: `10`.
- Demo downloads observed: `70,834`.

Product claims/context:

- Focuses on XAUUSD/GOLD.
- Described as a low-frequency, high-quality setup EA.
- Described as a trend-following grid system.
- Described as having 12 advanced built-in strategies.
- Works with multiple broker presets/risk sets.
- Recommends ECN/RAW/low-spread brokers.
- Requires 2-decimal price quotation for GOLD.
- Not compatible with 3-decimal GOLD quotes according to the description.
- Requires hedging account type.
- VPS is mandatory for 24/7 operation.

Version-history observations relevant to analysis:

- `3.70` added Friday night close trading time, letting users choose when the EA stops opening new trades on Friday night.
- `3.65` shortened comment length due to possible broker server comment-length limits.
- `3.64` added custom trade comment, individual trading days, and trade direction settings.
- `3.52` made IC Markets/VT Markets RAW Medium Risk the default set and changed lot calculation to automatic by default.
- `3.5` added a high-risk preset with additional trading strategies and up to 40% more trade activity.
- `3.0` reoptimized for gold market conditions, adjusted risk levels, increased strategy count to 10 including London strategies, and added broker presets.
- `2.6` emphasized compatibility only with brokers having 2 decimals for XAUUSD.
- `2.0` redesigned strategies, removed martingale from all strategies, closed internal strategy configurability, and restructured inputs.

## User-Provided Key Constraints

- The EA runs on M15.
- Entries are triggered by M15 conditions.
- Close and add-on conditions are checked every minute after entry.
- Recent entry frequency is low; the last two weeks had very few entries.
- First phase should be A+B:
  - descriptive analysis
  - approximate rule inference
- Later phase may attempt C:
  - behavioral replication / strategy approximation.

## Important Analytical Implications

- Entry analysis should primarily use M15 features.
- Management analysis should use M1 data after each entry.
- M1 data should verify closes and add-ons rather than define primary entry conditions.
- Because entries are low frequency, false-positive analysis is critical: many similar-looking M15 setups may not trigger EA entries.
- Timezone alignment is a gating dependency before any session conclusion.
- Product version history implies not all historical trades necessarily represent the same internal logic if the backtest spans settings/versions; this must be checked from report metadata.


## Devin Context Persistence Hooks

Configured project-level Devin hooks under `.devin/` to preserve Quantum Queen analysis context across compaction and session boundaries.

Files created:

- `.devin/hooks.v1.json`
- `.devin/scripts/context_hooks.py`
- `.planning/context/latest_context.md`
- `.planning/context/restore_after_compaction.md`
- `.planning/context/hook_events.jsonl`
- `.planning/context/compaction_events.jsonl`
- `.planning/context/snapshots/*.md`

Hook events configured:

- `SessionStart`
- `UserPromptSubmit`
- `Stop`
- `SessionEnd`
- `PostCompaction`

Important note:

- Devin documentation exposes `PostCompaction`, but no explicit `PreCompaction` event was found in the current docs.
- To approximate pre-compaction safety, context is snapshotted continuously on user prompts, stops, and session end.
- After compaction, `PostCompaction` snapshots context again, records the compactor summary, and emits restore instructions.

Recovery procedure after compaction:

1. Read `task_plan.md`.
2. Read `findings.md`.
3. Read `progress.md`.
4. Read `.planning/context/latest_context.md`.
5. Continue from the latest incomplete phase in `task_plan.md`.


## Python / uv Analysis Environment

The project is now managed as a uv project:

- `pyproject.toml` created with project name `quantum-queen-research`.
- `uv.lock` created by `uv add`.
- Dependencies installed into the project `.venv`.

Installed analysis dependencies:

- pandas `2.3.3`
- openpyxl `3.1.5`
- numpy `2.2.6`
- scipy `1.15.3`
- scikit-learn `1.7.2`
- polars `1.41.2`
- pyarrow `24.0.0`
- matplotlib `3.10.9`
- seaborn `0.13.2`
- plotly `6.8.0`
- statsmodels `0.14.6`

Use commands like:

```bash
uv --project /Users/fedong/sources/QuantumQueenResearch run python your_script.py
```

Network-dependent `uv add` commands require the local proxy:

```bash
HTTP_PROXY=http://127.0.0.1:7897 HTTPS_PROXY=http://127.0.0.1:7897 \
http_proxy=http://127.0.0.1:7897 https_proxy=http://127.0.0.1:7897 \
uv --project /Users/fedong/sources/QuantumQueenResearch add <packages>
```

## Initial Excel Read Validation

`QuantumQueen_backtest_report.xlsx` can be read with pandas/openpyxl.

Observed workbook structure:

- Sheets: `Sheet1` only.
- First rows indicate this is a Chinese MT5 strategy test report.
- Broker/server line: `EBCFinancialGroupKY-Live01 (Build 5836)`.
- Expert line: `Quantum Queen 3.52(2)`.
- Symbol: `XAUUSD`.

Important implication:

- The analyzed backtest appears to be for EA version `3.52(2)`, not the currently published page version `3.70`. Version-specific behavior must be considered.


## Phase 0 Data Audit Findings

Generated:

- `outputs/data_audit_report.md`
- `outputs/raw_schema_summary.json`
- `scripts/phase0_data_audit.py`

Key findings:

- `QuantumQueen_backtest_report.xlsx` has one sheet: `Sheet1`.
- Main sheet dimensions: 22,707 rows x 15 columns.
- Report metadata shows:
  - Expert: `Quantum Queen 3.52(2)`
  - Symbol: `XAUUSD`
  - Period field: `M15 (2018.01.01 - 2026.06.09)`
  - Magic input: `1234`
  - Set input: `3`
- Orders section starts at Excel row 83; order header at row 84.
- Deals section starts at Excel row 11395; deal header at row 11396.
- Parsed orders: 11,310.
- Parsed XAUUSD deals: 11,310.
- Entry deals: 5,655; exit deals: 5,655.
- Every entry deal has an explicit strategy tag in the comment.

Observed active entry strategy tags:

| Strategy | Entries |
|---|---:|
| `T1/S01` | 1,573 |
| `T2/S03` | 1,063 |
| `T2/S04` | 1,216 |
| `T3/S06` | 324 |
| `T4/S08` | 231 |
| `T5/S09` | 234 |
| `T5/S10` | 360 |
| `T6/S12` | 654 |

Only 8 `S` strategy IDs appear in this report: `S01`, `S03`, `S04`, `S06`, `S08`, `S09`, `S10`, `S12`. The marketed 12 embedded strategies are not all active in this backtest/preset or some generated no entries in the tested period.

Timezone / alignment finding:

- User recalled exported trade-record time is GMT+3.
- Against the provided M1 CSV, best price/time alignment is report time floored to minute with `offset=0h`, not `-3h`.
- All-deal match rate at tolerance 0.25: 99.08% for offset 0.
- Entry-only match rate at tolerance 0.25: 98.27% for offset 0.
- Interpretation: for joining report trades to provided candles, use `broker_time` directly with no shift. If report time is GMT+3, then the provided CSV data should also be treated as the same broker/server clock despite the `+00:00` suffix. For session labeling, keep a derived `utc_time_est = broker_time - 3h` until broker timezone/DST policy is fully confirmed.


## Phase 1 Trade Reconstruction Findings

Generated:

- `scripts/phase1_reconstruct_trades.py`
- `src/qq_research/reconstruction.py`
- `tests/test_reconstruction.py`
- `tests/test_phase1_report.py`
- `outputs/trades_normalized.parquet`
- `outputs/positions.parquet`
- `outputs/baskets.parquet`
- `outputs/time_alignment_report.md`

Key findings:

- Parsed XAUUSD deals: 11,310.
- Entry deals: 5,655.
- Exit deals: 5,655.
- FIFO directional reconstruction creates 6,100 position fragments.
- Reconstructed analytical baskets: 1,657.
- Estimated position PnL exactly matches reported exit-deal profit sum: `1,347,268.41`, difference `0.0`.
- This validates using FIFO matching to assign blank exit comments back to original entry strategy tags.
- M1 alignment remains strong at offset `0h`: all-deal tolerance-0.25 match rate `0.9908`, entry-deal match rate `0.9827`.

Strategy-level reconstructed position summary:

| Strategy | Positions | Baskets | PnL est | Avg hold min |
|---|---:|---:|---:|---:|
| `T1/S01` | 1,769 | 459 | 4,625,172.10 | 484.36 |
| `T2/S03` | 1,193 | 318 | 2,774,986.27 | 369.10 |
| `T2/S04` | 1,231 | 378 | 2,246,850.28 | 200.16 |
| `T3/S06` | 402 | 99 | -14,994,461.54 | 4,445.38 |
| `T4/S08` | 231 | 58 | 1,014,496.77 | 110.87 |
| `T5/S09` | 234 | 71 | 1,520,356.22 | 374.85 |
| `T5/S10` | 386 | 108 | 2,101,890.16 | 624.31 |
| `T6/S12` | 654 | 166 | 2,057,978.15 | 216.66 |

Timing diagnostics:

- All entry deals at broker minute `% 15 == 0`: 38.66%.
- Basket first entries at broker minute `% 15 == 0`: 62.70%.
- Do not conclude yet that M15 entry gating is false. Entry deals include add-ons, and reconstructed baskets are analytical interval groups rather than native EA cycle IDs. Phase 2 should refine initial-entry detection before evaluating the M15-entry hypothesis.

Bug fixed during Phase 1:

- Initial `Seconds Diagnostics` table accidentally double-counted value-count results and displayed impossible seconds like `790`. Added a regression test and fixed report generation to count raw second values.


## Phase 2 Readiness Notes

Phase 2 should start from the Phase 1 parquet outputs:

- `outputs/trades_normalized.parquet`
- `outputs/positions.parquet`
- `outputs/baskets.parquet`

Critical invariants established before Phase 2:

- Strategy labels are explicit on entry deals and preserved through FIFO reconstruction.
- Exit comments are blank, but directional FIFO matching reconstructs strategy attribution exactly at total PnL level.
- Reconstructed position PnL exactly equals reported exit-deal profit total: `1,347,268.41`.
- Use offset `0h` for joining report timestamps to provided M1/M15 CSV candles.
- Treat CSV timestamps as broker/server-time aligned despite their `+00:00` suffix.
- Keep estimated UTC fields for session analysis using `broker_time - 3h`, pending any later DST/server-time refinement.
- Active strategies in this report are: `T1/S01`, `T2/S03`, `T2/S04`, `T3/S06`, `T4/S08`, `T5/S09`, `T5/S10`, `T6/S12`.
- `T3/S06` is a major outlier with large negative reconstructed PnL and long average holding time; prioritize it in later profiling.

Phase 2 should not assume every entry deal is an initial signal. Many entry deals are likely add-ons. Initial-entry detection must be derived carefully from reconstructed positions/baskets and timing/overlap context.

## Phase 2 Feature Engineering Findings

Generated:

- `src/qq_research/features.py`
- `scripts/phase2_feature_engineering.py`
- `tests/test_features.py`
- `tests/test_phase2_report.py`
- `outputs/deal_features.parquet`
- `outputs/basket_features.parquet`
- `outputs/feature_dictionary.md`
- `outputs/phase2_feature_report.md`

Feature table semantics:

- `deal_features.parquet` is reconstructed position / entry-deal level, not raw 11,310 deal-event level. It has one row per FIFO-matched entry-to-exit position fragment and preserves `entry_deal`, `exit_deal`, `strategy`, `T`, `S`, broker-time fields, and estimated UTC session fields.
- `basket_features.parquet` is reconstructed analytical basket/cycle level from Phase 1 basket IDs.

Key generated features:

- Broker and estimated UTC session features. Estimated UTC is still `broker_time - 3h`; candle joins still use broker/report time with `0h` offset.
- M15 entry context features: containing M15 bar shape, lookback momentum, recent high/low breakout relation, ATR/EMA trend context, price location inside the M15 range.
- M15 technical indicators use `pandas-ta-classic`, the installable pandas-ta compatible package available in this environment. Generated columns include RSI, ADX/DMI, MACD, ATR, and EMA-derived fields.
- M1 post-entry path features: path availability, MAE/MFE, net exit move, time-to-MAE/MFE, spread, and tick volume.
- Basket/order-structure features: `is_initial_entry`, `entry_sequence_in_basket`, add-on count, add-on spacing in minutes/price, volume multiplier, close span, and close-together flag.

Validation results:

- `deal_features.parquet`: 6,100 rows x 160 columns, matching `positions.parquet` row count.
- `basket_features.parquet`: 1,657 rows x 154 columns, matching `baskets.parquet` row count.
- M1 path coverage is 100% for deal and basket features.
- Deal-feature PnL sum matches Phase 1 positions within floating-point tolerance (`~3.7e-09` difference). Basket-feature PnL sum matches Phase 1 baskets exactly.
- Initial basket entries at broker minute `% 15 == 0`: `0.6270`.
- All reconstructed position/entry rows at broker minute `% 15 == 0`: `0.3739`.

Important interpretation:

- The initial-entry timing share is the relevant diagnostic for the user's M15-entry hypothesis; all entry rows include add-ons and therefore should not be expected to align to M15 boundaries.
- `T3/S06` remains a priority outlier: Phase 2 report shows much larger average MAE points than other strategies, consistent with Phase 1's large negative PnL and long holding times.

## Phase 3 Strategy Candidate Discovery Findings

Generated:

- `src/qq_research/strategy_discovery.py`
- `scripts/phase3_strategy_discovery.py`
- `tests/test_strategy_discovery.py`
- `outputs/strategy_cluster_assignments.parquet`
- `outputs/strategy_clusters_report.md`
- `outputs/cluster_diagnostics/`

Method:

- Clustered `outputs/basket_features.parquet` at basket/cycle level.
- Explicit `strategy` / `T` / `S` labels were preserved as reference labels, not used as clustering features.
- PnL/profit identifiers, row IDs, exit-time fields, and absolute price levels were excluded from clustering features to avoid outcome leakage, ID leakage, and historical price-regime clustering.
- Features were median-imputed, clipped at 1st/99th percentiles, standardized, then clustered with KMeans for k=2..12.
- Silhouette diagnostics use Manhattan distance because Euclidean pairwise-distance scoring produced sklearn/numpy RuntimeWarnings in this local environment despite finite scaled inputs.

Key results:

- Active explicit strategies in the report remain 8: `T1/S01`, `T2/S03`, `T2/S04`, `T3/S06`, `T4/S08`, `T5/S09`, `T5/S10`, `T6/S12`.
- KMeans natural silhouette choice: `k=3`.
- Forced k=12 assignments were generated for diagnostic comparison only.
- Best-cluster ARI vs explicit `T/S` strategy tags: `0.1690`.
- Best-cluster NMI vs explicit `T/S` strategy tags: `0.3213`.
- Natural clusters do not map cleanly one-to-one to explicit strategies; they appear to capture broad behavior regimes such as longer holds / lower RSI-downtrend context / short-duration momentum-volume behavior rather than exact embedded strategy IDs.
- Cluster 1 is enriched for `T6/S12` and `T3/S06`; this is useful for Phase 4 because `T3/S06` was already the major negative-PnL outlier.

Interpretation:

- Explicit `T/S` labels remain the strongest evidence for active strategy identity.
- The marketed 12 strategies are still not all observed in this backtest; forced 12 clusters should not be interpreted as proof of 12 active strategies.
- Phase 4 should use explicit strategies as supervised reference groups, then use cluster regimes as auxiliary behavioral slices for rule inference.

## Phase 4 Initial Compact-Feature Rule Inference Findings

Generated:

- `src/qq_research/rule_inference.py`
- `scripts/phase4_rule_inference.py`
- `tests/test_rule_inference.py`
- `outputs/strategy_profiles.md`

Scope:

- This is an initial compact-feature pass, not a final exact rule recovery.
- Entry inference uses only `is_initial_entry == True` rows to avoid mixing add-ons into M15 signal context.
- Each explicit strategy `T*/S*` is profiled against other strategies using median/IQR effect-size contrasts for entry context and basket/M1 management features.

Initial candidate classifications from compact features:

| Strategy | Candidate family | Confidence |
|---|---|---|
| `T1/S01` | overbought momentum / trend continuation context | low |
| `T2/S03` | overbought momentum / trend continuation context | low |
| `T2/S04` | overbought momentum / trend continuation context | low |
| `T3/S06` | oversold pullback / downtrend continuation context | low |
| `T4/S08` | trend breakout / momentum continuation | medium |
| `T5/S09` | trend breakout / momentum continuation | medium |
| `T5/S10` | overbought momentum / trend continuation context | low |
| `T6/S12` | downtrend breakout / short momentum continuation | medium |

Notable observations:

- `T3/S06` remains distinct: short-only, low RSI, high negative DMI, below-EMA context, large negative PnL, and wider add-on price spacing.
- `T4/S08` and `T5/S09` show stronger compact-feature evidence for trend breakout / momentum continuation.
- Several long-only strategies (`T1/S01`, `T2/S03`, `T2/S04`, `T5/S10`) share overbought/trend-continuation signatures but have low confidence under the compact feature set, so they are candidates for expanded indicator/parameter discovery.

Next implication:

- Before treating low-confidence profiles as useful rules, run the expanded indicator/parameter-discovery fallback requested by the user if more precise `Sxx` separation is needed.

## Phase 4 Expanded Indicator / Parameter Discovery Findings

Generated:

- `src/qq_research/expanded_indicator_discovery.py`
- `scripts/phase4_expanded_indicator_discovery.py`
- `tests/test_expanded_indicator_discovery.py`
- `outputs/expanded_indicator_discovery_report.md`
- `outputs/expanded_indicator_scores.csv`
- `outputs/expanded_indicator_feature_matrix.parquet` (large local artifact; not intended for lightweight checkpoint commits)

Scope:

- First-pass expanded search over M15 indicators and parameter variants using `pandas-ta-classic` plus explicit MA stacking/crossover features.
- Each feature is scored separately per explicit `Sxx`, comparing unique M15 bars with at least one initial basket entry for that strategy against the M15 background.
- High AUC lift is treated as feature-separation evidence, not proof of the exact EA rule.
- Raw absolute MA levels are excluded to avoid historical price-regime leakage; retained MA features are slope, close-distance, inter-MA spread, stacking booleans, cross events, and bars-since-cross.

Indicator universe:

- `pandas-ta-classic` exposes 305 lowercase callable names in this environment.
- First-pass computed families include MA slope/distance/spread/stacking/cross, RSI, CCI, CMO, ROC, MOM, ADX/DMI, AROON, Bollinger Bands, Donchian, Keltner Channels, CHOP, Fisher, AO, BOP, CMF, and EFI.
- This is broader than compact Phase 4 but still not exhaustive; more pandas-ta families can be added in later passes.

Top single-feature separators by strategy:

| Strategy | Top feature | Direction | AUC lift |
|---|---|---|---:|
| `T1/S01` | `fisher_14` | high | 0.3970 |
| `T2/S03` | `wma_21_minus_wma_50` | high | 0.4401 |
| `T2/S04` | `roc_20` | high | 0.4581 |
| `T3/S06` | `rsi_34` | low | 0.4455 |
| `T4/S08` | `rsi_34` | high | 0.4666 |
| `T5/S09` | `fisher_9` | high | 0.4723 |
| `T5/S10` | `fisher_9` | high | 0.3509 |
| `T6/S12` | `adx_7_dmp_7` | low | 0.4471 |

Interpretation:

- Expanded indicators improve separation for several previously low-confidence strategies.
- MA spread/slope features appear prominently for `T2/S03`, `T2/S04`, `T3/S06`, `T4/S08`, and others, supporting the user's hypothesis that crossover/stacking-like features may matter.
- Fisher/CMO/RSI/ADX-family features are frequent top candidates, so small or less-mainstream public indicators may be relevant.
- Next step should combine top features into multi-condition candidate rules and evaluate false positives/false negatives, rather than relying on single-feature AUC alone.

## Phase 4 Candidate Multi-Condition Rule Mining Findings

Generated:

- `src/qq_research/rule_mining.py`
- `scripts/phase4_candidate_rule_mining.py`
- `tests/test_rule_mining.py`
- `outputs/candidate_rule_combinations.csv`
- `outputs/candidate_rule_combinations.md`

Method:

- Uses top expanded single-feature candidates per `Sxx`.
- Builds 1-, 2-, and 3-condition AND rules using each feature's positive-entry median as threshold.
- Evaluates each rule against all M15 background bars with precision, recall, and precision lift vs base entry rate.
- These rules are hypotheses, not confirmed source rules.

Top candidate rule per strategy:

| Strategy | Top displayed rule | Precision | Lift vs base | Recall |
|---|---|---:|---:|---:|
| `T1/S01` | `fisher_9 >= 2.6333` | 0.0202 | 7.7x | 0.5013 |
| `T2/S03` | `wma_21_minus_wma_50 >= 4.9460 AND mom_34 >= 15.8350 AND sma_21_minus_sma_50 >= 6.5777` | 0.0474 | 21.3x | 0.4434 |
| `T2/S04` | `roc_20 >= 0.8012 AND wma_21_minus_wma_50 >= 5.2581` | 0.0686 | 26.0x | 0.4233 |
| `T3/S06` | `adx_21_dmp_21 <= 11.1566 AND ema_21_minus_ema_50 <= -4.5039` | 0.0138 | 23.8x | 0.3373 |
| `T4/S08` | `close_minus_ema_50 >= 16.0722 AND adx_21_adx_21 >= 47.5722 AND sma_50_slope_4 >= 2.2950` | 0.0859 | 261.5x | 0.2979 |
| `T5/S09` | `fisher_14 >= 4.0160 AND adx_7_adx_7 >= 68.9157` | 0.0356 | 76.1x | 0.3881 |
| `T5/S10` | `fisher_9 >= 2.7380 AND chop_14 <= 38.1306 AND sma_8_minus_sma_21 >= 2.3579` | 0.0110 | 15.1x | 0.2885 |
| `T6/S12` | `adx_7_dmp_7 <= 4.7437 AND cci_20 <= -174.5160` | 0.0421 | 37.9x | 0.3208 |

Interpretation:

- Absolute precision remains low because initial-entry bars are extremely sparse relative to all M15 bars.
- Precision lift vs base-rate is more informative for this discovery pass.
- `T4/S08` has the strongest narrow-rule lift among top candidates, consistent with its clearer compact trend-breakout profile.
- Rules should next be validated with time/session filters and direction-specific false-positive analysis before being treated as actionable approximate strategy rules.
