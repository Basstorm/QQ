# Temporal and Matched-Negative Rule Validation

## Scope

- Split time: `2021-01-01`. Rules are mined only on rows before the split and evaluated on rows at/after the split.
- Two modes are reported: all M15 background bars, and negatives matched to the strategy's positive entry bars by broker weekday + hour.
- This validates whether candidate indicator rules survive time separation; it still does not prove EA source rules.

## Positive sample counts

| Strategy | Train positives | Test positives |
|---|---:|---:|
| `T1/S01` | 196 | 181 |
| `T2/S03` | 153 | 165 |
| `T2/S04` | 187 | 191 |
| `T3/S06` | 42 | 41 |
| `T4/S08` | 28 | 19 |
| `T5/S09` | 38 | 29 |
| `T5/S10` | 57 | 47 |
| `T6/S12` | 92 | 67 |

## Top validated rules

### T1/S01 — all_background

| Rule | Train lift | Test lift | Train recall | Test recall | Test precision | Test matched |
|---|---:|---:|---:|---:|---:|---:|
| `fisher_9 >= 2.5788 AND wma_21_slope_4 >= 1.2686 AND ema_8_slope_4 >= 1.4224` | 9.6x | 9.0x | 0.321 | 0.425 | 0.0231 | 3332 |
| `fisher_9 >= 2.5788 AND wma_21_slope_4 >= 1.2686` | 9.4x | 9.0x | 0.352 | 0.459 | 0.0231 | 3595 |
| `fisher_9 >= 2.5788 AND wma_21_slope_4 >= 1.2686 AND close_minus_sma_21 >= 3.1386` | 9.3x | 9.0x | 0.321 | 0.425 | 0.0230 | 3351 |
| `fisher_9 >= 2.5788 AND ema_8_slope_4 >= 1.4224 AND close_minus_sma_21 >= 3.1386` | 9.0x | 8.8x | 0.316 | 0.431 | 0.0226 | 3444 |
| `fisher_9 >= 2.5788 AND wma_8_minus_wma_21 >= 1.4497 AND wma_21_slope_4 >= 1.2686` | 9.5x | 8.7x | 0.342 | 0.431 | 0.0222 | 3507 |

### T2/S03 — all_background

| Rule | Train lift | Test lift | Train recall | Test recall | Test precision | Test matched |
|---|---:|---:|---:|---:|---:|---:|
| `wma_21_minus_wma_50 >= 3.9578 AND ao >= 5.9092 AND roc_34 >= 0.8333` | 15.2x | 15.6x | 0.412 | 0.564 | 0.0363 | 2559 |
| `wma_21_minus_wma_50 >= 3.9578 AND roc_34 >= 0.8333 AND sma_21_slope_4 >= 1.8114` | 15.9x | 15.0x | 0.399 | 0.491 | 0.0350 | 2311 |
| `wma_21_minus_wma_50 >= 3.9578 AND roc_34 >= 0.8333 AND ema_50_slope_4 >= 1.1134` | 14.9x | 14.8x | 0.418 | 0.570 | 0.0346 | 2714 |
| `ao >= 5.9092 AND roc_34 >= 0.8333 AND ema_50_slope_4 >= 1.1134` | 13.8x | 14.8x | 0.405 | 0.558 | 0.0346 | 2662 |
| `ao >= 5.9092 AND wma_50_slope_4 >= 1.3709 AND roc_34 >= 0.8333` | 14.0x | 14.7x | 0.418 | 0.564 | 0.0342 | 2716 |

### T2/S04 — all_background

| Rule | Train lift | Test lift | Train recall | Test recall | Test precision | Test matched |
|---|---:|---:|---:|---:|---:|---:|
| `roc_20 >= 0.7826 AND wma_21_minus_wma_50 >= 4.6549 AND wma_21_slope_4 >= 2.3062` | 27.2x | 26.0x | 0.369 | 0.487 | 0.0702 | 1324 |
| `sma_21_slope_4 >= 2.3986 AND wma_21_minus_wma_50 >= 4.6549 AND wma_21_slope_4 >= 2.3062` | 25.6x | 25.6x | 0.396 | 0.571 | 0.0693 | 1572 |
| `ema_8_minus_ema_21 >= 3.3502 AND wma_21_minus_wma_50 >= 4.6549 AND wma_21_slope_4 >= 2.3062` | 24.6x | 25.6x | 0.406 | 0.586 | 0.0693 | 1617 |
| `roc_20 >= 0.7826 AND ema_8_minus_ema_21 >= 3.3502 AND wma_21_minus_wma_50 >= 4.6549` | 26.4x | 24.8x | 0.385 | 0.497 | 0.0670 | 1418 |
| `roc_20 >= 0.7826 AND wma_21_minus_wma_50 >= 4.6549 AND wma_50_slope_4 >= 1.7044` | 25.7x | 24.6x | 0.390 | 0.508 | 0.0666 | 1456 |

