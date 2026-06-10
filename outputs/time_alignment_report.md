# Phase 1 Trade Reconstruction and Time Alignment Report

## Executive Summary

- Normalized XAUUSD deals: `11310`.
- Entry deals: `5655`; exit deals: `5655`.
- Reconstructed position fragments: `6100`.
- Reconstructed baskets: `1657`.
- Position PnL estimate: `1347268.41`.
- Reported exit-deal profit sum: `1347268.41`.
- PnL reconstruction difference: `0.00000000`.
- M1 match rate at tolerance 0.25, all deals: `0.9908`.
- M1 match rate at tolerance 0.25, entry deals: `0.9827`.
- FIFO reconstruction is consistent with the report PnL, so blank exit comments can be assigned back to entry strategies through directional FIFO matching.

## Strategy-Level Reconstruction Summary

| Strategy | Positions | Baskets | Volume | PnL est | Avg hold min | Avg positions/basket | P95 max layers |
|---|---:|---:|---:|---:|---:|---:|---:|
| T1/S01 | 1769 | 459 | 39578.11 | 4625172.10 | 484.36 | 3.85 | 12.0 |
| T2/S03 | 1193 | 318 | 27281.14 | 2774986.27 | 369.10 | 3.75 | 12.4 |
| T2/S04 | 1231 | 378 | 31561.60 | 2246850.28 | 200.16 | 3.26 | 9.0 |
| T3/S06 | 402 | 99 | 8374.30 | -14994461.54 | 4445.38 | 4.06 | 6.1 |
| T4/S08 | 231 | 58 | 5433.76 | 1014496.77 | 110.87 | 3.98 | 14.1 |
| T5/S09 | 234 | 71 | 5846.26 | 1520356.22 | 374.85 | 3.30 | 9.0 |
| T5/S10 | 386 | 108 | 9382.97 | 2101890.16 | 624.31 | 3.57 | 9.0 |
| T6/S12 | 654 | 166 | 15372.47 | 2057978.15 | 216.66 | 3.94 | 12.0 |

## M15 Timing Diagnostics

- Share of all entry deals at broker minute `% 15 == 0`: `0.3866`.
- Share of basket first entries at broker minute `% 15 == 0`: `0.6270`.
- This does not yet prove or disprove the user's M15-entry model. Entry deals include both initial entries and add-ons. Basket construction is interval-based and may split/merge differently from the EA's internal cycle IDs. Phase 2 should identify initial signal entries more carefully before drawing final conclusions about M15 gating.

### All entry deals: broker minute modulo 15

| minute % 15 | count |
|---:|---:|
| 0 | 2186 |
| 1 | 157 |
| 2 | 147 |
| 3 | 550 |
| 4 | 143 |
| 5 | 365 |
| 6 | 464 |
| 7 | 153 |
| 8 | 129 |
| 9 | 370 |
| 10 | 243 |
| 11 | 144 |
| 12 | 353 |
| 13 | 142 |
| 14 | 109 |

### Basket first entries: broker minute modulo 15

| minute % 15 | count |
|---:|---:|
| 0 | 1039 |
| 1 | 5 |
| 2 | 1 |
| 3 | 172 |
| 5 | 70 |
| 6 | 122 |
| 8 | 3 |
| 9 | 106 |
| 10 | 53 |
| 11 | 2 |
| 12 | 83 |
| 14 | 1 |

## Seconds Diagnostics

### Entry deal second values

| second | count |
|---:|---:|
| 0 | 4820 |
| 1 | 790 |
| 2 | 31 |
| 3 | 9 |
| 4 | 5 |

### Exit deal second values

| second | count |
|---:|---:|
| 0 | 3685 |
| 1 | 1093 |
| 2 | 420 |
| 3 | 219 |
| 4 | 96 |
| 5 | 45 |
| 6 | 29 |
| 7 | 21 |
| 8 | 9 |
| 9 | 5 |
| 10 | 5 |
| 11 | 5 |
| 12 | 5 |
| 13 | 5 |
| 14 | 3 |
| 20 | 6 |
| 21 | 4 |

## Output Files

- `outputs/trades_normalized.parquet`
- `outputs/positions.parquet`
- `outputs/baskets.parquet`
- `outputs/time_alignment_report.md`

## Phase 2 Notes

1. Use `strategy` from reconstructed positions for per-strategy behavior profiling.
2. Preserve `broker_time` semantics for candle joins; use `utc_time_est = broker_time - 3h` for session labeling experiments.
3. Initial-entry detection needs refinement beyond interval baskets because add-on entries are represented as normal `in` deals.
4. Basket IDs are reconstructed analytical cycle IDs, not native EA IDs.
