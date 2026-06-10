# Final Approximate Strategy Rule Synthesis

## Scope

- This is not source-code recovery. It is a ranked synthesis of observed backtest behavior, expanded indicator discovery, candidate rules, and temporal validation.
- Temporal validation has the highest weight; full-sample rules without temporal support should be treated as weak hypotheses.
- `sparse_hint` means a rule has high lift but too few test matches or too little recall to trust as a robust rule.

## Summary Table

| Strategy | Candidate family | Overall confidence | All-background rule | Matched-context rule |
|---|---|---|---|---|
| `T1/S01` | overbought momentum / trend continuation context | **moderate** | `fisher_9 >= 2.5788 AND wma_21_slope_4 >= 1.2686 AND ema_8_slope_4 >= 1.4224` | `cci_20 >= 130.5291 AND adx_7_dmn_7 <= 8.1907 AND adx_7_dmp_7 >= 33.2559` |
| `T2/S03` | overbought momentum / trend continuation context | **robust** | `wma_21_minus_wma_50 >= 3.9578 AND ao >= 5.9092 AND roc_34 >= 0.8333` | `wma_50_slope_4 >= 1.3709 AND wma_21_minus_wma_50 >= 3.9578 AND sma_21_slope_4 >= 1.8114` |
| `T2/S04` | overbought momentum / trend continuation context | **robust** | `roc_20 >= 0.7826 AND wma_21_minus_wma_50 >= 4.6549 AND wma_21_slope_4 >= 2.3062` | `adx_21_dmn_21 <= 11.2552 AND roc_34 >= 0.8966 AND sma_21_slope_4 >= 2.3986` |
| `T3/S06` | oversold pullback / downtrend continuation context | **moderate** | `rsi_34 <= 35.3682 AND ema_21_minus_ema_50 <= -3.2949 AND wma_50_slope_4 <= -1.0769` | `adx_21_dmn_21 >= 32.7915 AND rsi_14 <= 29.5372 AND adx_21_dmp_21 <= 10.5209` |
| `T4/S08` | trend breakout / momentum continuation | **sparse_hint** | `adx_21_adx_21 >= 50.6542 AND ema_21_minus_ema_50 >= 7.2221 AND close_minus_ema_50 >= 15.5052` | `adx_21_adx_21 >= 50.6542 AND close_minus_ema_50 >= 15.5052` |
| `T5/S09` | trend breakout / momentum continuation | **tentative** | `fisher_9 >= 3.9664 AND adx_7_adx_7 >= 70.7447 AND cmo_21 >= 59.3097` | `cmo_14 >= 70.0936 AND cmo_21 >= 59.3097 AND chop_14 <= 28.5623` |
| `T5/S10` | overbought momentum / trend continuation context | **robust** | `fisher_14 >= 2.8407 AND wma_8_minus_wma_21 >= 1.4301 AND adx_7_adx_7 >= 49.5708` | `fisher_9 >= 2.5008 AND sma_8_slope_4 >= 1.7187` |
| `T6/S12` | downtrend breakout / short momentum continuation | **tentative** | `adx_7_dmp_7 <= 4.6586 AND cci_20 <= -184.4820 AND cmo_9 <= -63.4493` | `adx_7_dmp_7 <= 4.6586 AND cci_34 <= -205.1435 AND cmo_9 <= -63.4493` |

## Per-Strategy Detail

### T1/S01

- Candidate family: overbought momentum / trend continuation context.
- Overall confidence: **moderate**.
- All-background: moderate; test lift `9.0x`, test recall `0.425`.
- Matched-context: moderate; test lift `18.6x`, test recall `0.210`, test precision `0.5846`, matched rows `65`.
- Best all-background rule: `fisher_9 >= 2.5788 AND wma_21_slope_4 >= 1.2686 AND ema_8_slope_4 >= 1.4224`.
- Best matched-context rule: `cci_20 >= 130.5291 AND adx_7_dmn_7 <= 8.1907 AND adx_7_dmp_7 >= 33.2559`.

### T2/S03

