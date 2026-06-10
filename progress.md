# Quantum Queen EA Analysis Progress

## 2026-06-10 Session Log

### Completed

- Used Playwright to inspect the MQL5 product page for Quantum Queen MT5.
- Captured product context, version details, and version-history clues.
- Confirmed the three project data files exist:
  - `QuantumQueen_backtest_report.xlsx`
  - `xauusd_m1_2016_2026.csv`
  - `xauusd_m15_2016_2025.csv`
- Confirmed CSV headers and UTC timestamp format using standard Python CSV reading.
- Discussed an A+B-first analysis scope with the user:
  - A: descriptive strategy behavior analysis.
  - B: approximate rule inference.
  - C: possible later replication, not first pass.
- User clarified key mechanics:
  - EA entry logic operates on M15.
  - Close/add-on logic is checked every minute.
  - Recent entry frequency is low.
- Created persistent planning files:
  - `task_plan.md`
  - `findings.md`
  - `progress.md`

### In Progress

- Python analysis environment setup under `.venv` was started with `uv`.
- Dependency installation needs proxy variables:

```bash
export HTTP_PROXY=http://127.0.0.1:7897
export HTTPS_PROXY=http://127.0.0.1:7897
export http_proxy=http://127.0.0.1:7897
export https_proxy=http://127.0.0.1:7897
```

### Next Steps

1. Finish/verify the Python analysis environment.
2. Read `QuantumQueen_backtest_report.xlsx` to identify sheets and fields.
3. Produce Phase 0 data audit.
4. Confirm whether explicit strategy identifiers exist in the report.
5. Begin trade reconstruction and timestamp alignment.

### Notes

- The user explicitly asked to discuss and persist the plan first, not to rush into dependency troubleshooting or implementation.


### Devin Hook Persistence Setup

- Read Devin CLI hook documentation via the `devin-for-terminal` skill.
- Confirmed project hooks should be placed under `.devin/`.
- Created `.devin/hooks.v1.json` using the Claude-compatible hook format.
- Created `.devin/scripts/context_hooks.py` to snapshot planning context.
- Configured snapshots for `SessionStart`, `UserPromptSubmit`, `Stop`, `SessionEnd`, and `PostCompaction`.
- Verified JSON syntax with `python3 -m json.tool`.
- Manually tested normal snapshot behavior with a `ManualTest` hook payload.
- Manually tested `PostCompaction` behavior and confirmed `.planning/context/restore_after_compaction.md` is written.

Note: current Devin docs do not list a `PreCompaction` hook. Pre-compaction safety is handled by frequent snapshots before compaction-triggering moments rather than a dedicated pre-compaction event.


### Dependency and Data Readiness Check

- Converted the directory into a uv-managed project with `pyproject.toml` and `uv.lock`.
- Installed core analysis dependencies through `uv add` using the local proxy.
- Verified imports for pandas, openpyxl, numpy, scipy, scikit-learn, polars, pyarrow, matplotlib, seaborn, plotly, and statsmodels.
- Verified `QuantumQueen_backtest_report.xlsx` opens successfully.
- Verified both CSV files can be read with pandas.
- Initial Excel inspection shows one sheet, `Sheet1`, with MT5 report metadata:
  - Server/build: `EBCFinancialGroupKY-Live01 (Build 5836)`
  - Expert: `Quantum Queen 3.52(2)`
  - Symbol: `XAUUSD`

Ready to begin Phase 0 data audit.


### Phase 0 Data Audit Completed

- Created `scripts/phase0_data_audit.py`.
- Generated `outputs/data_audit_report.md`.
- Generated `outputs/raw_schema_summary.json`.
- Confirmed explicit entry strategy labels are available from comments (`T*/S*`).
- Confirmed only 8 strategy IDs are active in this report.
- Confirmed report-to-CSV price/time alignment uses offset `0h` after flooring deal timestamps to minute.
- Noted that GMT+3 may still be the semantic broker timezone for session labeling, but should not be applied when joining to the provided CSV files.

