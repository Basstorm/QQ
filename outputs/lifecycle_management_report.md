# Phase 5 Basket Lifecycle Management Diagnostics

## Scope

- This phase studies Quantum Queen's observed basket management, not the initial-entry filter.
- Add-on events measure spacing from previous and initial entries in direction-aware adverse points.
- Exit events measure final basket close price relative to volume-weighted entry price.
- The M1 lifecycle panel has one row per active basket-minute and is intended for later per-minute add-on/exit classifier mining.
- `pre_open_*` lifecycle fields describe the basket state before any add-on opened in that minute, which is the correct state for add-on trigger inference.

## Dataset Sizes

- Add-on events: `4,443`
- Delayed/grid add-on events: `1,215`
- Exit events / baskets: `1,657`
- Active basket-minute rows: `240,987`

## Strategy-Level Counts

| Strategy | Baskets | Same-minute add-ons | Delayed add-ons | Active M1 rows | Basket win rate % | Median basket PnL |
|---|---:|---:|---:|---:|---:|---:|
| `T1/S01` | 459 | 942 | 368 | 58556 | 98.47 | 1096.16 |
| `T2/S03` | 318 | 663 | 212 | 40247 | 97.80 | 991.42 |
| `T2/S04` | 378 | 623 | 230 | 31613 | 99.47 | 877.52 |
| `T3/S06` | 99 | 243 | 60 | 21147 | 98.99 | 854.70 |
| `T4/S08` | 58 | 98 | 75 | 6400 | 100.00 | 2718.45 |
| `T5/S09` | 71 | 119 | 44 | 24513 | 100.00 | 2265.12 |
| `T5/S10` | 108 | 223 | 55 | 30508 | 88.89 | 499.48 |
| `T6/S12` | 166 | 317 | 171 | 28003 | 100.00 | 1382.38 |

## Delayed/Grid Add-on Adverse Spacing From Previous Entry

| Strategy | q10 | q25 | median | q75 | q90 |
|---|---:|---:|---:|---:|---:|
| `T1/S01` | 1.51 | 1.55 | 1.64 | 1.83 | 2.17 |
| `T2/S03` | 1.51 | 1.55 | 1.62 | 1.73 | 1.98 |
| `T2/S04` | 1.53 | 1.58 | 1.68 | 1.88 | 2.26 |
| `T3/S06` | 3.03 | 3.08 | 3.20 | 3.66 | 4.87 |
| `T4/S08` | 1.55 | 1.60 | 1.80 | 2.30 | 3.19 |
| `T5/S09` | 5.10 | 5.18 | 5.41 | 5.83 | 6.39 |
| `T5/S10` | 3.03 | 3.07 | 3.14 | 3.51 | 3.76 |
| `T6/S12` | 2.04 | 2.09 | 2.24 | 2.46 | 2.72 |

## Delayed/Grid Add-on Minutes Since Previous Entry

| Strategy | q10 | q25 | median | q75 | q90 |
|---|---:|---:|---:|---:|---:|
| `T1/S01` | 4.0 | 10.7 | 30.0 | 124.2 | 316.0 |
| `T2/S03` | 5.0 | 11.0 | 28.5 | 92.2 | 284.1 |
| `T2/S04` | 4.0 | 8.0 | 20.0 | 56.5 | 194.5 |
| `T3/S06` | 12.6 | 62.5 | 118.5 | 207.5 | 1025.5 |
| `T4/S08` | 2.4 | 6.0 | 14.0 | 55.5 | 123.8 |
| `T5/S09` | 9.9 | 31.8 | 114.5 | 220.7 | 578.2 |
| `T5/S10` | 22.0 | 61.5 | 231.0 | 441.5 | 2252.2 |
| `T6/S12` | 5.0 | 12.0 | 36.0 | 90.5 | 155.0 |

## Exit Move From Basket Entry VWAP

| Strategy | q10 | q25 | median | q75 | q90 |
|---|---:|---:|---:|---:|---:|
| `T1/S01` | 0.52 | 0.57 | 0.71 | 1.08 | 2.04 |
| `T2/S03` | 0.52 | 0.56 | 0.68 | 0.98 | 2.05 |
| `T2/S04` | 0.52 | 0.57 | 0.66 | 0.81 | 1.13 |
| `T3/S06` | 0.53 | 0.57 | 0.65 | 0.93 | 1.37 |
| `T4/S08` | 1.56 | 1.58 | 1.70 | 1.91 | 2.26 |
| `T5/S09` | 2.06 | 2.10 | 2.25 | 2.63 | 3.40 |
| `T5/S10` | -0.05 | 0.82 | 2.05 | 2.34 | 3.92 |
| `T6/S12` | 1.03 | 1.09 | 1.20 | 1.49 | 1.82 |

## Initial Interpretation

- High basket win rates confirm that management/exit behavior is central to QQ's edge.
- Add-on spacing should next be modeled as a per-minute classification problem using `basket_minute_lifecycle.parquet` negatives and `lifecycle_add_on_events.parquet` positives.
- Exit detection should next test whether final exits occur at fixed basket PnL, fixed points above/below entry VWAP, or layer-dependent TP thresholds.