### T3/S06 — all_background

| Rule | Train lift | Test lift | Train recall | Test recall | Test precision | Test matched |
|---|---:|---:|---:|---:|---:|---:|
| `rsi_34 <= 35.3682 AND ema_21_minus_ema_50 <= -3.2949 AND wma_50_slope_4 <= -1.0769` | 24.8x | 13.7x | 0.357 | 0.366 | 0.0080 | 1883 |
| `rsi_34 <= 35.3682 AND roc_34 <= -0.7694 AND ema_21_minus_ema_50 <= -3.2949` | 26.8x | 13.2x | 0.357 | 0.293 | 0.0077 | 1565 |
| `adx_21_dmp_21 <= 10.5209 AND ema_21_minus_ema_50 <= -3.2949 AND wma_50_slope_4 <= -1.0769` | 27.2x | 12.8x | 0.333 | 0.268 | 0.0074 | 1482 |
| `adx_21_dmp_21 <= 10.5209 AND ema_50_slope_4 <= -0.9347 AND ema_21_minus_ema_50 <= -3.2949` | 27.2x | 12.7x | 0.333 | 0.268 | 0.0074 | 1487 |
| `adx_21_dmp_21 <= 10.5209 AND ema_21_minus_ema_50 <= -3.2949` | 28.3x | 12.6x | 0.357 | 0.268 | 0.0073 | 1499 |

### T4/S08 — all_background

| Rule | Train lift | Test lift | Train recall | Test recall | Test precision | Test matched |
|---|---:|---:|---:|---:|---:|---:|
| `adx_21_adx_21 >= 50.6542 AND ema_21_minus_ema_50 >= 7.2221 AND close_minus_ema_50 >= 15.5052` | 351.1x | 63.0x | 0.286 | 0.053 | 0.0169 | 59 |
| `adx_21_adx_21 >= 50.6542 AND close_minus_ema_50 >= 15.5052 AND sma_50_slope_4 >= 2.3313` | 345.2x | 63.0x | 0.286 | 0.053 | 0.0169 | 59 |
| `adx_21_adx_21 >= 50.6542 AND close_minus_ema_50 >= 15.5052` | 339.5x | 60.9x | 0.286 | 0.053 | 0.0164 | 61 |
| `adx_21_adx_21 >= 50.6542 AND ema_50_slope_4 >= 2.2413 AND close_minus_ema_50 >= 15.5052` | 307.2x | 60.9x | 0.250 | 0.053 | 0.0164 | 61 |
| `adx_21_adx_21 >= 50.6542 AND ema_50_slope_4 >= 2.2413 AND sma_50_slope_4 >= 2.3313` | 240.8x | 59.0x | 0.286 | 0.053 | 0.0159 | 63 |

### T5/S09 — all_background

| Rule | Train lift | Test lift | Train recall | Test recall | Test precision | Test matched |
|---|---:|---:|---:|---:|---:|---:|
| `fisher_9 >= 3.9664 AND adx_7_adx_7 >= 70.7447 AND cmo_21 >= 59.3097` | 130.7x | 48.7x | 0.263 | 0.103 | 0.0200 | 150 |
| `fisher_9 >= 3.9664 AND adx_7_adx_7 >= 70.7447` | 106.0x | 45.8x | 0.316 | 0.172 | 0.0188 | 266 |
| `adx_7_adx_7 >= 70.7447 AND adx_14_dmp_14 >= 40.6574` | 122.7x | 42.7x | 0.289 | 0.069 | 0.0175 | 114 |
| `fisher_14 >= 4.2594 AND adx_7_adx_7 >= 70.7447` | 102.9x | 35.2x | 0.342 | 0.138 | 0.0144 | 277 |
| `fisher_9 >= 3.9664 AND cmo_21 >= 59.3097` | 90.2x | 25.0x | 0.368 | 0.103 | 0.0103 | 292 |

### T5/S10 — all_background