Error encountered:

- Initial script used `np.where` to create strategy labels and failed because pandas evaluated the NaN branch for exit rows. Fixed by assigning strategy only on rows where both `T` and `S` are present.


### Phase 1 Trade Reconstruction Completed

- Added TDD tests for strategy comment parsing, FIFO reconstruction, basket grouping, and Phase 1 seconds diagnostics.
- Implemented `src/qq_research/reconstruction.py`.
- Implemented `scripts/phase1_reconstruct_trades.py`.
- Generated normalized trade, position, and basket parquet files.
- Generated `outputs/time_alignment_report.md`.
- Verified tests pass with `python -m unittest discover`.
- Verified parquet output shapes:
  - `trades_normalized.parquet`: 11,310 rows x 31 columns
  - `positions.parquet`: 6,100 rows x 27 columns
  - `baskets.parquet`: 1,657 rows x 14 columns
- Verified reconstructed PnL equals report exit-profit total exactly.

Ready to begin Phase 2 feature engineering.


### Pre-Compaction Checkpoint Before Phase 2

Current state before user-triggered context compaction:

- Phase 0 is complete.
- Phase 1 is complete.
- Phase 2 is ready to start.
- Local git is tracking the lightweight project state.
- Raw data, `.venv`, parquet outputs, and runtime context snapshots remain local-only via `.gitignore`.

Latest commits:

- `9d93a6b Add Phase 1 trade reconstruction.`
- `9781a18 Add Phase 0 data audit.`
- `231cd70 Add uv-managed analysis environment.`
- `c9d58f0 Initialize local analysis tracking.`

Files to read after compaction, in order:

1. `task_plan.md` — confirms Phase 2 is ready to start.
2. `findings.md` — durable project findings from MQL5, Phase 0, Phase 1.
3. `progress.md` — chronological work log and checkpoint.
4. `outputs/data_audit_report.md` — Phase 0 summary.
5. `outputs/time_alignment_report.md` — Phase 1 summary.
6. `src/qq_research/reconstruction.py` — reusable parsing/reconstruction functions.
7. `scripts/phase1_reconstruct_trades.py` — how Phase 1 parquet files are generated.

Phase 2 starting point:

- Use `outputs/trades_normalized.parquet`, `outputs/positions.parquet`, and `outputs/baskets.parquet` as local source tables.
- Build feature engineering on top of reconstructed positions/baskets, preserving `strategy`, `T`, `S`, `broker_time`, and `utc_time_est`.
- Join candles using broker/report time with offset `0h`; do not shift when joining to the provided CSVs.
- For session analysis only, derive `utc_time_est = broker_time - 3h` because user recalls report/export time is GMT+3.
- Be careful evaluating the M15-entry claim: raw entry deals include add-ons; Phase 2 needs a better initial-entry/add-on distinction.

Immediate Phase 2 tasks:

1. Add tests for candle feature helpers and position/basket feature construction.
2. Create feature module/script to compute:
   - M15 entry context features.
   - M1 post-entry management path features.
   - Time/session features in both broker time and estimated UTC.
   - Basket/order-structure features.
3. Generate `outputs/deal_features.parquet`, `outputs/basket_features.parquet`, and `outputs/feature_dictionary.md`.
4. Produce a short Phase 2 report before moving to clustering/rule inference.

### Phase 2 Session Started

- Restored context from `task_plan.md`, `findings.md`, and `progress.md`.
- Confirmed Phase 2 source parquet schemas:
  - `trades_normalized.parquet`: 11,310 rows x 31 columns.
  - `positions.parquet`: 6,100 rows x 27 columns.
  - `baskets.parquet`: 1,657 rows x 14 columns.
- mem0 search found no additional project-specific QuantumQueenResearch memories beyond local planning files.
- Phase 2 implementation design: add reusable feature helpers in `src/qq_research/features.py`, a generation script in `scripts/phase2_feature_engineering.py`, and TDD tests in `tests/test_features.py`.

