# QuantumQueenApproxNonRisky EA

`Experts/QuantumQueenApproxNonRisky.mq5` is a first-pass MT5 Expert Advisor generated from the current reverse-engineered non-risky Quantum Queen conclusions.

## Scope

Included matched-context strategies:

- `T1/S01`
- `T2/S03`
- `T2/S04`
- `T4/S08`
- `T5/S09`

Excluded strategies:

- `T3/S06`
- `T5/S10`
- `T6/S12`

## Trading model

- Long-only, XAUUSD-oriented.
- Entry checks run once per new M15 bar.
- Basket management runs once per new M1 bar.
- Basket exits use close-based VWAP TP thresholds.
- Add-ons use adverse distance from the last layer plus optional minimum minutes since the last layer.
- Basket layering is capped by the observed max layer count for each included strategy.
- Entry is edge-only: a basket opens only when a strategy condition changes from false to true.
- `TpSpreadCompensationPoints` and `AddOnSpreadCompensationPoints` compensate for the difference between the Python close/close research model and MT5 ask/bid execution.
- `RequireCurrentM15Confirmation` requires the current forming M15 bar to still satisfy the entry condition before acting on the last closed M15 signal. This filters stale entries where the previous bar was valid but the current bar has already invalidated the setup.

## Position sizing

Default compounding size:

```text
floor(AccountBalance / 400) * 0.01 lots
```

The EA normalizes the final lot to the broker's min/max/step.

## Backtest notes

Copy `Experts/QuantumQueenApproxNonRisky.mq5` into the MT5 data folder under `MQL5/Experts/`, compile in MetaEditor, and run Strategy Tester on XAUUSD.

Use an MT5 hedging account for basket/layer behavior. On a netting account, positions on the same symbol may be merged and the add-on basket logic will not match the intended model.

This EA is an approximation for research backtesting, not source-code recovery. It does not model all original QQ hidden behavior, broker-side execution nuances, spread/slippage assumptions, or S06/S10/S12 risk logic.

Version `0.12` intentionally does not add an emergency stop or timeout guard, so it remains closer to the Python research backtest. It only adds edge-only entry, spread compensation, and current-bar confirmation to reduce stale closed-bar entries. If this version still diverges strongly, the next likely cause to inspect is MT5 indicator-definition differences versus the Python/pandas-ta feature matrix.
