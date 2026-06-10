# Phase 4 Approximate Strategy Profiles

## Scope and Caution

- These are approximate, evidence-based profiles from backtest behavior and reconstructed feature tables, not source-code recovery.
- Entry inference uses `is_initial_entry == True` rows to avoid mixing add-ons with initial M15 signal context.
- Compact features are used first. If a strategy remains ambiguous, use the expanded indicator/parameter discovery fallback described in the project plan.

## Expanded indicator fallback

- If compact features cannot explain an `Sxx`, search a broad public-indicator universe, not only common defaults.
- Include MA crossover/stacking features and broad `pandas-ta`/compatible indicator families with parameter grids.

## T1/S01

- Initial entries / baskets: `459` / `459`.
- Direction mix: long:1.00.
- Broker-session mix: off_session:1.00.
- PnL estimate: `4625172.10`.
- Avg holding minutes: `494.58`; avg add-ons/basket: `2.85`.
- Avg M1 MAE/MFE points: `2.38` / `1.26`.
- Candidate family: **overbought momentum / trend continuation context**.
- Confidence: `low`.
- Evidence: high RSI, positive M15 momentum.

### Entry-context differentiators

| Feature | Strategy median | Rest median | Delta | Effect | IQR band |
|---|---:|---:|---:|---:|---|
| `broker_entry_hour` | 22.000 | 19.000 | 3.000 | 1.00 | [22.000, 23.000] |
| `broker_entry_minute_mod_15` | 3.000 | 0.000 | 3.000 | 0.60 | [0.000, 6.000] |
| `m15_adx_14` | 28.659 | 39.367 | -10.707 | 0.57 | [21.375, 39.267] |
| `m15_momentum_8_close_points` | 4.130 | 1.840 | 2.290 | 0.40 | [2.320, 7.020] |
| `m15_breakout_above_recent_high_8_points` | -0.020 | -0.930 | 0.910 | 0.39 | [-0.500, 0.730] |
| `m15_macd_hist_12_26_9` | 0.420 | 0.108 | 0.311 | 0.36 | [0.132, 0.888] |
| `m15_momentum_4_close_points` | 1.690 | 0.510 | 1.180 | 0.33 | [0.530, 3.625] |
| `m15_close_distance_to_ema_8` | 1.494 | 0.739 | 0.755 | 0.32 | [0.649, 2.748] |

### Management differentiators

| Feature | Strategy median | Rest median | Delta | Effect | IQR band |
|---|---:|---:|---:|---:|---|
| `m1_mfe_points` | 0.810 | 0.970 | -0.160 | 0.16 | [0.495, 1.370] |
| `holding_minutes` | 51.000 | 27.000 | 24.000 | 0.12 | [8.000, 284.008] |
| `add_on_spacing_minutes_mean` | 9.000 | 4.438 | 4.562 | 0.10 | [0.003, 64.172] |
| `add_on_spacing_price_abs_mean` | 0.615 | 0.466 | 0.149 | 0.09 | [0.000, 1.640] |
| `m1_mae_atr_14` | 0.633 | 0.535 | 0.098 | 0.08 | [0.222, 1.497] |
| `m1_time_to_mae_minutes` | 13.000 | 7.000 | 6.000 | 0.07 | [1.000, 157.000] |
| `m1_mae_points` | 1.400 | 1.250 | 0.150 | 0.06 | [0.550, 3.005] |
| `m1_time_to_mfe_minutes` | 12.000 | 10.000 | 2.000 | 0.05 | [3.000, 107.000] |

### Uncertainty

- This profile is descriptive and approximate. It may reflect shared basket management or market-regime effects rather than the exact EA entry rule.
- If the differentiators are weak or inconsistent, run the expanded indicator/parameter discovery fallback for this `Sxx`.

## T2/S03

- Initial entries / baskets: `318` / `318`.
- Direction mix: long:1.00.
- Broker-session mix: off_session:0.99, asia:0.01.
- PnL estimate: `2774986.27`.
- Avg holding minutes: `345.16`; avg add-ons/basket: `2.75`.
- Avg M1 MAE/MFE points: `2.04` / `1.17`.
- Candidate family: **overbought momentum / trend continuation context**.
- Confidence: `low`.
- Evidence: high RSI, positive M15 momentum.