### Phase 2 Feature Engineering Completed

- Added `pandas-ta-classic` dependency because `pandas-ta` / `pandas_ta` were not available for this project's Python 3.10-compatible dependency resolution; `pandas-ta-classic` imports as `pandas_ta_classic` and provides RSI/ADX/MACD/ATR/EMA functions.
- Added TDD tests for:
  - broker/estimated-UTC session feature generation,
  - M15 containing-bar context and lookback features,
  - pandas-ta-classic M15 indicator columns,
  - long/short M1 MAE/MFE path features,
  - basket structure and add-on spacing features,
  - Phase 2 feature dictionary/report text.
- Implemented `src/qq_research/features.py`.
- Implemented `scripts/phase2_feature_engineering.py`.
- Generated Phase 2 outputs:
  - `outputs/deal_features.parquet` (6,100 x 160),
  - `outputs/basket_features.parquet` (1,657 x 154),
  - `outputs/feature_dictionary.md`,
  - `outputs/phase2_feature_report.md`.
- Verification after generation:
  - `python -m unittest discover -s tests -v` passes 11 tests.
  - Required key columns are present in both feature tables.
  - M1 path availability is 100%.
  - Feature-table PnL totals match Phase 1 source tables within floating-point tolerance.
- Code review found and fixed a path-feature helper inconsistency with custom `entry_time_col`.
- Code simplification removed an unnecessary merge before basket feature construction.

### Phase 3 Strategy Candidate Discovery Completed

- Created Phase 2 checkpoint commit `9d922b4 Add Phase 2 feature engineering checkpoint.`
- Started Phase 3 from `outputs/basket_features.parquet` and `outputs/deal_features.parquet`.
- Added TDD tests for clustering feature selection, matrix scaling, best-k selection, cluster/strategy overlap, and report generation.
- Implemented `src/qq_research/strategy_discovery.py` and `scripts/phase3_strategy_discovery.py`.
- Generated Phase 3 outputs:
  - `outputs/strategy_cluster_assignments.parquet`,
  - `outputs/strategy_clusters_report.md`,
  - `outputs/cluster_diagnostics/kmeans_diagnostics.csv`,
  - `outputs/cluster_diagnostics/best_cluster_strategy_overlap.csv`,
  - `outputs/cluster_diagnostics/best_cluster_feature_summary.csv`,
  - `outputs/cluster_diagnostics/clustering_feature_columns.csv`.
- Debugged sklearn RuntimeWarnings:
  - Initial root cause involved large zero-IQR columns not scaling under RobustScaler.
  - After switching to clipped StandardScaler, remaining warning was isolated to Euclidean `silhouette_score` pairwise distance computation, not KMeans or matrix validity.
  - Switched silhouette diagnostics to Manhattan distance; script output is clean.
- Excluded absolute price level features after observing early clusters were influenced by historical price regime.
- Current Phase 3 result: natural KMeans k=3, forced k=12 generated, 8 active explicit strategies confirmed.

### Phase 4 Initial Compact-Feature Rule Inference Completed

- Created Phase 3 checkpoint commit `2e8f99c Add Phase 3 strategy discovery checkpoint.`
- User clarified that expanded indicator discovery should not be limited to named examples; broad `pandas-ta`/compatible public indicators should be considered if compact features are insufficient.
- Implemented TDD tests for:
  - strategy-vs-rest feature contrast ranking,
  - simple candidate family classification,
  - strategy profile report uncertainty and expanded-indicator fallback text.
- Implemented `src/qq_research/rule_inference.py` and `scripts/phase4_rule_inference.py`.
- Generated `outputs/strategy_profiles.md`.
- Current Phase 4 is an initial compact-feature pass; several strategies remain low confidence and should trigger expanded indicator/parameter discovery if more precise rules are required.

### Phase 4 Expanded Indicator / Parameter Discovery First Pass Completed