| Rule | Train lift | Test lift | Train recall | Test recall | Test precision | Test matched |
|---|---:|---:|---:|---:|---:|---:|
| `fisher_14 >= 2.8407 AND wma_8_minus_wma_21 >= 1.4301 AND adx_7_adx_7 >= 49.5708` | 10.8x | 10.8x | 0.298 | 0.383 | 0.0072 | 2499 |
| `fisher_9 >= 2.5008 AND fisher_14 >= 2.8407 AND sma_8_slope_4 >= 1.7187` | 10.9x | 10.4x | 0.316 | 0.404 | 0.0069 | 2740 |
| `fisher_9 >= 2.5008 AND fisher_14 >= 2.8407 AND adx_7_adx_7 >= 49.5708` | 10.6x | 10.2x | 0.386 | 0.362 | 0.0068 | 2504 |
| `fisher_9 >= 2.5008 AND adx_7_adx_7 >= 49.5708 AND wma_21_slope_4 >= 1.2492` | 10.4x | 10.2x | 0.281 | 0.362 | 0.0068 | 2514 |
| `fisher_14 >= 2.8407 AND sma_8_slope_4 >= 1.7187 AND adx_7_adx_7 >= 49.5708` | 13.3x | 10.1x | 0.298 | 0.298 | 0.0067 | 2080 |

### T6/S12 — all_background

| Rule | Train lift | Test lift | Train recall | Test recall | Test precision | Test matched |
|---|---:|---:|---:|---:|---:|---:|
| `adx_7_dmp_7 <= 4.6586 AND cci_20 <= -184.4820 AND cmo_9 <= -63.4493` | 53.8x | 36.8x | 0.283 | 0.164 | 0.0349 | 315 |
| `adx_7_dmp_7 <= 4.6586 AND adx_7_dmn_7 >= 41.8687 AND cci_20 <= -184.4820` | 52.7x | 34.7x | 0.272 | 0.134 | 0.0330 | 273 |
| `adx_7_dmp_7 <= 4.6586 AND cci_20 <= -184.4820 AND rsi_8 <= 24.4583` | 45.9x | 32.2x | 0.272 | 0.164 | 0.0306 | 360 |
| `adx_7_dmp_7 <= 4.6586 AND cci_20 <= -184.4820 AND bbands_34_bbp_34_2_0 <= -0.0438` | 48.6x | 28.7x | 0.304 | 0.149 | 0.0272 | 367 |
| `adx_7_dmp_7 <= 4.6586 AND adx_7_dmn_7 >= 41.8687` | 34.4x | 27.7x | 0.326 | 0.209 | 0.0263 | 533 |

### T1/S01 — matched_hour_weekday

| Rule | Train lift | Test lift | Train recall | Test recall | Test precision | Test matched |
|---|---:|---:|---:|---:|---:|---:|
| `cci_20 >= 130.5291 AND adx_7_dmn_7 <= 8.1907 AND adx_7_dmp_7 >= 33.2559` | 18.0x | 18.6x | 0.240 | 0.210 | 0.5846 | 65 |
| `adx_7_dmn_7 <= 8.1907 AND adx_7_dmp_7 >= 33.2559 AND bbands_20_bbp_20_2_0 >= 0.8876` | 17.7x | 17.3x | 0.260 | 0.210 | 0.5429 | 70 |
| `cci_20 >= 130.5291 AND adx_7_dmn_7 <= 8.1907 AND close_minus_sma_21 >= 3.1386` | 17.1x | 15.9x | 0.255 | 0.249 | 0.5000 | 90 |
| `cci_20 >= 130.5291 AND fisher_9 >= 2.5788 AND adx_7_dmn_7 <= 8.1907` | 17.6x | 15.7x | 0.250 | 0.215 | 0.4937 | 79 |
| `adx_7_dmn_7 <= 8.1907 AND adx_7_dmp_7 >= 33.2559` | 14.3x | 15.4x | 0.306 | 0.309 | 0.4828 | 116 |

### T2/S03 — matched_hour_weekday

