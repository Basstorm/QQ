from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from qq_research.features import (
    add_basket_structure_features,
    add_time_session_features,
    attach_m15_entry_context,
    compute_position_path_features,
)

OUTPUTS = PROJECT / "outputs"
POSITIONS_PARQUET = OUTPUTS / "positions.parquet"
BASKETS_PARQUET = OUTPUTS / "baskets.parquet"
M15_CSV = PROJECT / "xauusd_m15_2016_2025.csv"
M1_CSV = PROJECT / "xauusd_m1_2016_2026.csv"


def build_deal_features(positions: pd.DataFrame, m15: pd.DataFrame, m1: pd.DataFrame) -> pd.DataFrame:
    deal_features, _ = add_basket_structure_features(positions)
    deal_features = add_time_session_features(deal_features, "entry_time", "exit_time")
    deal_features = attach_m15_entry_context(deal_features, m15)
    deal_features = compute_position_path_features(deal_features, m1)
    deal_features["holding_minutes"] = deal_features["holding_seconds"] / 60
    deal_features["m1_mfe_atr_14"] = deal_features["m1_mfe_points"] / deal_features["m15_atr_14"]
    deal_features["m1_mae_atr_14"] = deal_features["m1_mae_points"] / deal_features["m15_atr_14"]
    return deal_features.sort_values(["entry_time", "position_id"], kind="mergesort").reset_index(drop=True)


def build_basket_features(baskets: pd.DataFrame, positions: pd.DataFrame, m15: pd.DataFrame, m1: pd.DataFrame) -> pd.DataFrame:
    _, structure = add_basket_structure_features(positions, baskets)
    basket_features = add_time_session_features(structure, "first_entry_time", "last_exit_time")
    basket_features = attach_m15_entry_context(
        basket_features,
        m15,
        entry_time_col="first_entry_time",
        entry_price_col="initial_entry_price",
    )
    basket_features = compute_position_path_features(
        basket_features,
        m1,
        id_col="basket_id",
        entry_time_col="first_entry_time",
        exit_time_col="last_exit_time",
        entry_price_col="initial_entry_price",
        exit_price_col="final_exit_price",
    )
    basket_features["holding_minutes"] = basket_features["holding_seconds"] / 60
    basket_features["m1_mfe_atr_14"] = basket_features["m1_mfe_points"] / basket_features["m15_atr_14"]
    basket_features["m1_mae_atr_14"] = basket_features["m1_mae_points"] / basket_features["m15_atr_14"]
    return basket_features.sort_values("basket_id").reset_index(drop=True)


def build_feature_dictionary(deal_features: pd.DataFrame, basket_features: pd.DataFrame) -> str:
    lines = [
        "# Phase 2 Feature Dictionary",
        "",
        "## Table Semantics",
        "",
        "- `deal_features.parquet`: reconstructed position / entry-deal level. One row is one FIFO-matched entry-to-exit position fragment, preserving `entry_deal`, `exit_deal`, `strategy`, `T`, `S`, `broker_*`, and estimated UTC session fields.",
        "- `basket_features.parquet`: reconstructed analytical basket/cycle level. One row is one interval-based basket from Phase 1, augmented with initial-entry, add-on, close-span, M15 context, and M1 path features.",
        "",
        "## Indicator Implementation",
        "",
        "- M15 technical indicators use `pandas-ta-classic`, the installable pandas-ta compatible package available in this environment.",
        "- `m15_rsi_14`, `m15_adx_14`, `m15_dmp_14`, `m15_dmn_14`, `m15_macd_12_26_9`, `m15_macd_hist_12_26_9`, `m15_macd_signal_12_26_9`, `m15_atr_14`, and `m15_ema_*` are generated through pandas-ta-classic with short-sample fallbacks where needed.",
        "",
        "## `deal_features.parquet` Columns",
        "",
        "| Column | Description |",
        "|---|---|",
    ]
    lines.extend(feature_rows(deal_features.columns))
    lines.extend(
        [
            "",
            "## `basket_features.parquet` Columns",
            "",
            "| Column | Description |",
            "|---|---|",
        ]
    )
    lines.extend(feature_rows(basket_features.columns))
    return "\n".join(lines) + "\n"


