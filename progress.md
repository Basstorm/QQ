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
