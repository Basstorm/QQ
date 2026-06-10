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

## Phase 4 Temporal and Matched-Negative Validation Findings

Generated:

- `src/qq_research/temporal_validation.py`
- `scripts/phase4_temporal_validation.py`
- `tests/test_temporal_validation.py`
- `outputs/temporal_rule_validation.csv`
- `outputs/temporal_train_feature_scores.csv`
- `outputs/temporal_rule_validation.md`

Method:

- Uses split time `2021-01-01` because it gives the most balanced train/test positive counts among checked yearly splits.
- Rules are mined only on train rows before the split, then evaluated unchanged on test rows at/after the split.
- Two validation modes are reported:
  - `all_background`: compare entries with all M15 bars in the period.
  - `matched_hour_weekday`: compare entries with non-entry bars from the same broker weekday/hour contexts.
- Matched mode is stricter but can produce very small matched counts for sparse strategies; always inspect `Test matched` before trusting a high lift.

Positive sample counts:

| Strategy | Train positives | Test positives |
|---|---:|---:|
| `T1/S01` | 196 | 181 |
| `T2/S03` | 153 | 165 |
| `T2/S04` | 187 | 191 |
| `T3/S06` | 42 | 41 |
| `T4/S08` | 28 | 19 |
| `T5/S09` | 38 | 29 |
| `T5/S10` | 57 | 47 |
| `T6/S12` | 92 | 67 |

Top all-background train/test-stable signals:

| Strategy | Example rule | Train lift | Test lift | Test recall |
|---|---|---:|---:|---:|
| `T1/S01` | `fisher_9 + wma_21_slope_4 + ema_8_slope_4` | 9.6x | 9.0x | 0.425 |
| `T2/S03` | `wma_21_minus_wma_50 + ao + roc_34` | 15.2x | 15.6x | 0.564 |
| `T2/S04` | `roc_20 + wma_21_minus_wma_50 + wma_21_slope_4` | 27.2x | 26.0x | 0.487 |
| `T3/S06` | `rsi_34 low + ema_21_minus_ema_50 low + wma_50_slope_4 low` | 24.8x | 13.7x | 0.366 |
| `T5/S10` | `fisher_14 + wma_8_minus_wma_21 + adx_7` | 10.8x | 10.8x | 0.383 |
| `T6/S12` | `adx_7_dmp low + cci_20 low + cmo_9 low` | 53.8x | 36.8x | 0.164 |

Key interpretation:

- `T2/S03` and `T2/S04` look materially stronger after temporal validation: MA spread/slope plus momentum features retain similar train/test lifts and decent test recall.
- `T1/S01` and `T5/S10` retain modest but stable train/test lift; they remain broader momentum/oscillator-context rules, not precise entries.
- `T3/S06` and `T6/S12` retain bearish/short-side validation signals, but `T3/S06` still has low absolute precision and small positive counts.
- `T4/S08` and `T5/S09` show high lift but weak test recall and very small matched-mode test matched counts; treat them as sparse-rule hints, not robust rule recovery.

## Phase 4 Final Approximate Strategy Rule Synthesis

Generated:

- `src/qq_research/strategy_synthesis.py`
- `scripts/phase4_strategy_synthesis.py`
- `tests/test_strategy_synthesis.py`
- `outputs/strategy_rule_synthesis.csv`
- `outputs/strategy_rule_synthesis.md`

Method:

- Combines compact strategy family profiles with temporal validation results.
- Temporal validation has the highest weight; full-sample candidate rules without temporal support are not treated as robust.
- Confidence labels:
  - `robust`: strong test lift, useful recall, and sufficient test matches.
  - `moderate`: stable but less precise or less broad.
  - `tentative`: useful signal but low recall or small matched count.
  - `sparse_hint`: high lift but too few matches / too little recall.

Final synthesized confidence:

| Strategy | Family | Confidence | Main validated signal |
|---|---|---|---|
| `T1/S01` | overbought momentum / trend continuation | moderate | Fisher + rising WMA/EMA slopes; matched CCI/ADX bullish pressure filter |
| `T2/S03` | overbought momentum / trend continuation | robust | WMA21-WMA50 spread + AO/ROC or MA slopes |
| `T2/S04` | overbought momentum / trend continuation | robust | ROC20/ROC34 + WMA spread + MA slope, with weak negative DMI |
| `T3/S06` | oversold/downtrend continuation | moderate | RSI low + bearish EMA/WMA slope; matched negative DMI pressure |
| `T4/S08` | trend breakout / momentum continuation | sparse_hint | very strong ADX/EMA-distance breakout but only sparse test matches |
| `T5/S09` | trend breakout / momentum continuation | tentative | Fisher/ADX/CMO high momentum, but weak test recall and sparse matched validation |
| `T5/S10` | overbought momentum / trend continuation | robust | Fisher + short MA slope/spread, stable especially in matched-context validation |
| `T6/S12` | downtrend breakout / short momentum continuation | tentative | low DMP + negative CCI/CMO bearish momentum, but low recall/matched count |

Interpretation:

- The strongest recoverable initial-entry families are `T2/S03`, `T2/S04`, and `T5/S10`.
- `T1/S01` is directionally stable but broader and less precise.
- `T3/S06` and `T6/S12` appear to be bearish/short-side contexts, but sample size limits precision.
- `T4/S08` and `T5/S09` remain sparse high-momentum breakout hints; do not treat their thresholds as robust source-rule recovery.
- This synthesis is still approximate behavioral reverse engineering, not EA source-code recovery.

## Phase 4 Robust Rule Vectorbt Smoke Backtest

Generated:

- `src/qq_research/robust_vectorbt_backtest.py`
- `scripts/phase4_robust_vectorbt_backtest.py`
- `tests/test_robust_vectorbt_backtest.py`
- `outputs/robust_vectorbt_backtest.csv`
- `outputs/robust_vectorbt_backtest.md`

Method:

- Added `vectorbt` dependency.
- Backtested the three `robust` synthesized strategy families: `T2/S03`, `T2/S04`, and `T5/S10`.
- Uses M15 close data only.
- Long-only, one-unit position sizing, no fees/slippage.
- Entry occurs when a robust rule mask changes from false to true.
- Exit occurs when the same rule mask changes from true to false.
- This intentionally excludes Quantum Queen grid/add-on management, inferred TP/SL, and basket-level exit logic.

Results:

| Strategy | Variant | Return % | Max DD % | Sharpe | Trades | Win rate % |
|---|---|---:|---:|---:|---:|---:|
| `T2/S03` | `all_background` | 1.65 | -1.47 | 0.46 | 494 | 36.44 |
| `T2/S03` | `matched_context` | 1.14 | -1.97 | 0.31 | 445 | 41.80 |
| `T2/S04` | `all_background` | -0.75 | -1.86 | -0.26 | 353 | 36.83 |
| `T2/S04` | `matched_context` | 0.01 | -1.00 | 0.01 | 269 | 37.17 |
| `T5/S10` | `all_background` | 0.12 | -1.66 | 0.05 | 841 | 38.76 |
| `T5/S10` | `matched_context` | -1.68 | -2.33 | -0.49 | 1459 | 37.77 |

Interpretation:

- The robust entry contexts do not become strong standalone long-only strategies when exited simply on rule deactivation.
- `T2/S03` is the only clearly positive simple-rule variant in this smoke test, but the edge is small.
- `T2/S04` was robust as an entry classifier, but its naive rule-on/rule-off trade management is near flat to negative.
- `T5/S10` matched-context rule is a strong entry-bar classifier but overtrades and loses under naive exits.
- This supports the hypothesis that Quantum Queen's performance depends heavily on basket/grid/TP management and/or additional exit filters; initial-entry filters alone are not enough to reproduce EA returns.