def feature_rows(columns: pd.Index) -> list[str]:
    return [f"| `{column}` | {describe_column(str(column))} |" for column in columns]


def describe_column(column: str) -> str:
    if column in {"strategy", "T", "S", "direction", "symbol", "tag_symbol", "magic"}:
        return "Strategy identity and direction metadata preserved from Phase 1 reconstruction."
    if column in {"position_id", "basket_id", "entry_deal", "exit_deal", "entry_order", "exit_order"}:
        return "Identifier preserved from reconstructed trades or MT5 report records."
    if column.startswith("broker_"):
        return "Broker/server-clock time feature used for candle joins and raw timing diagnostics."
    if column.startswith("utc_"):
        return "Estimated UTC feature derived as broker time minus 3 hours for session analysis."
    if column.startswith("m15_rsi") or column.startswith("m15_adx") or column.startswith("m15_dmp") or column.startswith("m15_dmn") or column.startswith("m15_macd"):
        return "M15 technical indicator generated with pandas-ta-classic."
    if column.startswith("m15_ema") or "distance_to_m15_ema" in column:
        return "M15 EMA trend context generated with pandas-ta-classic and derived distance/slope features."
    if column.startswith("m15_atr") or column.endswith("_atr_14"):
        return "M15 ATR volatility context generated with pandas-ta-classic and used for ATR-normalized path features."
    if column.startswith("m15_momentum") or column.startswith("m15_breakout") or column.startswith("m15_recent"):
        return "M15 lookback momentum, recent high/low, and breakout relation feature."
    if column.startswith("m15_") or column.startswith("entry_price_position"):
        return "M15 entry-bar candle context, shape, spread, volume, or price-location feature."
    if column.startswith("m1_"):
        return "M1 post-entry management path feature covering MAE/MFE, path availability, spread, volume, or timing."
    if column in {"is_initial_entry", "entry_sequence_in_basket", "add_on_count"} or column.startswith("add_on"):
        return "Basket/order-structure feature distinguishing initial signal entries from add-ons."
    if column.startswith("initial_") or column.startswith("final_") or column.startswith("close_") or column == "closed_together_within_1m":
        return "Basket structure and close-coordination feature."
    if "pnl" in column or "profit" in column:
        return "PnL/profit field from Phase 1 reconstruction or MT5 exit report."
    if "time" in column or "seconds" in column or "minutes" in column:
        return "Timestamp or duration feature."
    if "price" in column:
        return "Price level or price-difference feature."
    if "volume" in column:
        return "Lot size or tick/real-volume feature."
    return "Feature preserved or derived during Phase 2 feature engineering."