- Created Phase 4 compact checkpoint commit `b4eb7fc Add Phase 4 compact rule inference checkpoint.`
- Implemented expanded indicator discovery with TDD coverage for:
  - MA stacking/cross/spread feature generation,
  - strategy entry labels on M15 bars,
  - per-strategy AUC-lift scoring.
- Generated expanded outputs:
  - `outputs/expanded_indicator_discovery_report.md`,
  - `outputs/expanded_indicator_scores.csv`,
  - `outputs/expanded_indicator_feature_matrix.parquet`.
- Code review identified and fixed absolute MA level leakage; raw MA levels are now excluded from expanded features.
- First-pass matrix contains 143,097 M15 rows and 137 generated feature columns after excluding raw MA levels.
- Top candidates include Fisher, WMA spread, ROC, RSI, and ADX/DMI features depending on strategy.

### Phase 4 Candidate Multi-Condition Rule Mining Completed

- Implemented rule mining with TDD coverage for condition generation, AND-rule evaluation, precision/recall/base-rate lift, and report generation.
- Generated `outputs/candidate_rule_combinations.csv` and `outputs/candidate_rule_combinations.md`.
- Added precision lift vs base-rate after observing raw precision can look misleadingly low because initial-entry bars are extremely sparse.
- Candidate rules now provide interpretable 1-3 condition hypotheses per active `Sxx`.

### Phase 4 Temporal and Matched-Negative Validation First Pass Completed

- Created checkpoint commit `646f2d3 Add Phase 4 expanded indicator discovery checkpoint.`
- Implemented temporal validation without writing a formal spec per user instruction.
- Added TDD tests for temporal splitting, rule parsing, matched context masking, period evaluation, and train-rule/test evaluation.
- Generated `outputs/temporal_rule_validation.csv`, `outputs/temporal_train_feature_scores.csv`, and `outputs/temporal_rule_validation.md`.
- Default split is `2021-01-01`, selected after checking yearly positive-count balance.
- Validation shows `T2/S03` and `T2/S04` have the strongest temporally stable MA/momentum rule signals; sparse strategies still require caution.

### Phase 4 Final Approximate Strategy Synthesis Completed

- Created checkpoint commit `d7d62dc Add Phase 4 temporal rule validation checkpoint.`
- Implemented final synthesis with TDD coverage for temporal rule selection, confidence classification, row synthesis, and Markdown report generation.
- Generated `outputs/strategy_rule_synthesis.csv` and `outputs/strategy_rule_synthesis.md`.
- Final synthesis ranks `T2/S03`, `T2/S04`, and `T5/S10` as robust initial-entry rule families; `T1/S01` and `T3/S06` as moderate; `T5/S09` and `T6/S12` as tentative; `T4/S08` as sparse hint.

### Phase 4 Robust Rule Vectorbt Smoke Backtest Completed

- Added `vectorbt` dependency using `uv add vectorbt`.
- Implemented robust-rule vectorbt smoke backtest with TDD coverage for rule-mask evaluation, edge-signal generation, and robust-variant selection.
- Generated `outputs/robust_vectorbt_backtest.csv` and `outputs/robust_vectorbt_backtest.md`.
- Result: standalone long-only rule-on/rule-off backtests are weak; only `T2/S03` is modestly positive, supporting the conclusion that robust entry contexts are not sufficient without Quantum Queen's basket/exit management.

### Phase 5 Basket Lifecycle Diagnostics First Pass Completed

- Started Phase 5 after observing robust entry filters alone are weak standalone strategies and QQ's high win rate likely comes from basket management.
- Implemented lifecycle management feature generation with TDD coverage for add-on spacing, exit VWAP TP features, and M1 basket lifecycle rows.
- Generated add-on events, exit events, and active basket-minute lifecycle parquet outputs plus `outputs/lifecycle_management_report.md`.
- Key finding: delayed/grid add-on spacing is strategy-specific and tight for T1/T2 (~1.6 points), wider for T3/T5/T6; exit moves from entry VWAP are small and strategy-specific.
- The lifecycle panel includes `pre_open_*` features for true per-minute add-on trigger inference.