## Phase 5 Basket Lifecycle Management Diagnostics

Generated:

- `src/qq_research/lifecycle_management.py`
- `scripts/phase5_lifecycle_management.py`
- `tests/test_lifecycle_management.py`
- `outputs/lifecycle_add_on_events.parquet`
- `outputs/lifecycle_exit_events.parquet`
- `outputs/basket_minute_lifecycle.parquet`
- `outputs/lifecycle_management_report.md`

Purpose:

- Shift focus from initial-entry filters to QQ's high-win-rate basket management.
- Entry filters remain approximated by the robust Phase 4 rules for now.
- Phase 5 first pass reconstructs add-on, exit, and active M1 basket state features from actual QQ trades.

Generated datasets:

- Add-on events: 4,443 total.
- Delayed/grid add-on events: 1,215 after excluding same-minute add-ons/splits.
- Exit events / baskets: 1,657.
- Active basket-minute lifecycle rows: 240,987.
- Lifecycle includes `pre_open_*` fields so add-on trigger inference can use the basket state before a new layer opens in that minute.

Key counts and win rates:

| Strategy | Baskets | Same-minute add-ons | Delayed add-ons | Basket win rate % | Median basket PnL |
|---|---:|---:|---:|---:|---:|
| `T1/S01` | 459 | 942 | 368 | 98.47 | 1096.16 |
| `T2/S03` | 318 | 663 | 212 | 97.80 | 991.42 |
| `T2/S04` | 378 | 623 | 230 | 99.47 | 877.52 |
| `T3/S06` | 99 | 243 | 60 | 98.99 | 854.70 |
| `T4/S08` | 58 | 98 | 75 | 100.00 | 2718.45 |
| `T5/S09` | 71 | 119 | 44 | 100.00 | 2265.12 |
| `T5/S10` | 108 | 223 | 55 | 88.89 | 499.48 |
| `T6/S12` | 166 | 317 | 171 | 100.00 | 1382.38 |

Delayed/grid add-on adverse spacing from previous entry, median points:

| Strategy | Median adverse spacing |
|---|---:|
| `T1/S01` | 1.64 |
| `T2/S03` | 1.62 |
| `T2/S04` | 1.68 |
| `T3/S06` | 3.20 |
| `T4/S08` | 1.80 |
| `T5/S09` | 5.41 |
| `T5/S10` | 3.14 |
| `T6/S12` | 2.24 |

Exit move from basket entry VWAP, median points:

| Strategy | Median exit move from VWAP |
|---|---:|
| `T1/S01` | 0.71 |
| `T2/S03` | 0.68 |
| `T2/S04` | 0.66 |
| `T3/S06` | 0.65 |
| `T4/S08` | 1.70 |
| `T5/S09` | 2.25 |
| `T5/S10` | 2.05 |
| `T6/S12` | 1.20 |

Interpretation:

- QQ's very high basket win rate is real in reconstructed data and strongly supports prioritizing basket management inference.
- A large share of add-ons are same-minute splits or simultaneous layer opens; true grid add-ons should be studied using delayed add-ons only.
- The main T1/T2/T3 families have tight delayed spacing around ~1.6 or ~3.2 XAUUSD points, while T5/S09 uses much wider spacing around ~5.4 points.
- Exit behavior appears close to small positive basket-VWAP TP thresholds for T1/T2/T3 (~0.65-0.71 points) and larger thresholds for T4/T5/T6 families.
- Next step should mine per-minute add-on and exit classifier rules from `basket_minute_lifecycle.parquet`, using `pre_open_*` for add-ons and `open_*` state for exits.

## Phase 5 Add-on Trigger Threshold Mining

Generated:

- `src/qq_research/add_on_trigger_mining.py`
- `scripts/phase5_add_on_trigger_mining.py`
- `tests/test_add_on_trigger_mining.py`
- `outputs/add_on_trigger_thresholds.csv`
- `outputs/add_on_trigger_thresholds.md`

Method:

