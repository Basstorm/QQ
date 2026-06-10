# Expanded Indicator / Parameter Discovery Report

## Scope

- This is a broad first-pass search over public technical-indicator features using `pandas-ta-classic` plus explicit MA stacking/crossover features.
- It scores each feature separately for each explicit `Sxx`, comparing that strategy's initial-entry M15 bars against the M15 background.
- Positive counts are unique M15 bars with at least one initial basket entry for that `Sxx`; multiple entries on the same M15 bar collapse to one positive bar.
- High AUC lift is evidence of separation, not proof of the exact EA rule. Combined multi-condition searches can build on these ranked candidates.

## Indicator Universe Notes

- `pandas-ta-classic` exposes `305` lowercase callable names in this environment.
- First-pass computed families include MA slope/distance/spread/stacking/cross, RSI, CCI, CMO, ROC, MOM, ADX/DMI, AROON, Bollinger Bands, Donchian, Keltner Channels, CHOP, Fisher, AO, BOP, CMF, and EFI.
- This is intentionally broader than the compact Phase 4 feature set but still not exhaustive. The next pass can add more families from the callable universe.

## Output Files

- `outputs/expanded_indicator_feature_matrix.parquet`
- `outputs/expanded_indicator_scores.csv`
- `outputs/expanded_indicator_discovery_report.md`

## Data Summary

- M15 feature rows: `143097`.
- Generated feature columns: `137`.

## Top Candidates by Strategy

### T1/S01

- Initial-entry positives: `377`.

| Feature | Direction | AUC | AUC lift | Positive median | Background median |
|---|---|---:|---:|---:|---:|
| `fisher_14` | high | 0.8970 | 0.3970 | 2.8132 | 0.0632 |
| `fisher_9` | high | 0.8970 | 0.3970 | 2.6333 | 0.0466 |
| `wma_21_slope_4` | high | 0.8743 | 0.3743 | 1.4271 | 0.0147 |
| `adx_7_dmn_7` | low | 0.1272 | 0.3728 | 8.3180 | 19.8276 |
| `wma_8_minus_wma_21` | high | 0.8696 | 0.3696 | 1.6044 | 0.0192 |
| `close_minus_sma_21` | high | 0.8643 | 0.3643 | 3.5967 | 0.0467 |
| `ema_8_slope_4` | high | 0.8643 | 0.3643 | 1.5638 | 0.0185 |
| `ema_21_slope_4` | high | 0.8621 | 0.3621 | 1.3379 | 0.0199 |
| `sma_8_minus_sma_21` | high | 0.8571 | 0.3571 | 2.1791 | 0.0252 |
| `cmo_9` | high | 0.8567 | 0.3567 | 53.3454 | 0.7605 |
| `cmo_14` | high | 0.8563 | 0.3563 | 42.1603 | 0.5894 |
| `rsi_8` | high | 0.8552 | 0.3552 | 69.7387 | 50.4086 |

### T2/S03

- Initial-entry positives: `318`.

| Feature | Direction | AUC | AUC lift | Positive median | Background median |
|---|---|---:|---:|---:|---:|
| `wma_21_minus_wma_50` | high | 0.9401 | 0.4401 | 4.9460 | 0.0425 |
| `ao` | high | 0.9283 | 0.4283 | 7.0979 | 0.0702 |
| `roc_34` | high | 0.9266 | 0.4266 | 0.9005 | 0.0096 |
| `wma_50_slope_4` | high | 0.9265 | 0.4265 | 1.6236 | 0.0165 |
| `close_minus_sma_50` | high | 0.9223 | 0.4223 | 10.1798 | 0.1116 |
| `mom_34` | high | 0.9217 | 0.4217 | 15.8350 | 0.1500 |
| `sma_21_minus_sma_50` | high | 0.9174 | 0.4174 | 6.5777 | 0.0658 |
| `sma_21_slope_4` | high | 0.9162 | 0.4162 | 2.1479 | 0.0162 |
| `ema_50_slope_4` | high | 0.9162 | 0.4162 | 1.3326 | 0.0195 |
| `ema_8_minus_ema_21` | high | 0.9116 | 0.4116 | 2.6170 | 0.0313 |
| `close_minus_wma_50` | high | 0.9092 | 0.4092 | 6.5998 | 0.0831 |
| `close_minus_ema_50` | high | 0.9075 | 0.4075 | 7.9533 | 0.1252 |

### T2/S04

- Initial-entry positives: `378`.

