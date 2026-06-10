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