- Uses `basket_minute_lifecycle.parquet` rows with `pre_open_layer_count > 0`.
- Positive labels are delayed/grid add-on minutes with an existing basket state.
- Added pre-last-layer lifecycle features:
  - `pre_last_entry_price`
  - `minutes_since_pre_last_entry`
  - `adverse_from_pre_last_entry_points`
- Main rule form tested per strategy/layer:
  - `adverse_from_pre_last_entry_points >= adverse_q25`
- This uses the basket state before the add-on opens in that minute, avoiding leakage from the new layer.

Key thresholds by strategy, focusing on early layers:

| Strategy | Prior layer 1 q25 / median adverse | Prior layer 2 q25 / median adverse | Typical minutes median |
|---|---:|---:|---:|
| `T1/S01` | 1.46 / 1.74 | 1.68 / 1.83 | 30-44m |
| `T2/S03` | 1.62 / 1.79 | 1.70 / 1.95 | 22-23m |
| `T2/S04` | 1.55 / 1.75 | 1.65 / 1.76 | 18-33m |
| `T3/S06` | 3.00 / 3.18 | 3.02 / 3.11 | 111-144m |
| `T4/S08` | 1.64 / 1.85 | 1.69 / 1.90 | 13-16m |
| `T5/S09` | 5.03 / 5.58 | 5.40 / 5.65 | 104-118m |
| `T5/S10` | 3.19 / 3.38 | 2.83 / 3.43 | 130-310m |
| `T6/S12` | 1.95 / 2.13 | 2.02 / 2.18 | 44-55m |

Interpretation:

- Add-on trigger behavior is strongly consistent with strategy-specific adverse-distance thresholds from the previous layer.
- The first two prior-layer thresholds are very stable inside each family:
  - T1/T2/T4: ~1.5-1.7 points q25, ~1.75-1.95 median.
  - T3/T5/S10: ~3.0 points q25/median.
  - T5/S09: ~5.0-5.6 points.
  - T6/S12: ~2.0-2.2 points.
- Precision varies because threshold-only rules still match many candidate minutes, especially early layers with long basket exposure, but lift is strong for most strategy/layer cells.
- Next step should add a time gate and/or layer-specific cooldown to improve precision, then test a simple add-on simulator using these thresholds.

## Phase 5 Add-on Cooldown / Time-Gate Mining

Generated:

- `scripts/phase5_add_on_cooldown_mining.py`
- `outputs/add_on_cooldown_rules.csv`
- `outputs/add_on_cooldown_rules.md`

Method:

- Extends add-on trigger mining from a one-feature rule to a two-feature rule:
  - `adverse_from_pre_last_entry_points >= adverse_threshold`
  - `minutes_since_pre_last_entry >= min_minutes`
- Candidate rules were mined per `strategy + pre_open_layer_count`.
- Candidate selection sorted by F1, then precision, then recall.
- Baseline comparison is the distance-only rule using the positive q25 adverse threshold and no time gate.

Results:

- 37 strategy/layer cells met the minimum positive sample requirement.
- 20 of 37 selected rules had `min_minutes = 0`, meaning no meaningful cooldown was needed by the F1 criterion.
- 17 of 37 selected rules preferred a positive time gate.
- F1 improvement from adding the time gate was modest overall:
  - mean improvement: ~0.045
  - median improvement: ~0.021
  - 75th percentile improvement: ~0.056
  - maximum improvement: ~0.291

Important examples:

| Strategy | Prior layers | Adverse threshold | Min minutes | F1 | Baseline F1 |
|---|---:|---:|---:|---:|---:|
| `T2/S03` | 3 | 1.64 | 5.0 | 0.436 | 0.376 |
| `T2/S03` | 4 | 1.57 | 5.2 | 0.364 | 0.165 |
| `T2/S04` | 3 | 1.91 | 3.8 | 0.583 | 0.518 |
| `T2/S04` | 5 | 1.77 | 5.0 | 0.556 | 0.389 |
| `T3/S06` | 1 | 3.18 | 4.8 | 0.606 | 0.577 |
| `T4/S08` | 1 | 1.64 | 3.0 | 0.540 | 0.507 |
| `T4/S08` | 2 | 1.69 | 7.0 | 0.585 | 0.533 |
| `T6/S12` | 3 | 1.95 | 15.0 | 0.535 | 0.514 |