### Entry-context differentiators

| Feature | Strategy median | Rest median | Delta | Effect | IQR band |
|---|---:|---:|---:|---:|---|
| `broker_entry_hour` | 22.000 | 19.000 | 3.000 | 1.00 | [22.000, 22.000] |
| `m15_macd_hist_12_26_9` | -0.120 | 0.279 | -0.399 | 0.46 | [-0.428, 0.234] |
| `m15_momentum_32_close_points` | 15.170 | 8.520 | 6.650 | 0.36 | [9.335, 25.507] |
| `m15_macd_12_26_9` | 2.945 | 1.974 | 0.972 | 0.29 | [1.831, 4.590] |
| `m15_adx_14` | 41.213 | 36.030 | 5.182 | 0.27 | [32.789, 47.949] |
| `m15_ema_50_slope_4` | 1.333 | 0.954 | 0.379 | 0.24 | [0.822, 2.151] |
| `m15_close_distance_to_ema_50` | 7.953 | 5.900 | 2.053 | 0.22 | [4.679, 13.577] |
| `m15_momentum_16_close_points` | 4.225 | 6.250 | -2.025 | 0.21 | [1.410, 8.343] |

### Management differentiators

| Feature | Strategy median | Rest median | Delta | Effect | IQR band |
|---|---:|---:|---:|---:|---|
| `add_on_spacing_price_abs_mean` | 0.302 | 0.624 | -0.322 | 0.19 | [0.000, 1.600] |
| `m1_mfe_points` | 0.810 | 0.960 | -0.150 | 0.15 | [0.530, 1.228] |
| `m1_mae_points` | 1.130 | 1.390 | -0.260 | 0.10 | [0.423, 2.387] |
| `m1_mae_atr_14` | 0.473 | 0.600 | -0.128 | 0.10 | [0.177, 1.033] |
| `m1_mfe_atr_14` | 0.363 | 0.406 | -0.043 | 0.09 | [0.223, 0.546] |
| `holding_minutes` | 20.008 | 33.000 | -12.992 | 0.06 | [7.000, 188.012] |
| `add_on_spacing_minutes_mean` | 4.000 | 6.333 | -2.333 | 0.05 | [0.002, 21.858] |
| `m1_time_to_mfe_minutes` | 10.000 | 11.000 | -1.000 | 0.02 | [2.000, 30.000] |

### Uncertainty

- This profile is descriptive and approximate. It may reflect shared basket management or market-regime effects rather than the exact EA entry rule.
- If the differentiators are weak or inconsistent, run the expanded indicator/parameter discovery fallback for this `Sxx`.

## T2/S04

- Initial entries / baskets: `378` / `378`.
- Direction mix: long:1.00.
- Broker-session mix: newyork:1.00, asia:0.00.
- PnL estimate: `2246850.28`.
- Avg holding minutes: `116.77`; avg add-ons/basket: `2.26`.
- Avg M1 MAE/MFE points: `1.89` / `0.94`.
- Candidate family: **overbought momentum / trend continuation context**.
- Confidence: `low`.
- Evidence: high RSI, positive M15 momentum.

### Entry-context differentiators

| Feature | Strategy median | Rest median | Delta | Effect | IQR band |
|---|---:|---:|---:|---:|---|
| `broker_entry_hour` | 19.000 | 22.000 | -3.000 | 1.00 | [19.000, 19.000] |
| `m15_momentum_16_close_points` | 11.090 | 4.590 | 6.500 | 0.66 | [6.590, 17.840] |
| `m15_ema_21_slope_4` | 2.318 | 1.145 | 1.173 | 0.59 | [1.506, 3.441] |
| `m15_macd_12_26_9` | 3.609 | 1.668 | 1.941 | 0.57 | [2.493, 5.006] |
| `m15_ema_50_slope_4` | 1.646 | 0.813 | 0.833 | 0.52 | [1.064, 2.368] |
| `m15_close_distance_to_ema_50` | 9.629 | 5.002 | 4.627 | 0.49 | [6.338, 14.079] |
| `m15_close_distance_to_ema_21` | 5.209 | 2.766 | 2.444 | 0.48 | [3.238, 8.042] |
| `m15_momentum_32_close_points` | 16.095 | 7.740 | 8.355 | 0.46 | [11.053, 22.953] |

