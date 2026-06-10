# Phase 2 Feature Dictionary

## Table Semantics

- `deal_features.parquet`: reconstructed position / entry-deal level. One row is one FIFO-matched entry-to-exit position fragment, preserving `entry_deal`, `exit_deal`, `strategy`, `T`, `S`, `broker_*`, and estimated UTC session fields.
- `basket_features.parquet`: reconstructed analytical basket/cycle level. One row is one interval-based basket from Phase 1, augmented with initial-entry, add-on, close-span, M15 context, and M1 path features.

## Indicator Implementation

- M15 technical indicators use `pandas-ta-classic`, the installable pandas-ta compatible package available in this environment.
- `m15_rsi_14`, `m15_adx_14`, `m15_dmp_14`, `m15_dmn_14`, `m15_macd_12_26_9`, `m15_macd_hist_12_26_9`, `m15_macd_signal_12_26_9`, `m15_atr_14`, and `m15_ema_*` are generated through pandas-ta-classic with short-sample fallbacks where needed.

## `deal_features.parquet` Columns

| Column | Description |
|---|---|
| `position_id` | Identifier preserved from reconstructed trades or MT5 report records. |
| `strategy` | Strategy identity and direction metadata preserved from Phase 1 reconstruction. |
| `T` | Strategy identity and direction metadata preserved from Phase 1 reconstruction. |
| `S` | Strategy identity and direction metadata preserved from Phase 1 reconstruction. |
| `tag_symbol` | Strategy identity and direction metadata preserved from Phase 1 reconstruction. |
| `magic` | Strategy identity and direction metadata preserved from Phase 1 reconstruction. |
| `symbol` | Strategy identity and direction metadata preserved from Phase 1 reconstruction. |
| `direction` | Strategy identity and direction metadata preserved from Phase 1 reconstruction. |
| `volume` | Lot size or tick/real-volume feature. |
| `entry_time` | Timestamp or duration feature. |
| `exit_time` | Timestamp or duration feature. |
| `entry_minute` | Feature preserved or derived during Phase 2 feature engineering. |
| `exit_minute` | Feature preserved or derived during Phase 2 feature engineering. |
| `utc_entry_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `utc_exit_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `entry_price` | Price level or price-difference feature. |
| `exit_price` | Price level or price-difference feature. |
| `entry_deal` | Identifier preserved from reconstructed trades or MT5 report records. |
| `exit_deal` | Identifier preserved from reconstructed trades or MT5 report records. |
| `entry_order` | Identifier preserved from reconstructed trades or MT5 report records. |
| `exit_order` | Identifier preserved from reconstructed trades or MT5 report records. |
| `entry_comment` | Feature preserved or derived during Phase 2 feature engineering. |
| `exit_comment` | Feature preserved or derived during Phase 2 feature engineering. |
| `exit_profit_reported` | PnL/profit field from Phase 1 reconstruction or MT5 exit report. |
| `pnl_est` | PnL/profit field from Phase 1 reconstruction or MT5 exit report. |
| `holding_seconds` | Timestamp or duration feature. |
| `basket_id` | Identifier preserved from reconstructed trades or MT5 report records. |
| `entry_sequence_in_basket` | Basket/order-structure feature distinguishing initial signal entries from add-ons. |
| `basket_first_entry_time` | Timestamp or duration feature. |
| `initial_entry_price` | Basket structure and close-coordination feature. |
| `initial_volume` | Basket structure and close-coordination feature. |
| `is_initial_entry` | Basket/order-structure feature distinguishing initial signal entries from add-ons. |
| `minutes_from_basket_first_entry` | Timestamp or duration feature. |
| `entry_price_delta_from_initial` | Price level or price-difference feature. |
| `entry_price_abs_delta_from_initial` | Price level or price-difference feature. |
| `volume_multiplier_vs_initial` | Lot size or tick/real-volume feature. |
| `broker_entry_time` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `utc_entry_time_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `broker_entry_hour` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `broker_entry_weekday` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `broker_entry_month` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `broker_entry_minute_mod_15` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `broker_entry_second` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `broker_entry_is_friday` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `broker_entry_session` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `utc_entry_hour_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `utc_entry_weekday_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `utc_entry_month_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `utc_entry_session_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `utc_entry_in_asia_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `utc_entry_in_london_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `utc_entry_in_newyork_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `utc_entry_in_london_newyork_overlap_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `broker_exit_time` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `utc_exit_time_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `broker_exit_hour` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `broker_exit_weekday` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `broker_exit_month` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `broker_exit_minute_mod_15` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `broker_exit_second` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `broker_exit_is_friday` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `broker_exit_session` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `utc_exit_hour_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `utc_exit_weekday_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `utc_exit_month_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `utc_exit_session_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `utc_exit_in_asia_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `utc_exit_in_london_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `utc_exit_in_newyork_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `utc_exit_in_london_newyork_overlap_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `entry_m15_time` | Timestamp or duration feature. |
| `m15_open` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_high` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_low` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_close` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_tick_volume` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_spread` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_real_volume` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_body_points` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_body_abs_points` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_range_points` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_upper_wick_points` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_lower_wick_points` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_body_to_range` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_momentum_1_close_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_recent_high_1` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_recent_low_1` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_breakout_above_recent_high_1_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_breakout_below_recent_low_1_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_momentum_2_close_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_recent_high_2` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_recent_low_2` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_breakout_above_recent_high_2_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_breakout_below_recent_low_2_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_momentum_4_close_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_recent_high_4` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_recent_low_4` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_breakout_above_recent_high_4_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_breakout_below_recent_low_4_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_momentum_8_close_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_recent_high_8` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_recent_low_8` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_breakout_above_recent_high_8_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_breakout_below_recent_low_8_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_momentum_16_close_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_recent_high_16` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_recent_low_16` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_breakout_above_recent_high_16_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_breakout_below_recent_low_16_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_momentum_32_close_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_recent_high_32` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_recent_low_32` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_breakout_above_recent_high_32_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_breakout_below_recent_low_32_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_atr_14` | M15 ATR volatility context generated with pandas-ta-classic and used for ATR-normalized path features. |
| `m15_range_atr_14_ratio` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_atr_14_percentile_252` | M15 ATR volatility context generated with pandas-ta-classic and used for ATR-normalized path features. |
| `m15_ema_8` | M15 EMA trend context generated with pandas-ta-classic and derived distance/slope features. |
| `m15_ema_8_slope_4` | M15 EMA trend context generated with pandas-ta-classic and derived distance/slope features. |
| `m15_close_distance_to_ema_8` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_ema_21` | M15 EMA trend context generated with pandas-ta-classic and derived distance/slope features. |
| `m15_ema_21_slope_4` | M15 EMA trend context generated with pandas-ta-classic and derived distance/slope features. |
| `m15_close_distance_to_ema_21` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_ema_50` | M15 EMA trend context generated with pandas-ta-classic and derived distance/slope features. |
| `m15_ema_50_slope_4` | M15 EMA trend context generated with pandas-ta-classic and derived distance/slope features. |
| `m15_close_distance_to_ema_50` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_rsi_14` | M15 technical indicator generated with pandas-ta-classic. |
| `m15_adx_14` | M15 technical indicator generated with pandas-ta-classic. |
| `m15_dmp_14` | M15 technical indicator generated with pandas-ta-classic. |
| `m15_dmn_14` | M15 technical indicator generated with pandas-ta-classic. |
| `m15_macd_12_26_9` | M15 technical indicator generated with pandas-ta-classic. |
| `m15_macd_hist_12_26_9` | M15 technical indicator generated with pandas-ta-classic. |
| `m15_macd_signal_12_26_9` | M15 technical indicator generated with pandas-ta-classic. |
| `entry_price_position_in_m15_range` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `entry_price_distance_to_m15_ema_8` | M15 EMA trend context generated with pandas-ta-classic and derived distance/slope features. |
| `entry_price_distance_to_m15_ema_21` | M15 EMA trend context generated with pandas-ta-classic and derived distance/slope features. |
| `entry_price_distance_to_m15_ema_50` | M15 EMA trend context generated with pandas-ta-classic and derived distance/slope features. |
| `m15_momentum_1_directional_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_momentum_2_directional_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_momentum_4_directional_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_momentum_8_directional_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_momentum_16_directional_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_momentum_32_directional_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m1_path_bar_count` | M1 post-entry management path feature covering MAE/MFE, path availability, spread, volume, or timing. |
| `m1_path_available` | M1 post-entry management path feature covering MAE/MFE, path availability, spread, volume, or timing. |
| `m1_path_high_max` | M1 post-entry management path feature covering MAE/MFE, path availability, spread, volume, or timing. |
| `m1_path_low_min` | M1 post-entry management path feature covering MAE/MFE, path availability, spread, volume, or timing. |
| `m1_path_close_last` | M1 post-entry management path feature covering MAE/MFE, path availability, spread, volume, or timing. |
| `m1_mfe_points` | M1 post-entry management path feature covering MAE/MFE, path availability, spread, volume, or timing. |
| `m1_mae_points` | M1 post-entry management path feature covering MAE/MFE, path availability, spread, volume, or timing. |
| `m1_net_exit_move_points` | M1 post-entry management path feature covering MAE/MFE, path availability, spread, volume, or timing. |
| `m1_time_to_mfe_minutes` | M1 post-entry management path feature covering MAE/MFE, path availability, spread, volume, or timing. |
| `m1_time_to_mae_minutes` | M1 post-entry management path feature covering MAE/MFE, path availability, spread, volume, or timing. |
| `m1_spread_mean` | M1 post-entry management path feature covering MAE/MFE, path availability, spread, volume, or timing. |
| `m1_spread_max` | M1 post-entry management path feature covering MAE/MFE, path availability, spread, volume, or timing. |
| `m1_tick_volume_sum` | M1 post-entry management path feature covering MAE/MFE, path availability, spread, volume, or timing. |
| `m1_tick_volume_mean` | M1 post-entry management path feature covering MAE/MFE, path availability, spread, volume, or timing. |
| `holding_minutes` | Timestamp or duration feature. |
| `m1_mfe_atr_14` | M15 ATR volatility context generated with pandas-ta-classic and used for ATR-normalized path features. |
| `m1_mae_atr_14` | M15 ATR volatility context generated with pandas-ta-classic and used for ATR-normalized path features. |

## `basket_features.parquet` Columns

| Column | Description |
|---|---|
| `basket_id` | Identifier preserved from reconstructed trades or MT5 report records. |
| `strategy` | Strategy identity and direction metadata preserved from Phase 1 reconstruction. |
| `T` | Strategy identity and direction metadata preserved from Phase 1 reconstruction. |
| `S` | Strategy identity and direction metadata preserved from Phase 1 reconstruction. |
| `direction` | Strategy identity and direction metadata preserved from Phase 1 reconstruction. |
| `position_count` | Feature preserved or derived during Phase 2 feature engineering. |
| `total_volume` | Lot size or tick/real-volume feature. |
| `pnl_est` | PnL/profit field from Phase 1 reconstruction or MT5 exit report. |
| `first_entry_time` | Timestamp or duration feature. |
| `last_entry_time` | Timestamp or duration feature. |
| `first_exit_time` | Timestamp or duration feature. |
| `last_exit_time` | Timestamp or duration feature. |
| `holding_seconds` | Timestamp or duration feature. |
| `max_layers` | Feature preserved or derived during Phase 2 feature engineering. |
| `add_on_count` | Basket/order-structure feature distinguishing initial signal entries from add-ons. |
| `initial_position_id` | Basket structure and close-coordination feature. |
| `initial_entry_time` | Basket structure and close-coordination feature. |
| `initial_entry_price` | Basket structure and close-coordination feature. |
| `initial_volume` | Basket structure and close-coordination feature. |
| `final_exit_time` | Basket structure and close-coordination feature. |
| `final_exit_price` | Basket structure and close-coordination feature. |
| `add_on_spacing_minutes_mean` | Basket/order-structure feature distinguishing initial signal entries from add-ons. |
| `add_on_spacing_minutes_min` | Basket/order-structure feature distinguishing initial signal entries from add-ons. |
| `add_on_spacing_minutes_max` | Basket/order-structure feature distinguishing initial signal entries from add-ons. |
| `add_on_spacing_price_abs_mean` | Basket/order-structure feature distinguishing initial signal entries from add-ons. |
| `add_on_spacing_price_abs_min` | Basket/order-structure feature distinguishing initial signal entries from add-ons. |
| `add_on_spacing_price_abs_max` | Basket/order-structure feature distinguishing initial signal entries from add-ons. |
| `max_volume_multiplier_vs_initial` | Lot size or tick/real-volume feature. |
| `close_span_minutes` | Basket structure and close-coordination feature. |
| `closed_together_within_1m` | Basket structure and close-coordination feature. |
| `broker_entry_time` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `utc_entry_time_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `broker_entry_hour` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `broker_entry_weekday` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `broker_entry_month` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `broker_entry_minute_mod_15` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `broker_entry_second` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `broker_entry_is_friday` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `broker_entry_session` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `utc_entry_hour_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `utc_entry_weekday_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `utc_entry_month_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `utc_entry_session_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `utc_entry_in_asia_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `utc_entry_in_london_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `utc_entry_in_newyork_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `utc_entry_in_london_newyork_overlap_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `broker_exit_time` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `utc_exit_time_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `broker_exit_hour` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `broker_exit_weekday` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `broker_exit_month` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `broker_exit_minute_mod_15` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `broker_exit_second` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `broker_exit_is_friday` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `broker_exit_session` | Broker/server-clock time feature used for candle joins and raw timing diagnostics. |
| `utc_exit_hour_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `utc_exit_weekday_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `utc_exit_month_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `utc_exit_session_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `utc_exit_in_asia_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `utc_exit_in_london_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `utc_exit_in_newyork_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `utc_exit_in_london_newyork_overlap_est` | Estimated UTC feature derived as broker time minus 3 hours for session analysis. |
| `entry_m15_time` | Timestamp or duration feature. |
| `m15_open` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_high` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_low` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_close` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_tick_volume` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_spread` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_real_volume` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_body_points` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_body_abs_points` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_range_points` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_upper_wick_points` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_lower_wick_points` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_body_to_range` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_momentum_1_close_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_recent_high_1` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_recent_low_1` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_breakout_above_recent_high_1_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_breakout_below_recent_low_1_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_momentum_2_close_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_recent_high_2` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_recent_low_2` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_breakout_above_recent_high_2_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_breakout_below_recent_low_2_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_momentum_4_close_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_recent_high_4` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_recent_low_4` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_breakout_above_recent_high_4_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_breakout_below_recent_low_4_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_momentum_8_close_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_recent_high_8` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_recent_low_8` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_breakout_above_recent_high_8_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_breakout_below_recent_low_8_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_momentum_16_close_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_recent_high_16` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_recent_low_16` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_breakout_above_recent_high_16_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_breakout_below_recent_low_16_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_momentum_32_close_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_recent_high_32` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_recent_low_32` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_breakout_above_recent_high_32_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_breakout_below_recent_low_32_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_atr_14` | M15 ATR volatility context generated with pandas-ta-classic and used for ATR-normalized path features. |
| `m15_range_atr_14_ratio` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_atr_14_percentile_252` | M15 ATR volatility context generated with pandas-ta-classic and used for ATR-normalized path features. |
| `m15_ema_8` | M15 EMA trend context generated with pandas-ta-classic and derived distance/slope features. |
| `m15_ema_8_slope_4` | M15 EMA trend context generated with pandas-ta-classic and derived distance/slope features. |
| `m15_close_distance_to_ema_8` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_ema_21` | M15 EMA trend context generated with pandas-ta-classic and derived distance/slope features. |
| `m15_ema_21_slope_4` | M15 EMA trend context generated with pandas-ta-classic and derived distance/slope features. |
| `m15_close_distance_to_ema_21` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_ema_50` | M15 EMA trend context generated with pandas-ta-classic and derived distance/slope features. |
| `m15_ema_50_slope_4` | M15 EMA trend context generated with pandas-ta-classic and derived distance/slope features. |
| `m15_close_distance_to_ema_50` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `m15_rsi_14` | M15 technical indicator generated with pandas-ta-classic. |
| `m15_adx_14` | M15 technical indicator generated with pandas-ta-classic. |
| `m15_dmp_14` | M15 technical indicator generated with pandas-ta-classic. |
| `m15_dmn_14` | M15 technical indicator generated with pandas-ta-classic. |
| `m15_macd_12_26_9` | M15 technical indicator generated with pandas-ta-classic. |
| `m15_macd_hist_12_26_9` | M15 technical indicator generated with pandas-ta-classic. |
| `m15_macd_signal_12_26_9` | M15 technical indicator generated with pandas-ta-classic. |
| `entry_price_position_in_m15_range` | M15 entry-bar candle context, shape, spread, volume, or price-location feature. |
| `entry_price_distance_to_m15_ema_8` | M15 EMA trend context generated with pandas-ta-classic and derived distance/slope features. |
| `entry_price_distance_to_m15_ema_21` | M15 EMA trend context generated with pandas-ta-classic and derived distance/slope features. |
| `entry_price_distance_to_m15_ema_50` | M15 EMA trend context generated with pandas-ta-classic and derived distance/slope features. |
| `m15_momentum_1_directional_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_momentum_2_directional_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_momentum_4_directional_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_momentum_8_directional_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_momentum_16_directional_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m15_momentum_32_directional_points` | M15 lookback momentum, recent high/low, and breakout relation feature. |
| `m1_path_bar_count` | M1 post-entry management path feature covering MAE/MFE, path availability, spread, volume, or timing. |
| `m1_path_available` | M1 post-entry management path feature covering MAE/MFE, path availability, spread, volume, or timing. |
| `m1_path_high_max` | M1 post-entry management path feature covering MAE/MFE, path availability, spread, volume, or timing. |
| `m1_path_low_min` | M1 post-entry management path feature covering MAE/MFE, path availability, spread, volume, or timing. |
| `m1_path_close_last` | M1 post-entry management path feature covering MAE/MFE, path availability, spread, volume, or timing. |
| `m1_mfe_points` | M1 post-entry management path feature covering MAE/MFE, path availability, spread, volume, or timing. |
| `m1_mae_points` | M1 post-entry management path feature covering MAE/MFE, path availability, spread, volume, or timing. |
| `m1_net_exit_move_points` | M1 post-entry management path feature covering MAE/MFE, path availability, spread, volume, or timing. |
| `m1_time_to_mfe_minutes` | M1 post-entry management path feature covering MAE/MFE, path availability, spread, volume, or timing. |
| `m1_time_to_mae_minutes` | M1 post-entry management path feature covering MAE/MFE, path availability, spread, volume, or timing. |
| `m1_spread_mean` | M1 post-entry management path feature covering MAE/MFE, path availability, spread, volume, or timing. |
| `m1_spread_max` | M1 post-entry management path feature covering MAE/MFE, path availability, spread, volume, or timing. |
| `m1_tick_volume_sum` | M1 post-entry management path feature covering MAE/MFE, path availability, spread, volume, or timing. |
| `m1_tick_volume_mean` | M1 post-entry management path feature covering MAE/MFE, path availability, spread, volume, or timing. |
| `holding_minutes` | Timestamp or duration feature. |
| `m1_mfe_atr_14` | M15 ATR volatility context generated with pandas-ta-classic and used for ATR-normalized path features. |
| `m1_mae_atr_14` | M15 ATR volatility context generated with pandas-ta-classic and used for ATR-normalized path features. |
