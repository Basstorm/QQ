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
