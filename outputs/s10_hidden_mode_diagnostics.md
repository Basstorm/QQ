# T5/S10 Hidden Target Mode Diagnostics

## Target Mode Counts

| Target mode | Baskets |
|---|---:|
| `late_high` | 18 |
| `mixed_other` | 8 |
| `overnight_medium` | 34 |
| `quick_low` | 34 |
| `timeout_loss` | 14 |

## Feature Separation Scores

| Feature | Eta squared | Non-null | Mode medians |
|---|---:|---:|---|
| `path_mae` | 0.580 | 108 | late_high=-3.585; mixed_other=-6.161; overnight_medium=-1.935; quick_low=-0.265; timeout_loss=-2.525 |
| `path_mfe` | 0.458 | 108 | late_high=4.286; mixed_other=2.258; overnight_medium=2.065; quick_low=1.945; timeout_loss=0.060 |
| `entry_hour` | 0.430 | 108 | late_high=8.500; mixed_other=22.000; overnight_medium=22.000; quick_low=22.000; timeout_loss=22.000 |
| `mfe_30m` | 0.339 | 108 | late_high=0.630; mixed_other=0.220; overnight_medium=0.325; quick_low=1.570; timeout_loss=0.060 |
| `early_adverse_max` | 0.257 | 108 | late_high=1.185; mixed_other=0.450; overnight_medium=1.010; quick_low=0.260; timeout_loss=1.760 |
| `mae_30m` | 0.238 | 108 | late_high=-1.185; mixed_other=-0.465; overnight_medium=-1.010; quick_low=-0.260; timeout_loss=-1.760 |
| `mfe_5m` | 0.225 | 108 | late_high=0.065; mixed_other=-0.115; overnight_medium=-0.150; quick_low=0.770; timeout_loss=0.015 |
| `observed_minutes` | 0.219 | 108 | late_high=658.500; mixed_other=1174.000; overnight_medium=289.500; quick_low=19.000; timeout_loss=53.500 |
| `mae_5m` | 0.125 | 108 | late_high=-0.350; mixed_other=-0.395; overnight_medium=-0.500; quick_low=-0.100; timeout_loss=-0.770 |
| `max_layers_30m` | 0.009 | 108 | late_high=1.000; mixed_other=1.000; overnight_medium=1.000; quick_low=1.000; timeout_loss=1.000 |
| `entry_minute` | 0.007 | 108 | late_high=18.500; mixed_other=22.500; overnight_medium=20.000; quick_low=20.000; timeout_loss=0.000 |
| `add_ons_30m` | 0.003 | 108 | late_high=0.000; mixed_other=0.000; overnight_medium=0.000; quick_low=0.000; timeout_loss=0.000 |

## Interpretation

- `path_mfe`, `path_mae`, and `observed_minutes` are post-entry/full-path diagnostics and should not be used as live entry-time selectors.
- The strongest practical early-path separator is `quick_low` via favorable movement in the first 5-30 minutes.
- Other S10 target modes remain weakly separated by entry/early-path single features.

## Best One-Feature Early Rules

| Target mode | Rule | Matched | Precision | Recall | F1 |
|---|---|---:|---:|---:|---:|
| `quick_low` | `mfe_30m >= 0.680` | 54 | 0.556 | 0.882 | 0.682 |
| `quick_low` | `mfe_5m >= 0.150` | 54 | 0.519 | 0.824 | 0.636 |
| `quick_low` | `mfe_5m >= 0.683` | 27 | 0.704 | 0.559 | 0.623 |
| `quick_low` | `mae_5m >= -0.110` | 27 | 0.704 | 0.559 | 0.623 |
| `quick_low` | `mfe_30m >= 1.435` | 27 | 0.704 | 0.559 | 0.623 |
| `quick_low` | `mfe_30m >= 0.024` | 81 | 0.420 | 1.000 | 0.591 |
| `quick_low` | `mae_30m >= -0.815` | 54 | 0.481 | 0.765 | 0.591 |
| `quick_low` | `early_adverse_max <= 0.815` | 54 | 0.481 | 0.765 | 0.591 |
| `quick_low` | `mae_30m >= -1.680` | 81 | 0.407 | 0.971 | 0.574 |
| `quick_low` | `early_adverse_max <= 1.680` | 81 | 0.407 | 0.971 | 0.574 |
| `quick_low` | `mae_30m >= -0.265` | 27 | 0.630 | 0.500 | 0.557 |
| `quick_low` | `early_adverse_max <= 0.265` | 27 | 0.630 | 0.500 | 0.557 |
| `overnight_medium` | `mfe_5m <= 0.683` | 81 | 0.395 | 0.941 | 0.557 |
| `overnight_medium` | `mae_5m <= -0.110` | 81 | 0.395 | 0.941 | 0.557 |
| `quick_low` | `mfe_5m >= -0.260` | 82 | 0.390 | 0.941 | 0.552 |
| `overnight_medium` | `mfe_30m <= 1.435` | 81 | 0.383 | 0.912 | 0.539 |
| `quick_low` | `entry_hour >= 22.000` | 95 | 0.358 | 1.000 | 0.527 |
| `quick_low` | `entry_hour >= 22.000` | 95 | 0.358 | 1.000 | 0.527 |
| `quick_low` | `entry_hour >= 22.000` | 95 | 0.358 | 1.000 | 0.527 |
| `overnight_medium` | `mfe_5m <= 0.150` | 54 | 0.426 | 0.676 | 0.523 |