Interpretation:

- The core add-on trigger remains adverse distance from the previous layer.
- A small positive cooldown/time gate improves some mid-layer cells, especially T2/S03 layers 3-4, T2/S04 layers 3-6, and T4/S08 early layers.
- The cooldown effect is secondary: many best rules choose `min_minutes = 0`, and overall F1 improvement is modest.
- Operational approximation for add-ons should prioritize strategy-specific grid distance first, then optionally add a small cooldown of ~3-8 minutes for selected families/layers.
- Longer median observed delays in raw positives likely reflect price not reaching grid distance for a long time, not an explicit minimum wait requirement.

## Phase 5 Exit VWAP TP Threshold Mining

Generated:

- `src/qq_research/exit_trigger_mining.py`
- `scripts/phase5_exit_trigger_mining.py`
- `tests/test_exit_trigger_mining.py`
- `outputs/exit_trigger_thresholds.csv`
- `outputs/exit_trigger_thresholds.md`

Method:

- Uses active basket-minute rows from `basket_minute_lifecycle.parquet`.
- Positive labels are final exit minutes.
- Main rule tested per `strategy + open_layer_count`:
  - `close_move_from_open_vwap_points >= TP(strategy, open_layer_count)`
- `close_move_from_open_vwap_points` is direction-aware and measures current M1 close relative to the active basket VWAP.
- Candidate TP thresholds are positive q10/q25/median/q75 exit moves per strategy/layer count.

Representative early-layer exit move quantiles:

| Strategy | Open layers | Positives | Move q25 | Move median | Best TP |
|---|---:|---:|---:|---:|---:|
| `T1/S01` | 1 | 211 | 0.56 | 0.76 | 0.56 |
| `T1/S01` | 2 | 101 | 0.51 | 0.75 | 0.34 |
| `T1/S01` | 3 | 40 | 0.51 | 0.73 | 0.51 |
| `T2/S03` | 1 | 153 | 0.49 | 0.68 | 0.49 |
| `T2/S03` | 2 | 55 | 0.51 | 0.73 | 0.51 |
| `T2/S03` | 3 | 34 | 0.53 | 0.72 | 0.53 |
| `T2/S04` | 1 | 182 | 0.43 | 0.65 | 0.43 |
| `T2/S04` | 2 | 48 | 0.49 | 0.76 | 0.35 |
| `T2/S04` | 3 | 41 | 0.47 | 0.60 | 0.32 |
| `T3/S06` | 1 | 62 | 0.68 | 0.84 | 0.84 |
| `T3/S06` | 2 | 14 | 0.82 | 1.19 | 0.82 |
| `T4/S08` | 1 | 21 | 1.37 | 1.78 | 1.78 |
| `T5/S09` | 1 | 38 | 2.13 | 2.46 | 1.86 |
| `T5/S10` | 1 | 62 | 0.56 | 1.28 | 2.98 |
| `T6/S12` | 1 | 61 | 1.17 | 1.39 | 1.17 |
| `T6/S12` | 2 | 29 | 1.10 | 1.48 | 1.10 |

Interpretation:

- Exit positive quantiles strongly support a basket-VWAP TP mechanism.
- T1/T2 early-layer exits cluster around ~0.45-0.55 q25 and ~0.60-0.76 median points.
- T3 exits are higher, around ~0.68-0.82 q25 and ~0.84-1.19 median points.
- T4/T5/S09/T6 use larger TP regimes consistent with the earlier basket-level exit event summary.
- Naive per-minute threshold precision is low in many early-layer cells because once TP is reached, all subsequent active minutes before the actual close are counted as false positives. This suggests the next step should test first-cross or first-eligible TP logic rather than treating every TP-satisfied minute as an independent exit signal.
- T5/S10 remains unusual: positive exit move distribution is broad and best F1 chooses high TP with low recall, indicating either mixed exit modes, different basket handling, or more path-dependent logic.

