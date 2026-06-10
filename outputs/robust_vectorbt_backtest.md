# Vectorbt Backtest of Robust Approximate Rules

## Scope

- Uses only M15 close data and the robust approximate entry-rule variants from `strategy_rule_synthesis.csv`.
- Long-only, one-unit position sizing, no grid/add-on management, no inferred EA take-profit/stop-loss logic, no fees/slippage.
- Entry is the rule mask changing from false to true; exit is the rule mask changing from true to false.
- This tests whether the inferred context filters have standalone directional edge, not whether they reproduce Quantum Queen's managed basket PnL.

## Results

| Strategy | Variant | Return % | Max DD % | Sharpe | Trades | Win rate % | Signal bars |
|---|---|---:|---:|---:|---:|---:|---:|
| `T2/S03` | `all_background` | 1.65 | -1.47 | 0.46 | 494 | 36.44 | 4528 |
| `T2/S03` | `matched_context` | 1.14 | -1.97 | 0.31 | 445 | 41.80 | 5217 |
| `T2/S04` | `all_background` | -0.75 | -1.86 | -0.26 | 353 | 36.83 | 2306 |
| `T2/S04` | `matched_context` | 0.01 | -1.00 | 0.01 | 269 | 37.17 | 1477 |
| `T5/S10` | `all_background` | 0.12 | -1.66 | 0.05 | 841 | 38.76 | 4499 |
| `T5/S10` | `matched_context` | -1.68 | -2.33 | -0.49 | 1459 | 37.77 | 6351 |

## Rules

- `T2/S03` / `all_background`: `wma_21_minus_wma_50 >= 3.9578 AND ao >= 5.9092 AND roc_34 >= 0.8333`
- `T2/S03` / `matched_context`: `wma_50_slope_4 >= 1.3709 AND wma_21_minus_wma_50 >= 3.9578 AND sma_21_slope_4 >= 1.8114`
- `T2/S04` / `all_background`: `roc_20 >= 0.7826 AND wma_21_minus_wma_50 >= 4.6549 AND wma_21_slope_4 >= 2.3062`
- `T2/S04` / `matched_context`: `adx_21_dmn_21 <= 11.2552 AND roc_34 >= 0.8966 AND sma_21_slope_4 >= 2.3986`
- `T5/S10` / `all_background`: `fisher_14 >= 2.8407 AND wma_8_minus_wma_21 >= 1.4301 AND adx_7_adx_7 >= 49.5708`
- `T5/S10` / `matched_context`: `fisher_9 >= 2.5008 AND sma_8_slope_4 >= 1.7187`
