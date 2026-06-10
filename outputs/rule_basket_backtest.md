# Non-S10 Rule Entry Basket Backtest

## Scope

- Uses inferred M15 entry rules to seed baskets.
- Excludes `T5/S10`.
- Uses normalized one-unit initial sizing; reported PnL is direction-aware points, not account currency.
- Basket management uses inferred add-on thresholds and close-based VWAP TP on M1 close.

| Variant | Strategy | Trades | Unclosed | Closed % | Win % | Total points | Avg points | Median points | Worst trade | Max DD | Avg layers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `all_background` | `T1/S01` | 1270 | 0 | 100.0 | 100.0 | 1789.06 | 1.409 | 0.810 | 0.56 | 0.00 | 1.37 |
| `all_background` | `T2/S03` | 484 | 0 | 100.0 | 100.0 | 542.08 | 1.120 | 0.800 | 0.49 | 0.00 | 1.25 |
| `all_background` | `T2/S04` | 348 | 0 | 100.0 | 100.0 | 379.54 | 1.091 | 0.815 | 0.43 | 0.00 | 1.24 |
| `all_background` | `T3/S06` | 452 | 1 | 99.8 | 99.8 | -73.10 | -0.162 | 1.160 | -771.33 | -771.33 | 1.19 |
| `all_background` | `T4/S08` | 14 | 0 | 100.0 | 100.0 | 56.84 | 4.060 | 2.860 | 1.82 | 0.00 | 2.00 |
| `all_background` | `T5/S09` | 96 | 0 | 100.0 | 100.0 | 333.58 | 3.475 | 2.165 | 1.87 | 0.00 | 1.46 |
| `all_background` | `T6/S12` | 381 | 1 | 99.7 | 99.7 | -206.59 | -0.542 | 1.590 | -1034.92 | -1034.92 | 1.35 |
| `matched_context` | `T1/S01` | 1946 | 0 | 100.0 | 100.0 | 2507.35 | 1.288 | 0.790 | 0.56 | 0.00 | 1.20 |
| `matched_context` | `T2/S03` | 441 | 0 | 100.0 | 100.0 | 516.64 | 1.172 | 0.860 | 0.49 | 0.00 | 1.37 |
| `matched_context` | `T2/S04` | 263 | 0 | 100.0 | 100.0 | 320.14 | 1.217 | 0.850 | 0.43 | 0.00 | 1.19 |
| `matched_context` | `T3/S06` | 518 | 0 | 100.0 | 100.0 | 848.34 | 1.638 | 1.175 | 0.84 | 0.00 | 1.16 |
| `matched_context` | `T4/S08` | 14 | 0 | 100.0 | 100.0 | 53.65 | 3.832 | 2.255 | 1.82 | 0.00 | 1.93 |
| `matched_context` | `T5/S09` | 140 | 0 | 100.0 | 100.0 | 434.99 | 3.107 | 2.235 | 1.87 | 0.00 | 1.24 |
| `matched_context` | `T6/S12` | 419 | 1 | 99.8 | 99.8 | -125.91 | -0.301 | 1.580 | -1034.92 | -1034.92 | 1.38 |