### Management differentiators

| Feature | Strategy median | Rest median | Delta | Effect | IQR band |
|---|---:|---:|---:|---:|---|
| `m1_mfe_atr_14` | 0.296 | 0.439 | -0.143 | 0.30 | [0.204, 0.417] |
| `m1_mae_atr_14` | 0.307 | 0.659 | -0.351 | 0.27 | [0.136, 0.890] |
| `m1_mae_points` | 0.900 | 1.440 | -0.540 | 0.21 | [0.380, 2.248] |
| `m1_time_to_mfe_minutes` | 5.000 | 14.000 | -9.000 | 0.21 | [2.000, 15.000] |
| `m1_mfe_points` | 0.800 | 0.980 | -0.180 | 0.18 | [0.572, 1.130] |
| `add_on_spacing_price_abs_mean` | 0.328 | 0.594 | -0.266 | 0.16 | [0.000, 1.610] |
| `holding_minutes` | 11.000 | 43.017 | -32.017 | 0.15 | [3.017, 49.750] |
| `add_on_spacing_minutes_mean` | 1.857 | 7.001 | -5.144 | 0.12 | [0.000, 19.500] |

### Uncertainty

- This profile is descriptive and approximate. It may reflect shared basket management or market-regime effects rather than the exact EA entry rule.
- If the differentiators are weak or inconsistent, run the expanded indicator/parameter discovery fallback for this `Sxx`.

## T3/S06

- Initial entries / baskets: `99` / `99`.
- Direction mix: short:1.00.
- Broker-session mix: off_session:1.00.
- PnL estimate: `-14994461.54`.
- Avg holding minutes: `672.60`; avg add-ons/basket: `3.06`.
- Avg M1 MAE/MFE points: `3.37` / `1.24`.
- Candidate family: **oversold pullback / downtrend continuation context**.
- Confidence: `low`.
- Evidence: low RSI, negative M15 momentum.

### Entry-context differentiators

| Feature | Strategy median | Rest median | Delta | Effect | IQR band |
|---|---:|---:|---:|---:|---|
| `m15_dmn_14` | 32.058 | 11.700 | 20.358 | 2.58 | [29.419, 35.820] |
| `m15_rsi_14` | 31.947 | 65.511 | -33.564 | 2.09 | [27.481, 37.352] |
| `m15_dmp_14` | 10.394 | 29.334 | -18.940 | 1.68 | [7.410, 11.992] |
| `m15_close_distance_to_ema_50` | -7.659 | 6.850 | -14.510 | 1.53 | [-14.421, -5.552] |
| `m15_macd_12_26_9` | -2.764 | 2.342 | -5.106 | 1.51 | [-5.229, -1.745] |
| `m15_ema_50_slope_4` | -1.279 | 1.108 | -2.387 | 1.49 | [-2.527, -0.841] |
| `m15_ema_21_slope_4` | -1.320 | 1.570 | -2.889 | 1.45 | [-2.808, -0.891] |
| `m15_close_distance_to_ema_21` | -3.508 | 3.707 | -7.216 | 1.41 | [-6.044, -2.057] |

### Management differentiators

| Feature | Strategy median | Rest median | Delta | Effect | IQR band |
|---|---:|---:|---:|---:|---|
| `add_on_spacing_price_abs_mean` | 3.020 | 0.520 | 2.500 | 1.48 | [0.000, 3.175] |
| `add_on_spacing_minutes_mean` | 67.333 | 5.000 | 62.333 | 1.42 | [0.004, 170.600] |
| `add_on_count` | 0.000 | 1.000 | -1.000 | 0.33 | [0.000, 1.000] |
| `max_layers` | 1.000 | 2.000 | -1.000 | 0.33 | [1.000, 2.000] |
| `position_count` | 1.000 | 2.000 | -1.000 | 0.33 | [1.000, 2.000] |
| `holding_minutes` | 75.000 | 29.000 | 46.000 | 0.22 | [8.000, 430.517] |
| `m1_time_to_mfe_minutes` | 16.000 | 10.000 | 6.000 | 0.14 | [2.000, 140.500] |
| `m1_mfe_atr_14` | 0.437 | 0.391 | 0.046 | 0.10 | [0.251, 0.717] |