## Phase 5 Exit First-Cross / First-Touch Analysis

Generated:

- `src/qq_research/exit_first_cross.py`
- `scripts/phase5_exit_first_cross.py`
- `tests/test_exit_first_cross.py`
- `outputs/exit_first_cross_events.csv`
- `outputs/exit_first_cross_summary.csv`
- `outputs/exit_first_cross_report.md`

Lifecycle update:

- `basket_minute_lifecycle.parquet` now includes M1 high/low and direction-aware intrabar favorable movement:
  - `m1_high`
  - `m1_low`
  - `high_move_from_open_vwap_points`
  - `low_move_from_open_vwap_points`
  - `touch_move_from_open_vwap_points`
- For long baskets, `touch_move_from_open_vwap_points = high - basket_vwap`.
- For short baskets, `touch_move_from_open_vwap_points = basket_vwap - low`.

Method:

- Compares first M1 TP eligibility to the actual QQ final exit minute.
- Tested four variants:
  - `close_q25`: M1 close crosses positive exit q25 TP.
  - `close_median`: M1 close crosses positive exit median TP.
  - `touch_q25`: intrabar favorable high/low touches positive exit q25 TP.
  - `touch_median`: intrabar favorable high/low touches positive exit median TP.
- Thresholds are per `strategy + open_layer_count` from `outputs/exit_trigger_thresholds.csv`.

Overall results:

| Variant | Cross found % | Weighted within 1m % | Median of layer medians |
|---|---:|---:|---:|
| `close_q25` | 83.3 | 62.5 | 1.0m |
| `close_median` | 55.4 | 69.6 | 1.0m |
| `touch_q25` | 86.9 | 38.8 | 4.0m |
| `touch_median` | 70.8 | 60.9 | 1.0m |

`close_q25` strategy-level results, among baskets where a cross was found:

| Strategy | Cross-found baskets | Within 1m % | Median lag | q75 lag | q90 lag |
|---|---:|---:|---:|---:|---:|
| `T1/S01` | 404 | 75.99 | 1.0 | 1.0 | 125.5 |
| `T2/S03` | 284 | 69.37 | 1.0 | 3.0 | 35.4 |
| `T2/S04` | 344 | 74.71 | 1.0 | 2.0 | 4.7 |
| `T3/S06` | 70 | 75.71 | 1.0 | 1.0 | 11.3 |
| `T4/S08` | 31 | 61.29 | 1.0 | 3.0 | 14.0 |
| `T5/S09` | 41 | 82.93 | 1.0 | 1.0 | 2.0 |
| `T5/S10` | 70 | 10.00 | 68.5 | 316.25 | 774.2 |
| `T6/S12` | 137 | 78.83 | 1.0 | 1.0 | 4.4 |

Interpretation:

- `close_q25` is the best first approximation for QQ's exit timing. It finds a TP cross in 83.3% of baskets and many core families exit within 1 minute of first close-cross.
- `touch_q25` finds slightly more crosses but with much worse timing; intrabar touch often occurs too early. This argues against a simple tick/intrabar touch TP model, at least with M1 high/low approximation.
- `close_median` is more conservative: when it crosses, timing is often close, but it misses many actual exits.
- Core families (`T1/S01`, `T2/S03`, `T2/S04`, `T3/S06`, `T5/S09`, `T6/S12`) are broadly consistent with M1 close-based VWAP TP exits.
- `T5/S10` remains an outlier: first close-cross occurs far before actual exits, supporting the earlier hypothesis that it uses mixed/path-dependent exit logic or a different TP regime.
- Large q90 lags for some T1/T2 cells show that a subset of baskets touch TP early but are not closed quickly; these may involve spread filters, session filters, minimum profit-money thresholds, partial close behavior, or later-layer special handling.