| Rule | Train lift | Test lift | Train recall | Test recall | Test precision | Test matched |
|---|---:|---:|---:|---:|---:|---:|
| `wma_50_slope_4 >= 1.3709 AND wma_21_minus_wma_50 >= 3.9578 AND sma_21_slope_4 >= 1.8114` | 11.4x | 8.4x | 0.399 | 0.588 | 0.3865 | 251 |
| `wma_50_slope_4 >= 1.3709 AND close_minus_wma_50 >= 5.8526 AND sma_21_slope_4 >= 1.8114` | 10.6x | 8.2x | 0.392 | 0.570 | 0.3790 | 248 |
| `wma_50_slope_4 >= 1.3709 AND close_minus_sma_50 >= 7.9084 AND sma_21_slope_4 >= 1.8114` | 10.7x | 8.2x | 0.399 | 0.606 | 0.3788 | 264 |
| `ao >= 5.9092 AND wma_50_slope_4 >= 1.3709 AND sma_21_slope_4 >= 1.8114` | 10.8x | 8.2x | 0.412 | 0.606 | 0.3774 | 265 |
| `close_minus_sma_50 >= 7.9084 AND ema_50_slope_4 >= 1.1134 AND sma_21_slope_4 >= 1.8114` | 10.3x | 8.1x | 0.405 | 0.606 | 0.3731 | 268 |

### T2/S04 — matched_hour_weekday

| Rule | Train lift | Test lift | Train recall | Test recall | Test precision | Test matched |
|---|---:|---:|---:|---:|---:|---:|
| `adx_21_dmn_21 <= 11.2552 AND roc_34 >= 0.8966 AND sma_21_slope_4 >= 2.3986` | 12.3x | 12.2x | 0.310 | 0.288 | 0.6322 | 87 |
| `adx_21_dmn_21 <= 11.2552 AND sma_21_slope_4 >= 2.3986` | 12.3x | 12.0x | 0.310 | 0.382 | 0.6239 | 117 |
| `adx_21_dmn_21 <= 11.2552 AND roc_20 >= 0.7826` | 12.6x | 12.0x | 0.310 | 0.304 | 0.6237 | 93 |
| `adx_21_dmn_21 <= 11.2552 AND rsi_34 >= 64.0381` | 10.6x | 11.7x | 0.358 | 0.314 | 0.6061 | 99 |
| `adx_14_dmn_14 <= 9.8632 AND roc_20 >= 0.7826` | 12.8x | 11.7x | 0.294 | 0.272 | 0.6047 | 86 |

### T3/S06 — matched_hour_weekday

| Rule | Train lift | Test lift | Train recall | Test recall | Test precision | Test matched |
|---|---:|---:|---:|---:|---:|---:|
| `adx_21_dmn_21 >= 32.7915 AND rsi_14 <= 29.5372 AND adx_21_dmp_21 <= 10.5209` | 38.7x | 34.1x | 0.286 | 0.122 | 0.5000 | 10 |
| `rsi_21 <= 33.1633 AND adx_21_dmp_21 <= 10.5209 AND cmo_21 <= -45.5363` | 31.6x | 29.2x | 0.333 | 0.146 | 0.4286 | 14 |
| `rsi_34 <= 35.3682 AND adx_21_dmp_21 <= 10.5209 AND cmo_21 <= -45.5363` | 32.8x | 29.2x | 0.357 | 0.146 | 0.4286 | 14 |
| `adx_21_dmp_21 <= 10.5209 AND cmo_21 <= -45.5363` | 30.8x | 25.6x | 0.357 | 0.146 | 0.3750 | 16 |
| `rsi_34 <= 35.3682 AND adx_21_dmn_21 >= 32.7915 AND adx_14_dmp_14 <= 10.1498` | 36.7x | 24.1x | 0.310 | 0.146 | 0.3529 | 17 |

### T4/S08 — matched_hour_weekday

| Rule | Train lift | Test lift | Train recall | Test recall | Test precision | Test matched |
|---|---:|---:|---:|---:|---:|---:|
| `adx_21_adx_21 >= 50.6542 AND close_minus_ema_50 >= 15.5052` | 263.9x | 355.8x | 0.286 | 0.053 | 1.0000 | 1 |
| `ema_21_minus_ema_50 >= 7.2221 AND adx_21_adx_21 >= 50.6542 AND close_minus_ema_50 >= 15.5052` | 263.9x | 355.8x | 0.286 | 0.053 | 1.0000 | 1 |
| `adx_21_adx_21 >= 50.6542 AND close_minus_ema_50 >= 15.5052 AND sma_50_slope_4 >= 2.3313` | 263.9x | 355.8x | 0.286 | 0.053 | 1.0000 | 1 |
| `adx_21_adx_21 >= 50.6542 AND close_minus_ema_50 >= 15.5052 AND wma_50_slope_4 >= 2.4245` | 263.9x | 355.8x | 0.286 | 0.053 | 1.0000 | 1 |
| `adx_21_adx_21 >= 50.6542 AND close_minus_ema_50 >= 15.5052 AND sma_21_minus_sma_50 >= 6.6422` | 263.9x | 355.8x | 0.286 | 0.053 | 1.0000 | 1 |

