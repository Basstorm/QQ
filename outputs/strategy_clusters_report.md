# Phase 3 Strategy Candidate Discovery Report

## Executive Summary

- Active explicit strategies: `8` — T1/S01, T2/S03, T2/S04, T3/S06, T4/S08, T5/S09, T5/S10, T6/S12.
- Basket rows clustered: `1657`.
- Feature columns used for clustering: `94`.
- Natural KMeans candidate selected by silhouette: `k=3`.
- Forced 12-cluster view generated: `True`.
- Best-cluster adjusted Rand index vs explicit `T/S` strategy tags: `0.1690`.
- Best-cluster normalized mutual information vs explicit `T/S` strategy tags: `0.3213`.

## Interpretation

- Explicit `T/S` tags remain the strongest strategy identifiers; clustering is used as a behavioral cross-check, not as proof of hidden exact EA rules.
- The forced 12-cluster view is diagnostic only. This backtest contains 8 active explicit strategy IDs, so 12 clusters should not be interpreted as evidence that all marketed strategies traded.
- Basket-level clustering mixes entry context and management behavior. Use Phase 4 rule inference to separate initial-entry hypotheses from grid/add-on and close management.

## KMeans Diagnostics

- Silhouette scores use Manhattan distance on median-imputed, clipped, standardized features to avoid sklearn Euclidean pairwise-distance warnings on this environment.

| k | silhouette | min size | max size |
|---:|---:|---:|---:|
| 2 | 0.2177 | 473 | 1184 |
| 3 | 0.2564 | 277 | 1083 |
| 4 | 0.2260 | 156 | 977 |
| 5 | 0.1523 | 148 | 717 |
| 6 | 0.1580 | 46 | 696 |
| 7 | 0.1344 | 45 | 599 |
| 8 | 0.1575 | 41 | 671 |
| 9 | 0.1360 | 45 | 601 |
| 10 | 0.1157 | 51 | 472 |
| 11 | 0.1486 | 41 | 608 |
| 12 | 0.1102 | 49 | 456 |

## Best-Cluster Strategy Overlap

| Cluster | Rows | Dominant strategy | Dominant share | Strategy mix |
|---:|---:|---|---:|---|
| 0 | 1083 | T1/S01 | 0.340 | T1/S01:368, T2/S04:298, T2/S03:276, T5/S10:75, T5/S09:44, T4/S08:19, T3/S06:3 |
| 1 | 277 | T6/S12 | 0.599 | T6/S12:166, T3/S06:96, T5/S10:13, T4/S08:2 |
| 2 | 297 | T1/S01 | 0.306 | T1/S01:91, T2/S04:80, T2/S03:42, T4/S08:37, T5/S09:27, T5/S10:20 |

## Feature Columns Used

`position_count`, `total_volume`, `holding_seconds`, `max_layers`, `add_on_count`, `initial_volume`, `add_on_spacing_minutes_mean`, `add_on_spacing_minutes_min`, `add_on_spacing_minutes_max`, `add_on_spacing_price_abs_mean`, `add_on_spacing_price_abs_min`, `add_on_spacing_price_abs_max`, `max_volume_multiplier_vs_initial`, `close_span_minutes`, `closed_together_within_1m`, `broker_entry_hour`, `broker_entry_weekday`, `broker_entry_month`, `broker_entry_minute_mod_15`, `broker_entry_second`, `broker_entry_is_friday`, `utc_entry_hour_est`, `utc_entry_weekday_est`, `utc_entry_month_est`, `utc_entry_in_asia_est`, `utc_entry_in_london_est`, `utc_entry_in_newyork_est`, `m15_tick_volume`, `m15_spread`, `m15_real_volume`, `m15_body_points`, `m15_body_abs_points`, `m15_range_points`, `m15_upper_wick_points`, `m15_lower_wick_points`, `m15_body_to_range`, `m15_momentum_1_close_points`, `m15_breakout_above_recent_high_1_points`, `m15_breakout_below_recent_low_1_points`, `m15_momentum_2_close_points`, `m15_breakout_above_recent_high_2_points`, `m15_breakout_below_recent_low_2_points`, `m15_momentum_4_close_points`, `m15_breakout_above_recent_high_4_points`, `m15_breakout_below_recent_low_4_points`, `m15_momentum_8_close_points`, `m15_breakout_above_recent_high_8_points`, `m15_breakout_below_recent_low_8_points`, `m15_momentum_16_close_points`, `m15_breakout_above_recent_high_16_points`, `m15_breakout_below_recent_low_16_points`, `m15_momentum_32_close_points`, `m15_breakout_above_recent_high_32_points`, `m15_breakout_below_recent_low_32_points`, `m15_atr_14`, `m15_range_atr_14_ratio`, `m15_atr_14_percentile_252`, `m15_ema_8_slope_4`, `m15_close_distance_to_ema_8`, `m15_ema_21_slope_4`, `m15_close_distance_to_ema_21`, `m15_ema_50_slope_4`, `m15_close_distance_to_ema_50`, `m15_rsi_14`, `m15_adx_14`, `m15_dmp_14`, `m15_dmn_14`, `m15_macd_12_26_9`, `m15_macd_hist_12_26_9`, `m15_macd_signal_12_26_9`, `entry_price_position_in_m15_range`, `entry_price_distance_to_m15_ema_8`, `entry_price_distance_to_m15_ema_21`, `entry_price_distance_to_m15_ema_50`, `m15_momentum_1_directional_points`, `m15_momentum_2_directional_points`, `m15_momentum_4_directional_points`, `m15_momentum_8_directional_points`, `m15_momentum_16_directional_points`, `m15_momentum_32_directional_points`, `m1_path_bar_count`, `m1_mfe_points`, `m1_mae_points`, `m1_net_exit_move_points`, `m1_time_to_mfe_minutes`, `m1_time_to_mae_minutes`, `m1_spread_mean`, `m1_spread_max`, `m1_tick_volume_sum`, `m1_tick_volume_mean`, `holding_minutes`, `m1_mfe_atr_14`, `m1_mae_atr_14`, `direction_sign`

## Best-Cluster Shifted Feature Summary

| Cluster | Rows | Top shifted median features |
|---:|---:|---|
| 0 | 1083 | holding_seconds=2581.000, m1_tick_volume_sum=2349.000, m15_tick_volume=1063.000, m1_tick_volume_mean=60.778, holding_minutes=43.017, m1_path_bar_count=39.000, add_on_spacing_minutes_max=20.500, m1_time_to_mae_minutes=13.000 |
| 1 | 277 | holding_seconds=3540.000, m1_tick_volume_sum=3201.000, m15_tick_volume=961.000, m15_rsi_14=31.483, holding_minutes=59.000, m1_path_bar_count=53.000, add_on_spacing_minutes_max=38.983, m15_dmn_14=33.238 |
| 2 | 297 | holding_seconds=300.000, m15_tick_volume=2427.000, m1_tick_volume_sum=1151.000, m1_tick_volume_mean=152.500, holding_minutes=5.000, m1_path_bar_count=6.000, total_volume=33.380, m15_momentum_32_close_points=25.120 |