| Feature | Direction | AUC | AUC lift | Positive median | Background median |
|---|---|---:|---:|---:|---:|
| `roc_20` | high | 0.9581 | 0.4581 | 0.8012 | 0.0049 |
| `sma_21_slope_4` | high | 0.9567 | 0.4567 | 2.6671 | 0.0157 |
| `ao` | high | 0.9557 | 0.4557 | 8.8970 | 0.0692 |
| `ema_8_minus_ema_21` | high | 0.9542 | 0.4542 | 3.8125 | 0.0308 |
| `wma_21_minus_wma_50` | high | 0.9534 | 0.4534 | 5.2581 | 0.0413 |
| `mom_20` | high | 0.9525 | 0.4525 | 13.8800 | 0.0800 |
| `wma_50_slope_4` | high | 0.9498 | 0.4498 | 1.9202 | 0.0162 |
| `ema_50_slope_4` | high | 0.9475 | 0.4475 | 1.6458 | 0.0193 |
| `close_minus_sma_50` | high | 0.9472 | 0.4472 | 11.6161 | 0.1096 |
| `close_minus_wma_50` | high | 0.9463 | 0.4463 | 8.7387 | 0.0815 |
| `roc_34` | high | 0.9459 | 0.4459 | 0.9086 | 0.0094 |
| `wma_21_slope_4` | high | 0.9447 | 0.4447 | 2.6060 | 0.0147 |

### T3/S06

- Initial-entry positives: `83`.

| Feature | Direction | AUC | AUC lift | Positive median | Background median |
|---|---|---:|---:|---:|---:|
| `rsi_34` | low | 0.0545 | 0.4455 | 36.1488 | 50.3680 |
| `adx_21_dmp_21` | low | 0.0592 | 0.4408 | 11.1566 | 20.2380 |
| `rsi_21` | low | 0.0644 | 0.4356 | 34.4900 | 50.3539 |
| `ema_50_slope_4` | low | 0.0645 | 0.4355 | -1.2138 | 0.0215 |
| `wma_50_slope_4` | low | 0.0657 | 0.4343 | -1.4494 | 0.0185 |
| `ema_21_minus_ema_50` | low | 0.0660 | 0.4340 | -4.5039 | 0.0798 |
| `close_minus_ema_50` | low | 0.0676 | 0.4324 | -7.1314 | 0.1370 |
| `close_minus_sma_50` | low | 0.0685 | 0.4315 | -9.0588 | 0.1268 |
| `cmo_21` | low | 0.0707 | 0.4293 | -42.2292 | 0.7126 |
| `wma_21_minus_wma_50` | low | 0.0719 | 0.4281 | -3.7857 | 0.0477 |
| `sma_50_slope_4` | low | 0.0726 | 0.4274 | -1.2704 | 0.0268 |
| `roc_34` | low | 0.0741 | 0.4259 | -0.8271 | 0.0109 |

### T4/S08

- Initial-entry positives: `47`.

| Feature | Direction | AUC | AUC lift | Positive median | Background median |
|---|---|---:|---:|---:|---:|
| `rsi_34` | high | 0.9666 | 0.4666 | 67.7285 | 50.3577 |
| `ema_21_minus_ema_50` | high | 0.9629 | 0.4629 | 7.8647 | 0.0773 |
| `close_minus_ema_50` | high | 0.9523 | 0.4523 | 16.0722 | 0.1335 |
| `ema_50_slope_4` | high | 0.9520 | 0.4520 | 2.4320 | 0.0208 |
| `adx_21_adx_21` | high | 0.9472 | 0.4472 | 47.5722 | 19.6285 |
| `sma_50_slope_4` | high | 0.9448 | 0.4448 | 2.2950 | 0.0262 |
| `rsi_21` | high | 0.9423 | 0.4423 | 68.9883 | 50.3394 |
| `adx_21_dmp_21` | high | 0.9423 | 0.4423 | 33.1890 | 20.2298 |
| `close_minus_sma_50` | high | 0.9394 | 0.4394 | 17.7810 | 0.1214 |
| `adx_21_dmn_21` | low | 0.0617 | 0.4383 | 10.7987 | 20.7246 |
| `wma_50_slope_4` | high | 0.9382 | 0.4382 | 2.5698 | 0.0177 |
| `roc_34` | high | 0.9290 | 0.4290 | 1.1670 | 0.0104 |

### T5/S09

- Initial-entry positives: `67`.

