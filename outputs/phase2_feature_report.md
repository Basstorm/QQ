# Phase 2 Feature Engineering Report

## Executive Summary

- Wrote `outputs/deal_features.parquet`: `6100` reconstructed position/entry-deal rows x `160` columns.
- Wrote `outputs/basket_features.parquet`: `1657` basket rows x `154` columns.
- Wrote `outputs/feature_dictionary.md` documenting generated columns.
- M15 candle context is joined using broker/report time with `0h` offset.
- Estimated UTC session labels use `utc_time_est = broker_time - 3h`.
- M15 technical indicators are generated with `pandas-ta-classic`.

## Initial-entry M15 alignment

- Share of all reconstructed entry/position rows at broker minute `% 15 == 0`: `0.3739`.
- Share of initial basket entries at broker minute `% 15 == 0`: `0.6270`.
- Initial-entry timing is the better diagnostic for the user's M15-entry hypothesis because add-ons are not expected to align strictly to M15 boundaries.

## M1 Path Coverage

- M1 path available for deal features: `1.0000`.

## Strategy Summary

| Strategy | Positions | Baskets | PnL est | Initial entries | Avg add-ons/basket | Avg MAE points | Avg MFE points |
|---|---:|---:|---:|---:|---:|---:|---:|
| T1/S01 | 1769 | 459 | 4625172.10 | 459 | 2.85 | 2.80 | 2.04 |
| T2/S03 | 1193 | 318 | 2774986.27 | 318 | 2.75 | 2.44 | 1.75 |
| T2/S04 | 1231 | 378 | 2246850.28 | 378 | 2.26 | 2.32 | 1.49 |
| T3/S06 | 402 | 99 | -14994461.54 | 99 | 3.06 | 19.48 | 4.37 |
| T4/S08 | 231 | 58 | 1014496.77 | 58 | 2.98 | 3.42 | 2.73 |
| T5/S09 | 234 | 71 | 1520356.22 | 71 | 2.30 | 4.94 | 3.86 |
| T5/S10 | 386 | 108 | 2101890.16 | 108 | 2.57 | 3.44 | 3.18 |
| T6/S12 | 654 | 166 | 2057978.15 | 166 | 2.94 | 3.33 | 2.69 |

## Notes Before Clustering / Rule Inference

1. Use `is_initial_entry == True` rows when evaluating M15 signal hypotheses.
2. Use add-on spacing, close span, and M1 MAE/MFE features for management-behavior clustering.
3. Keep strategy labels as supervised reference groups; clustering should test whether behavior naturally separates beyond explicit `T/S` tags.
4. Treat `T3/S06` as a priority outlier because Phase 1 found large negative PnL and unusually long holds.