### T5/S09 — matched_hour_weekday

| Rule | Train lift | Test lift | Train recall | Test recall | Test precision | Test matched |
|---|---:|---:|---:|---:|---:|---:|
| `cmo_14 >= 70.0936 AND cmo_21 >= 59.3097 AND chop_14 <= 28.5623` | 98.0x | 127.4x | 0.263 | 0.034 | 0.5000 | 2 |
| `cmo_21 >= 59.3097 AND chop_14 <= 28.5623 AND adx_14_dmp_14 >= 40.6574` | 103.3x | 85.0x | 0.316 | 0.034 | 0.3333 | 3 |
| `cmo_21 >= 59.3097 AND chop_14 <= 28.5623` | 90.1x | 85.0x | 0.342 | 0.034 | 0.3333 | 3 |
| `cmo_21 >= 59.3097 AND chop_14 <= 28.5623 AND wma_21_slope_4 >= 2.2829` | 111.2x | 85.0x | 0.237 | 0.034 | 0.3333 | 3 |
| `cmo_14 >= 70.0936 AND chop_14 <= 28.5623 AND adx_14_dmp_14 >= 40.6574` | 97.7x | 63.7x | 0.289 | 0.034 | 0.2500 | 4 |

### T5/S10 — matched_hour_weekday

| Rule | Train lift | Test lift | Train recall | Test recall | Test precision | Test matched |
|---|---:|---:|---:|---:|---:|---:|
| `fisher_9 >= 2.5008 AND sma_8_slope_4 >= 1.7187` | 11.2x | 15.2x | 0.333 | 0.574 | 0.1071 | 252 |
| `fisher_9 >= 2.5008 AND wma_8_minus_wma_21 >= 1.4301 AND sma_8_slope_4 >= 1.7187` | 10.8x | 15.1x | 0.316 | 0.553 | 0.1066 | 244 |
| `fisher_14 >= 2.8407 AND sma_8_slope_4 >= 1.7187 AND adx_7_adx_7 >= 49.5708` | 16.9x | 14.5x | 0.298 | 0.298 | 0.1022 | 137 |
| `fisher_9 >= 2.5008 AND sma_8_slope_4 >= 1.7187 AND adx_7_adx_7 >= 49.5708` | 16.6x | 14.3x | 0.298 | 0.298 | 0.1007 | 139 |
| `fisher_9 >= 2.5008 AND fisher_14 >= 2.8407 AND sma_8_slope_4 >= 1.7187` | 13.3x | 14.2x | 0.316 | 0.404 | 0.1000 | 190 |

### T6/S12 — matched_hour_weekday

| Rule | Train lift | Test lift | Train recall | Test recall | Test precision | Test matched |
|---|---:|---:|---:|---:|---:|---:|
| `adx_7_dmp_7 <= 4.6586 AND cci_34 <= -205.1435 AND cmo_9 <= -63.4493` | 26.9x | 34.5x | 0.250 | 0.134 | 0.3750 | 24 |
| `adx_7_dmp_7 <= 4.6586 AND cci_34 <= -205.1435` | 27.8x | 28.6x | 0.337 | 0.134 | 0.3103 | 29 |
| `adx_7_dmp_7 <= 4.6586 AND cci_34 <= -205.1435 AND rsi_14 <= 31.1776` | 26.1x | 28.0x | 0.272 | 0.104 | 0.3043 | 23 |
| `adx_7_dmp_7 <= 4.6586 AND adx_14_dmp_14 <= 9.7092 AND cci_34 <= -205.1435` | 27.4x | 27.3x | 0.293 | 0.119 | 0.2963 | 27 |
| `adx_7_dmp_7 <= 4.6586 AND ema_8_slope_4 <= -1.5769` | 21.8x | 26.3x | 0.272 | 0.358 | 0.2857 | 84 |

## Interpretation guide

- Rules with both train and test lift above baseline are more credible than full-sample rules.
- Rules with high train lift but weak test lift are likely overfit or regime-specific.
- Matched mode is stricter because it compares entries against non-entry bars from similar weekday/hour contexts.