def build_phase2_report(deal_features: pd.DataFrame, basket_features: pd.DataFrame) -> str:
    initial_entries = deal_features[deal_features["is_initial_entry"]]
    initial_m15_share = initial_entries["broker_entry_minute_mod_15"].eq(0).mean()
    all_entry_m15_share = deal_features["broker_entry_minute_mod_15"].eq(0).mean()
    m1_path_share = deal_features["m1_path_available"].mean()
    lines = [
        "# Phase 2 Feature Engineering Report",
        "",
        "## Executive Summary",
        "",
        f"- Wrote `outputs/deal_features.parquet`: `{len(deal_features)}` reconstructed position/entry-deal rows x `{deal_features.shape[1]}` columns.",
        f"- Wrote `outputs/basket_features.parquet`: `{len(basket_features)}` basket rows x `{basket_features.shape[1]}` columns.",
        "- Wrote `outputs/feature_dictionary.md` documenting generated columns.",
        "- M15 candle context is joined using broker/report time with `0h` offset.",
        "- Estimated UTC session labels use `utc_time_est = broker_time - 3h`.",
        "- M15 technical indicators are generated with `pandas-ta-classic`.",
        "",
        "## Initial-entry M15 alignment",
        "",
        f"- Share of all reconstructed entry/position rows at broker minute `% 15 == 0`: `{all_entry_m15_share:.4f}`.",
        f"- Share of initial basket entries at broker minute `% 15 == 0`: `{initial_m15_share:.4f}`.",
        "- Initial-entry timing is the better diagnostic for the user's M15-entry hypothesis because add-ons are not expected to align strictly to M15 boundaries.",
        "",
        "## M1 Path Coverage",
        "",
        f"- M1 path available for deal features: `{m1_path_share:.4f}`.",
        "",
        "## Strategy Summary",
        "",
        "| Strategy | Positions | Baskets | PnL est | Initial entries | Avg add-ons/basket | Avg MAE points | Avg MFE points |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
        strategy_summary_table(deal_features, basket_features),
        "",
        "## Notes Before Clustering / Rule Inference",
        "",
        "1. Use `is_initial_entry == True` rows when evaluating M15 signal hypotheses.",
        "2. Use add-on spacing, close span, and M1 MAE/MFE features for management-behavior clustering.",
        "3. Keep strategy labels as supervised reference groups; clustering should test whether behavior naturally separates beyond explicit `T/S` tags.",
        "4. Treat `T3/S06` as a priority outlier because Phase 1 found large negative PnL and unusually long holds.",
    ]
    return "\n".join(lines) + "\n"


def strategy_summary_table(deal_features: pd.DataFrame, basket_features: pd.DataFrame) -> str:
    deal_group = deal_features.groupby("strategy", dropna=False).agg(
        positions=("position_id", "count"),
        pnl=("pnl_est", "sum"),
        initial_entries=("is_initial_entry", "sum"),
        avg_mae=("m1_mae_points", "mean"),
        avg_mfe=("m1_mfe_points", "mean"),
    )
    basket_group = basket_features.groupby("strategy", dropna=False).agg(
        baskets=("basket_id", "count"),
        avg_addons=("add_on_count", "mean"),
    )
    table = deal_group.join(basket_group, how="outer").sort_index()
    rows = []
    for strategy, row in table.iterrows():
        rows.append(
            f"| {strategy} | {int(row['positions'])} | {int(row['baskets'])} | {row['pnl']:.2f} | {int(row['initial_entries'])} | {row['avg_addons']:.2f} | {row['avg_mae']:.2f} | {row['avg_mfe']:.2f} |"
        )
    return "\n".join(rows)


def read_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    positions = pd.read_parquet(POSITIONS_PARQUET)
    baskets = pd.read_parquet(BASKETS_PARQUET)
    m15 = pd.read_csv(M15_CSV)
    m1 = pd.read_csv(M1_CSV)
    return positions, baskets, m15, m1


def main() -> None:
    OUTPUTS.mkdir(exist_ok=True)
    positions, baskets, m15, m1 = read_inputs()
    deal_features = build_deal_features(positions, m15, m1)
    basket_features = build_basket_features(baskets, positions, m15, m1)
    deal_features.to_parquet(OUTPUTS / "deal_features.parquet", index=False)
    basket_features.to_parquet(OUTPUTS / "basket_features.parquet", index=False)
    (OUTPUTS / "feature_dictionary.md").write_text(build_feature_dictionary(deal_features, basket_features), encoding="utf-8")
    (OUTPUTS / "phase2_feature_report.md").write_text(build_phase2_report(deal_features, basket_features), encoding="utf-8")
    print("Wrote outputs/deal_features.parquet")
    print("Wrote outputs/basket_features.parquet")
    print("Wrote outputs/feature_dictionary.md")
    print("Wrote outputs/phase2_feature_report.md")


if __name__ == "__main__":
    main()