### Uncertainty

- This profile is descriptive and approximate. It may reflect shared basket management or market-regime effects rather than the exact EA entry rule.
- If the differentiators are weak or inconsistent, run the expanded indicator/parameter discovery fallback for this `Sxx`.

## T4/S08

- Initial entries / baskets: `58` / `58`.
- Direction mix: long:1.00.
- Broker-session mix: london:0.84, asia:0.16.
- PnL estimate: `1014496.77`.
- Avg holding minutes: `110.51`; avg add-ons/basket: `2.98`.
- Avg M1 MAE/MFE points: `3.68` / `1.78`.
- Candidate family: **trend breakout / momentum continuation**.
- Confidence: `medium`.
- Evidence: positive M15 momentum, above recent-high breakout, close above EMA21, ADX trend strength.

### Entry-context differentiators

| Feature | Strategy median | Rest median | Delta | Effect | IQR band |
|---|---:|---:|---:|---:|---|
| `broker_entry_hour` | 9.000 | 22.000 | -13.000 | 4.33 | [8.000, 10.000] |
| `m15_range_points` | 4.400 | 1.720 | 2.680 | 1.60 | [2.198, 5.840] |
| `m15_close_distance_to_ema_50` | 16.953 | 6.080 | 10.873 | 1.15 | [9.232, 20.151] |
| `m15_close_distance_to_ema_8` | 3.586 | 0.926 | 2.659 | 1.14 | [1.224, 5.908] |
| `broker_entry_minute_mod_15` | 5.000 | 0.000 | 5.000 | 1.00 | [0.000, 5.000] |
| `m15_momentum_4_close_points` | 4.425 | 0.860 | 3.565 | 1.00 | [0.778, 8.940] |
| `m15_ema_50_slope_4` | 2.447 | 1.013 | 1.434 | 0.89 | [1.520, 3.055] |
| `m15_range_atr_14_ratio` | 1.209 | 0.769 | 0.440 | 0.83 | [0.920, 1.815] |

### Management differentiators

| Feature | Strategy median | Rest median | Delta | Effect | IQR band |
|---|---:|---:|---:|---:|---|
| `m1_mfe_points` | 1.760 | 0.900 | 0.860 | 0.88 | [0.948, 2.265] |
| `add_on_spacing_price_abs_mean` | 1.618 | 0.520 | 1.097 | 0.65 | [0.272, 1.985] |
| `m1_mae_points` | 2.400 | 1.280 | 1.120 | 0.44 | [0.732, 4.717] |
| `add_on_count` | 2.000 | 1.000 | 1.000 | 0.33 | [0.000, 4.000] |
| `max_layers` | 3.000 | 2.000 | 1.000 | 0.33 | [1.000, 5.000] |
| `position_count` | 3.000 | 2.000 | 1.000 | 0.33 | [1.000, 5.000] |
| `m1_mfe_atr_14` | 0.518 | 0.391 | 0.127 | 0.27 | [0.353, 0.847] |
| `m1_mae_atr_14` | 0.798 | 0.551 | 0.247 | 0.19 | [0.191, 1.317] |

### Uncertainty

- This profile is descriptive and approximate. It may reflect shared basket management or market-regime effects rather than the exact EA entry rule.
- If the differentiators are weak or inconsistent, run the expanded indicator/parameter discovery fallback for this `Sxx`.

## T5/S09

- Initial entries / baskets: `71` / `71`.
- Direction mix: long:1.00.
- Broker-session mix: london:0.62, london_newyork_overlap:0.38.
- PnL estimate: `1520356.22`.
- Avg holding minutes: `435.89`; avg add-ons/basket: `2.30`.
- Avg M1 MAE/MFE points: `5.41` / `2.69`.
- Candidate family: **trend breakout / momentum continuation**.
- Confidence: `medium`.
- Evidence: positive M15 momentum, above recent-high breakout, close above EMA21, ADX trend strength.

### Entry-context differentiators