### Phase 5 Add-on Trigger Threshold First Pass Completed

- Added pre-last-layer fields to the M1 lifecycle panel for leakage-safe add-on trigger inference.
- Implemented add-on trigger threshold mining with TDD coverage for trigger frame filtering, threshold evaluation, and strategy/layer threshold extraction.
- Generated `outputs/add_on_trigger_thresholds.csv` and `outputs/add_on_trigger_thresholds.md`.
- Key result: delayed add-ons are well explained by adverse move from previous layer, with strategy-specific thresholds around 1.6, 2.1, 3.1, or 5.4 XAUUSD points depending on strategy family.

### Phase 5 Add-on Cooldown Analysis Completed

- Implemented distance-plus-time add-on rule mining with tests for two-feature rule evaluation and per-strategy/layer candidate selection.
- Generated `outputs/add_on_cooldown_rules.csv` and `outputs/add_on_cooldown_rules.md`.
- Result: cooldown/time gates are secondary. 20/37 selected strategy-layer rules need no time gate; positive gates help selected mid-layer cells, usually in the ~3-8 minute range, while adverse distance from the previous layer remains the primary trigger.

### Phase 5 Exit VWAP TP Threshold First Pass Completed

- Implemented exit trigger threshold mining with TDD coverage for active basket-minute filtering, threshold evaluation, and strategy/layer TP extraction.
- Generated `outputs/exit_trigger_thresholds.csv` and `outputs/exit_trigger_thresholds.md`.
- Result: positive exit minutes strongly support basket VWAP TP thresholds. T1/T2 early layers are around 0.45-0.76 points, T3 around 0.8-1.2, and T4/T5/T6 higher. Naive per-minute precision is low because TP-satisfied minutes before actual close become false positives, so the next step should evaluate first-cross TP logic.

### Phase 5 Exit First-Cross Analysis Completed

- Added M1 high/low and direction-aware touch-move features to the basket lifecycle panel.
- Implemented first-cross/first-touch exit analysis with tests.
- Generated `outputs/exit_first_cross_events.csv`, `outputs/exit_first_cross_summary.csv`, and `outputs/exit_first_cross_report.md`.
- Result: `close_q25` is the best first approximation. It finds TP crosses in 83.3% of baskets and core strategy families usually exit within ~1 minute after first M1 close-cross. Intrabar touch fires too early, and T5/S10 remains a major outlier.

### Phase 5 T5/S10 Exit Path Diagnostics Completed

- Implemented S10-specific path diagnostics and generated `outputs/s10_exit_path_diagnostics.md/.csv` and `outputs/s10_exit_path_summary.csv`.
- User confirmed QQ live exits are checked about once per minute and close on minute boundaries, supporting close-based rather than intrabar-touch exit inference.
- Result: S10 actual exits are usually near the basket's max close move, with median max-to-exit lag 1 minute and median retrace only 0.11 points. S10 is therefore not mainly a trailing/retrace exit. It appears mode/time/session-conditioned: 94/108 starts are at broker hour 22, quick 21-23 exits have lower median target, while later/overnight exits require higher effective targets.

### Phase 5 T5/S10 Mode-Conditioned TP First Pass Completed

- Implemented S10 current-session/current-holding mode TP mining with first-cross validation.
- Generated `outputs/s10_mode_tp_thresholds.csv`, `outputs/s10_mode_tp_first_cross_events.csv`, `outputs/s10_mode_tp_first_cross_summary.csv`, and `outputs/s10_mode_tp_report.md`.
- Result: current mode TP alone is not sufficient. Low/mid quantile thresholds still trigger too early; high quantiles are timely but low coverage. Oracle final-mode improves lag materially, indicating S10 likely has an entry-time hidden target mode rather than a pure current-clock rule.