- Candidate family: overbought momentum / trend continuation context.
- Overall confidence: **robust**.
- All-background: robust; test lift `15.6x`, test recall `0.564`.
- Matched-context: moderate; test lift `8.4x`, test recall `0.588`, test precision `0.3865`, matched rows `251`.
- Best all-background rule: `wma_21_minus_wma_50 >= 3.9578 AND ao >= 5.9092 AND roc_34 >= 0.8333`.
- Best matched-context rule: `wma_50_slope_4 >= 1.3709 AND wma_21_minus_wma_50 >= 3.9578 AND sma_21_slope_4 >= 1.8114`.

### T2/S04

- Candidate family: overbought momentum / trend continuation context.
- Overall confidence: **robust**.
- All-background: robust; test lift `26.0x`, test recall `0.487`.
- Matched-context: moderate; test lift `12.2x`, test recall `0.288`, test precision `0.6322`, matched rows `87`.
- Best all-background rule: `roc_20 >= 0.7826 AND wma_21_minus_wma_50 >= 4.6549 AND wma_21_slope_4 >= 2.3062`.
- Best matched-context rule: `adx_21_dmn_21 <= 11.2552 AND roc_34 >= 0.8966 AND sma_21_slope_4 >= 2.3986`.

### T3/S06

- Candidate family: oversold pullback / downtrend continuation context.
- Overall confidence: **moderate**.
- All-background: moderate; test lift `13.7x`, test recall `0.366`.
- Matched-context: tentative; test lift `34.1x`, test recall `0.122`, test precision `0.5000`, matched rows `10`.
- Best all-background rule: `rsi_34 <= 35.3682 AND ema_21_minus_ema_50 <= -3.2949 AND wma_50_slope_4 <= -1.0769`.
- Best matched-context rule: `adx_21_dmn_21 >= 32.7915 AND rsi_14 <= 29.5372 AND adx_21_dmp_21 <= 10.5209`.

### T4/S08

- Candidate family: trend breakout / momentum continuation.
- Overall confidence: **sparse_hint**.
- All-background: sparse_hint; test lift `63.0x`, test recall `0.053`.
- Matched-context: sparse_hint; test lift `355.8x`, test recall `0.053`, test precision `1.0000`, matched rows `1`.
- Best all-background rule: `adx_21_adx_21 >= 50.6542 AND ema_21_minus_ema_50 >= 7.2221 AND close_minus_ema_50 >= 15.5052`.
- Best matched-context rule: `adx_21_adx_21 >= 50.6542 AND close_minus_ema_50 >= 15.5052`.

### T5/S09

- Candidate family: trend breakout / momentum continuation.
- Overall confidence: **tentative**.
- All-background: tentative; test lift `48.7x`, test recall `0.103`.
- Matched-context: sparse_hint; test lift `127.4x`, test recall `0.034`, test precision `0.5000`, matched rows `2`.
- Best all-background rule: `fisher_9 >= 3.9664 AND adx_7_adx_7 >= 70.7447 AND cmo_21 >= 59.3097`.
- Best matched-context rule: `cmo_14 >= 70.0936 AND cmo_21 >= 59.3097 AND chop_14 <= 28.5623`.

### T5/S10

- Candidate family: overbought momentum / trend continuation context.
- Overall confidence: **robust**.
- All-background: moderate; test lift `10.8x`, test recall `0.383`.
- Matched-context: robust; test lift `15.2x`, test recall `0.574`, test precision `0.1071`, matched rows `252`.
- Best all-background rule: `fisher_14 >= 2.8407 AND wma_8_minus_wma_21 >= 1.4301 AND adx_7_adx_7 >= 49.5708`.
- Best matched-context rule: `fisher_9 >= 2.5008 AND sma_8_slope_4 >= 1.7187`.

### T6/S12

- Candidate family: downtrend breakout / short momentum continuation.
- Overall confidence: **tentative**.
- All-background: tentative; test lift `36.8x`, test recall `0.164`.
- Matched-context: tentative; test lift `34.5x`, test recall `0.134`, test precision `0.3750`, matched rows `24`.
- Best all-background rule: `adx_7_dmp_7 <= 4.6586 AND cci_20 <= -184.4820 AND cmo_9 <= -63.4493`.
- Best matched-context rule: `adx_7_dmp_7 <= 4.6586 AND cci_34 <= -205.1435 AND cmo_9 <= -63.4493`.