| Feature | Strategy median | Rest median | Delta | Effect | IQR band |
|---|---:|---:|---:|---:|---|
| `broker_entry_hour` | 11.000 | 22.000 | -11.000 | 3.67 | [10.000, 12.000] |
| `broker_entry_minute_mod_15` | 6.000 | 0.000 | 6.000 | 1.20 | [3.000, 9.000] |
| `m15_range_atr_14_ratio` | 1.333 | 0.762 | 0.570 | 1.08 | [0.977, 1.671] |
| `m15_dmp_14` | 37.486 | 28.428 | 9.058 | 0.80 | [32.982, 41.843] |
| `m15_momentum_4_close_points` | 3.570 | 0.840 | 2.730 | 0.76 | [1.510, 5.460] |
| `m15_macd_hist_12_26_9` | 0.806 | 0.181 | 0.625 | 0.72 | [0.465, 1.264] |
| `m15_ema_8_slope_4` | 3.077 | 1.329 | 1.748 | 0.68 | [2.133, 4.219] |
| `m15_dmn_14` | 7.112 | 12.240 | -5.128 | 0.65 | [5.175, 11.003] |

### Management differentiators

| Feature | Strategy median | Rest median | Delta | Effect | IQR band |
|---|---:|---:|---:|---:|---|
| `m1_mfe_atr_14` | 1.292 | 0.388 | 0.904 | 1.90 | [0.458, 2.093] |
| `m1_mfe_points` | 2.440 | 0.890 | 1.550 | 1.58 | [1.525, 3.050] |
| `m1_mae_atr_14` | 1.664 | 0.537 | 1.127 | 0.88 | [0.442, 3.594] |
| `add_on_spacing_price_abs_mean` | 1.917 | 0.520 | 1.397 | 0.83 | [0.000, 5.377] |
| `m1_mae_points` | 2.650 | 1.260 | 1.390 | 0.54 | [0.985, 7.350] |
| `holding_minutes` | 118.000 | 28.508 | 89.492 | 0.43 | [17.500, 283.533] |
| `add_on_count` | 0.000 | 1.000 | -1.000 | 0.33 | [0.000, 3.000] |
| `max_layers` | 1.000 | 2.000 | -1.000 | 0.33 | [1.000, 4.000] |

### Uncertainty

- This profile is descriptive and approximate. It may reflect shared basket management or market-regime effects rather than the exact EA entry rule.
- If the differentiators are weak or inconsistent, run the expanded indicator/parameter discovery fallback for this `Sxx`.

## T5/S10

- Initial entries / baskets: `108` / `108`.
- Direction mix: long:1.00.
- Broker-session mix: off_session:0.88, asia:0.08, london:0.04.
- PnL estimate: `2101890.16`.
- Avg holding minutes: `732.33`; avg add-ons/basket: `2.57`.
- Avg M1 MAE/MFE points: `3.26` / `1.86`.
- Candidate family: **overbought momentum / trend continuation context**.
- Confidence: `low`.
- Evidence: high RSI, positive M15 momentum.

### Entry-context differentiators

| Feature | Strategy median | Rest median | Delta | Effect | IQR band |
|---|---:|---:|---:|---:|---|
| `m15_adx_14` | 29.653 | 37.439 | -7.786 | 0.41 | [22.294, 39.303] |
| `m15_momentum_32_close_points` | 4.605 | 10.340 | -5.735 | 0.31 | [0.555, 16.550] |
| `broker_entry_minute_mod_15` | 1.500 | 0.000 | 1.500 | 0.30 | [0.000, 5.000] |
| `m15_macd_hist_12_26_9` | 0.407 | 0.188 | 0.219 | 0.25 | [0.125, 0.909] |
| `m15_macd_12_26_9` | 1.390 | 2.227 | -0.837 | 0.25 | [0.433, 3.088] |
| `m15_ema_50_slope_4` | 0.716 | 1.059 | -0.343 | 0.21 | [0.206, 1.405] |
| `m15_momentum_8_close_points` | 3.680 | 2.540 | 1.140 | 0.20 | [1.490, 7.273] |
| `m15_close_distance_to_ema_50` | 4.615 | 6.394 | -1.779 | 0.19 | [1.830, 9.263] |

### Management differentiators

