# Phase 6 Risk / Timeout Exit Mining

## Scope

- Lightweight diagnostic focused on observed QQ baskets, not a new optimized stop-loss model.
- Primary targets are `T3/S06` and `T6/S12`, because Phase 5 backtests exposed tail risk there.
- Candidate timeout levels are descriptive quantiles of real QQ basket holding time and adverse excursion.

| Strategy | Baskets | Negative exits | Hold median | Hold q75 | Hold q90 | Hold q95 | Adverse median | Adverse q90 | Exit q10 | Exit median | Max layers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `T3/S06` | 99 | 1 | 75.0 | 430.5 | 3005.2 | 3131.9 | 1.04 | 4.87 | 0.48 | 0.86 | 188 |
| `T6/S12` | 166 | 0 | 45.0 | 123.2 | 405.0 | 571.5 | 1.62 | 5.46 | 0.93 | 1.48 | 25 |

## Interpretation

- A practical first timeout cap should be conservative: near observed `hold_q95`, not fitted to maximize this sample.
- A separate adverse-excursion kill switch is not supported yet unless adverse tails are far beyond normal observed QQ baskets.
- Use these values only as candidate risk-control bounds for the next backtest pass.