## Phase 5 T5/S10 Exit Path Diagnostics

Generated:

- `src/qq_research/s10_exit_diagnostics.py`
- `scripts/phase5_s10_exit_diagnostics.py`
- `tests/test_s10_exit_diagnostics.py`
- `outputs/s10_exit_path_diagnostics.csv`
- `outputs/s10_exit_path_summary.csv`
- `outputs/s10_exit_path_diagnostics.md`

Context:

- User confirmed QQ checks live exits approximately once per minute and closes on minute boundaries. This supports the earlier `close_q25` result over intrabar `touch_q25`.
- `T5/S10` was the major outlier under the common close-cross TP analysis: first close-cross often occurred far before actual exit.

Key S10 path results:

- S10 has 108 baskets in the current lifecycle panel.
- Overall exit move distribution:
  - q25: `0.80`
  - median: `2.00`
  - q75: `3.40`
  - q90: `4.41`
- Overall max close move distribution:
  - q25: `1.10`
  - median: `2.13`
  - q75: `3.63`
  - q90: `5.04`
- Actual S10 exits are usually close to the path maximum:
  - median retrace from max close move to exit: `0.11`
  - q75 retrace: `0.40`
  - median minutes from max close move to actual exit: `1.0`
  - `82.4%` of baskets exit within 1 minute of max close move.
  - `68.5%` have retrace <= `0.25` points at exit.
  - `63.9%` satisfy both max-to-exit <= 1 minute and retrace <= 0.25.

Layer-specific S10 medians:

| Exit layers | Baskets | Exit median | Exit q25 | Exit q75 | Max median | Retrace median | Holding median | Max-to-exit median | Max-to-exit <=1m % |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 62 | 1.28 | 0.55 | 2.98 | 1.58 | 0.10 | 190.5 | 1.0 | 77.4 |
| 2 | 13 | 2.25 | 0.22 | 3.71 | 2.25 | 0.09 | 276.0 | 1.0 | 84.6 |
| 3 | 6 | 2.70 | 2.11 | 3.11 | 3.10 | 0.08 | 953.0 | 1.0 | 83.3 |
| 4 | 7 | 3.33 | 2.48 | 3.50 | 3.52 | 0.20 | 637.0 | 1.0 | 100.0 |
| 6 | 5 | 2.04 | 2.02 | 2.24 | 2.15 | 0.01 | 371.0 | 1.0 | 100.0 |
| 8 | 6 | 1.33 | 0.08 | 1.61 | 1.58 | 0.14 | 10.0 | 0.5 | 83.3 |

Time/session features:

- Entry hour is highly concentrated: 94/108 S10 baskets start at broker hour `22`.
- Exit hour is bimodal-ish:
  - 42 baskets exit in broker hours `21-23`, with median holding `17.5` minutes and median exit move `1.085`.
  - 39 baskets exit in broker hours `01-04`, with median holding `295` minutes and median exit move `1.74`.
  - Later exits (`05-20`) generally have higher exit medians around `2.9-4.3` and longer holding times.

Interpretation:

- S10 does not look like a simple trailing exit where QQ hits TP early and waits through a large retrace. Actual exits occur close to the path maximum in most baskets.
- S10's poor `close_q25` first-cross timing is mostly because the q25 threshold is too low for many S10 modes, not because the EA ignores a reached high-water mark for long periods.
- A single fixed TP is unlikely for S10. It likely has time/session-conditioned or mode-conditioned TP behavior:
  - quick 22:00-session exits with lower targets,
  - overnight / late-session exits with higher effective targets,
  - some loss or low-profit timeout exits.
- S10 should be modeled separately from the common T1/T2/T3/T4/T5-S09/T6 close_q25 basket VWAP TP rule.