| Feature | Strategy median | Rest median | Delta | Effect | IQR band |
|---|---:|---:|---:|---:|---|
| `holding_minutes` | 227.008 | 27.050 | 199.958 | 0.97 | [26.762, 647.263] |
| `m1_mfe_points` | 1.590 | 0.890 | 0.700 | 0.71 | [0.870, 2.410] |
| `m1_mfe_atr_14` | 0.717 | 0.383 | 0.334 | 0.70 | [0.387, 1.332] |
| `m1_time_to_mfe_minutes` | 35.000 | 10.000 | 25.000 | 0.58 | [6.750, 278.000] |
| `add_on_count` | 0.000 | 1.000 | -1.000 | 0.33 | [0.000, 3.000] |
| `max_layers` | 1.000 | 2.000 | -1.000 | 0.33 | [1.000, 4.000] |
| `position_count` | 1.000 | 2.000 | -1.000 | 0.33 | [1.000, 4.000] |
| `m1_mae_points` | 2.060 | 1.250 | 0.810 | 0.32 | [0.693, 4.010] |

### Uncertainty

- This profile is descriptive and approximate. It may reflect shared basket management or market-regime effects rather than the exact EA entry rule.
- If the differentiators are weak or inconsistent, run the expanded indicator/parameter discovery fallback for this `Sxx`.

## T6/S12

- Initial entries / baskets: `166` / `166`.
- Direction mix: short:1.00.
- Broker-session mix: london:1.00.
- PnL estimate: `2057978.15`.
- Avg holding minutes: `187.85`; avg add-ons/basket: `2.94`.
- Avg M1 MAE/MFE points: `3.26` / `1.74`.
- Candidate family: **downtrend breakout / short momentum continuation**.
- Confidence: `medium`.
- Evidence: negative M15 momentum, below recent-low breakout, close below EMA21, ADX trend strength.

### Entry-context differentiators

| Feature | Strategy median | Rest median | Delta | Effect | IQR band |
|---|---:|---:|---:|---:|---|
| `broker_entry_hour` | 8.000 | 22.000 | -14.000 | 4.67 | [8.000, 9.000] |
| `m15_dmn_14` | 34.552 | 11.479 | 23.073 | 2.92 | [30.842, 38.981] |
| `m15_rsi_14` | 30.685 | 66.174 | -35.488 | 2.21 | [26.237, 35.108] |
| `m15_dmp_14` | 9.759 | 29.725 | -19.966 | 1.77 | [8.073, 11.696] |
| `m15_breakout_above_recent_high_8_points` | -3.910 | -0.320 | -3.590 | 1.55 | [-6.583, -2.670] |
| `m15_close_distance_to_ema_21` | -3.316 | 3.843 | -7.160 | 1.40 | [-5.035, -2.144] |
| `m15_ema_21_slope_4` | -1.158 | 1.629 | -2.787 | 1.40 | [-1.944, -0.777] |
| `m15_ema_8_slope_4` | -1.979 | 1.603 | -3.581 | 1.39 | [-3.225, -1.244] |

### Management differentiators

| Feature | Strategy median | Rest median | Delta | Effect | IQR band |
|---|---:|---:|---:|---:|---|
| `m1_mfe_atr_14` | 0.827 | 0.377 | 0.451 | 0.95 | [0.405, 1.422] |
| `m1_mfe_points` | 1.450 | 0.880 | 0.570 | 0.58 | [0.723, 1.865] |
| `m1_mae_atr_14` | 1.021 | 0.517 | 0.504 | 0.39 | [0.366, 2.578] |
| `m1_mae_points` | 1.860 | 1.250 | 0.610 | 0.24 | [0.633, 3.770] |
| `m1_time_to_mfe_minutes` | 18.500 | 9.000 | 9.500 | 0.22 | [6.000, 52.500] |
| `add_on_spacing_price_abs_mean` | 0.823 | 0.513 | 0.310 | 0.18 | [0.000, 2.252] |
| `m1_time_to_mae_minutes` | 19.000 | 7.000 | 12.000 | 0.14 | [3.000, 60.250] |
| `holding_minutes` | 45.008 | 28.000 | 17.008 | 0.08 | [15.263, 123.263] |

### Uncertainty

- This profile is descriptive and approximate. It may reflect shared basket management or market-regime effects rather than the exact EA entry rule.
- If the differentiators are weak or inconsistent, run the expanded indicator/parameter discovery fallback for this `Sxx`.

