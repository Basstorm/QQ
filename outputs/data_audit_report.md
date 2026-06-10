# Phase 0 Data Audit Report

## Executive Summary

- Workbook sheets: `['Sheet1']`.
- Main sheet dimensions: `22707` rows x `15` columns.
- Expert: `Quantum Queen 3.52(2)`.
- Symbol: `XAUUSD`.
- Test period field: `M15 (2018.01.01 - 2026.06.09)`.
- Magic input: `1234`.
- Set input: `3`.
- Orders parsed: `11310`.
- Deals parsed: `11310`.
- Entry deals: `5655`; exit deals: `5655`.
- Every entry deal has an explicit strategy tag: `5655/5655`.
- Active strategy tags observed: `8`.
- This report contains explicit `T*/S*` strategy identifiers in entry comments, so Phase 1+ should preserve those labels before attempting behavioral clustering.

## Timezone / Offset Check

The user recalled that exported trade-record time is GMT+3. Against the provided M1 CSV, the best alignment is not `-3h`; it is `0h` after flooring trade timestamps to the minute.

- Best all-deal offset at tolerance 0.25: `0h`, match rate `0.9908`.
- Best entry-only offset at tolerance 0.25: `0h`, match rate `0.9827`.
- Interpretation: report timestamps and CSV timestamps share the same clock for analysis alignment. If the report is broker GMT+3, then the CSV timestamps should also be treated as broker/server time despite the `+00:00` suffix. For true UTC session labels, subtracting 3 hours may still be appropriate, but price/time joining should use offset `0h`.

Top offsets for all deals, tolerance 0.25:

| Offset hours applied to report time | Available | Matched | Match rate | Median distance | P90 distance |
|---:|---:|---:|---:|---:|---:|
| 0 | 11310 | 11206 | 0.9908 | 0.0000 | 0.0800 |
| 1 | 9987 | 1836 | 0.1838 | 1.2000 | 4.8400 |
| 2 | 7859 | 1065 | 0.1355 | 1.8500 | 6.5400 |
| 3 | 9900 | 1076 | 0.1087 | 2.0300 | 8.2800 |
| 5 | 8680 | 850 | 0.0979 | 2.6400 | 10.7410 |
| -1 | 10562 | 1034 | 0.0979 | 2.2600 | 7.1300 |
| 6 | 9679 | 925 | 0.0956 | 2.9200 | 11.4620 |

## Strategy Tags in Entry Comments

Entry comment pattern:

```text
QQ[XAUUSD]1234[T<family>/S<strategy>]
```

Observed `T/S` counts:

| Strategy tag | Entry count |
|---|---:|
| T1/S01 | 1573 |
| T2/S03 | 1063 |
| T2/S04 | 1216 |
| T3/S06 | 324 |
| T4/S08 | 231 |
| T5/S09 | 234 |
| T5/S10 | 360 |
| T6/S12 | 654 |

Observed `S` counts:

| S id | Entry count |
|---|---:|
| S01 | 1573 |
| S03 | 1063 |
| S04 | 1216 |
| S06 | 324 |
| S08 | 231 |
| S09 | 234 |
| S10 | 360 |
| S12 | 654 |

Important: only 8 strategy IDs appear in this backtest (`S01`, `S03`, `S04`, `S06`, `S08`, `S09`, `S10`, `S12`). The advertised 12 embedded strategies are not all active in this report/preset, or some had no trades in the tested period.

## Input Settings Extracted

| Input | Value |
|---|---|
| `<unnamed>` | `` |
| `InpAutoLotsValue` | `3` |
| `InpBEColor` | `16777215` |
| `InpComment` | `Quantum Queen MT5` |
| `InpDDMode` | `0` |
| `InpDDValue` | `0.0` |
| `InpFont` | `Trebuchet MS` |
| `InpFontSize` | `8` |
| `InpGridColor` | `65535` |
| `InpLineStyle` | `0` |
| `InpLineWidth` | `2` |
| `InpLotsCalc` | `2` |
| `InpLotsFixed` | `0.01` |
| `InpLotsFixedBalance` | `500.0` |
| `InpMQID` | `1` |
| `InpMagicNumber` | `1234` |
| `InpNoteName` | `Quantum Queen MT5 v3.52 (17/03/2026)` |
| `InpNoteOverview` | `XAUUSD. Chart timeframe doesn't matter; the EA manages it internally.` |
| `InpNoteWebsite` | `https://www.mql5.com/en/market/product/118805` |
| `InpPanel` | `1` |
| `InpPause` | `1` |
| `InpSets` | `3` |
| `InpSlippage` | `100` |
| `InpSpread` | `100` |
| `InpTPColor` | `65280` |
| `InpXmas` | `1` |

## CSV Inputs

### `xauusd_m15_2016_2025.csv`

- Rows: `245885`.
- Columns: `['time', 'open', 'high', 'low', 'close', 'tick_volume', 'spread', 'real_volume']`.
- Time range: `2016-01-04 01:00:00+00:00` to `2026-06-08 23:45:00+00:00`.
- Duplicate timestamps: `0`.
- Missing/invalid timestamps: `0`.

### `xauusd_m1_2016_2026.csv`

- Rows: `3667808`.
- Columns: `['time', 'open', 'high', 'low', 'close', 'tick_volume', 'spread', 'real_volume']`.
- Time range: `2016-01-04 01:00:00+00:00` to `2026-06-08 23:57:00+00:00`.
- Duplicate timestamps: `0`.
- Missing/invalid timestamps: `0`.

## Phase 1 Implications

1. Use `T/S` from comments as the primary strategy label for entries.
2. Reconstruct positions/baskets by matching exit deals to prior open positions because exit comments are blank.
3. Use report timestamp floored to minute for M1 joins; do not apply a `-3h` shift when joining to the provided CSV files.
4. Maintain both `broker_time` and derived `utc_time_est = broker_time - 3h` columns for session analysis until the broker timezone/DST policy is fully confirmed.
5. Because closes/add-ons can happen at second offsets within a minute, M1 management analysis must floor timestamps to minute while preserving original seconds for ordering.