| Feature | Direction | AUC | AUC lift | Positive median | Background median |
|---|---|---:|---:|---:|---:|
| `fisher_9` | high | 0.9723 | 0.4723 | 3.8476 | 0.0513 |
| `cmo_14` | high | 0.9692 | 0.4692 | 69.2552 | 0.6782 |
| `fisher_14` | high | 0.9685 | 0.4685 | 4.0160 | 0.0692 |
| `adx_7_adx_7` | high | 0.9626 | 0.4626 | 68.9157 | 32.1016 |
| `adx_14_dmp_14` | high | 0.9530 | 0.4530 | 37.7014 | 20.0431 |
| `rsi_14` | high | 0.9489 | 0.4489 | 74.7930 | 50.3831 |
| `adx_14_dmn_14` | low | 0.0544 | 0.4456 | 7.1122 | 20.4686 |
| `wma_8_minus_wma_21` | high | 0.9451 | 0.4451 | 2.9513 | 0.0219 |
| `wma_21_slope_4` | high | 0.9437 | 0.4437 | 2.3879 | 0.0173 |
| `cmo_21` | high | 0.9421 | 0.4421 | 54.7782 | 0.6678 |
| `ema_21_slope_4` | high | 0.9417 | 0.4417 | 2.0429 | 0.0218 |
| `adx_21_dmp_21` | high | 0.9410 | 0.4410 | 33.6933 | 20.2288 |

### T5/S10

- Initial-entry positives: `104`.

| Feature | Direction | AUC | AUC lift | Positive median | Background median |
|---|---|---:|---:|---:|---:|
| `fisher_9` | high | 0.8509 | 0.3509 | 2.7380 | 0.0510 |
| `fisher_14` | high | 0.8368 | 0.3368 | 2.8938 | 0.0689 |
| `wma_8_minus_wma_21` | high | 0.8261 | 0.3261 | 1.8379 | 0.0219 |
| `sma_8_slope_4` | high | 0.8234 | 0.3234 | 1.9512 | 0.0188 |
| `chop_14` | low | 0.1795 | 0.3205 | 38.1306 | 50.4614 |
| `sma_8_minus_sma_21` | high | 0.8166 | 0.3166 | 2.3579 | 0.0292 |
| `cmo_14` | high | 0.8152 | 0.3152 | 46.7563 | 0.6734 |
| `wma_21_slope_4` | high | 0.8114 | 0.3114 | 1.4863 | 0.0172 |
| `hma_32_slope_4` | high | 0.8102 | 0.3102 | 2.1260 | 0.0209 |
| `roc_10` | high | 0.8062 | 0.3062 | 0.2705 | 0.0038 |
| `ema_21_slope_4` | high | 0.8040 | 0.3040 | 1.2867 | 0.0218 |
| `mom_10` | high | 0.8024 | 0.3024 | 4.4650 | 0.0600 |

### T6/S12

- Initial-entry positives: `159`.

| Feature | Direction | AUC | AUC lift | Positive median | Background median |
|---|---|---:|---:|---:|---:|
| `adx_7_dmp_7` | low | 0.0529 | 0.4471 | 4.7437 | 19.4351 |
| `cmo_9` | low | 0.0641 | 0.4359 | -65.7767 | 0.9756 |
| `cci_34` | low | 0.0659 | 0.4341 | -188.8546 | 5.1237 |
| `fisher_9` | low | 0.0688 | 0.4312 | -2.7812 | 0.0548 |
| `adx_7_dmn_7` | high | 0.9311 | 0.4311 | 40.2800 | 19.7819 |
| `rsi_8` | low | 0.0707 | 0.4293 | 24.4849 | 50.4741 |
| `rsi_14` | low | 0.0708 | 0.4292 | 30.9938 | 50.4086 |
| `cci_20` | low | 0.0718 | 0.4282 | -174.5160 | 3.7926 |
| `bbands_34_bbp_34_2_0` | low | 0.0729 | 0.4271 | -0.0317 | 0.5148 |
| `adx_14_dmp_14` | low | 0.0735 | 0.4265 | 9.9915 | 20.0570 |
| `adx_14_dmn_14` | high | 0.9254 | 0.4254 | 34.4085 | 20.4547 |
| `cmo_21` | low | 0.0759 | 0.4241 | -41.4400 | 0.7299 |

## Next Use

- For low-confidence compact profiles, inspect top features here and build two/three-condition candidate rules per `Sxx`.
- MA crossover/stacking features such as `ema_8_gt_ema_21`, `ema_8_cross_above_ema_21`, and bars-since-cross are included in the score table when they separate entries.
- Treat all findings as hypotheses requiring false-positive/false-negative validation against non-entry M15 bars.
