from __future__ import annotations

import re
from collections import deque
from pathlib import Path

import numpy as np
import pandas as pd

STRATEGY_PATTERN = re.compile(r"QQ\[(?P<tag_symbol>[^\]]+)\](?P<magic>\d+)\[T(?P<T>\d+)/S(?P<S>\d+)\]")


def parse_strategy_comment(comment: object) -> dict[str, object] | None:
    if not isinstance(comment, str):
        return None
    match = STRATEGY_PATTERN.search(comment)
    if not match:
        return None
    family = int(match.group("T"))
    strategy_id = int(match.group("S"))
    return {
        "tag_symbol": match.group("tag_symbol"),
        "magic": match.group("magic"),
        "T": family,
        "S": strategy_id,
        "strategy": f"T{family}/S{strategy_id:02d}",
    }


def enrich_strategy_columns(deals: pd.DataFrame) -> pd.DataFrame:
    rows = deals.copy()
    parsed = rows["comment"].map(parse_strategy_comment) if "comment" in rows else pd.Series([None] * len(rows), index=rows.index)
    for col in ["tag_symbol", "magic", "T", "S", "strategy"]:
        rows[col] = parsed.map(lambda item: item.get(col) if item else None)
    return rows


def load_mt5_report(path: str | Path) -> tuple[dict[str, object], dict[str, str], pd.DataFrame, pd.DataFrame]:
    raw = pd.read_excel(path, sheet_name="Sheet1", header=None)
    order_label_idx = int(raw.index[raw[0].astype(str).str.strip().eq("订单")][0])
    deals_label_idx = int(raw.index[raw[0].astype(str).str.strip().eq("成交")][0])
    metadata, inputs = parse_report_metadata(raw)
    orders = parse_orders_section(raw, order_label_idx, deals_label_idx)
    deals = parse_deals_section(raw, deals_label_idx)
    return metadata, inputs, orders, deals


def parse_report_metadata(raw: pd.DataFrame) -> tuple[dict[str, object], dict[str, str]]:
    metadata: dict[str, object] = {}
    inputs: dict[str, str] = {}
    for idx in range(min(len(raw), 82)):
        row = raw.iloc[idx]
        key = row.iloc[0]
        value = row.iloc[3] if len(row) > 3 else None
        if isinstance(key, str) and key.strip().endswith(":"):
            metadata[key.strip().rstrip(":")] = None if pd.isna(value) else value
        if isinstance(value, str) and "=" in value:
            input_key, input_value = value.split("=", 1)
            inputs[input_key.strip()] = input_value.strip()
    return metadata, inputs


def parse_orders_section(raw: pd.DataFrame, order_label_idx: int, deals_label_idx: int) -> pd.DataFrame:
    rows = raw.iloc[order_label_idx + 2 : deals_label_idx, :13].copy()
    rows.columns = [
        "open_time",
        "order",
        "symbol",
        "type",
        "volume_raw",
        "blank_1",
        "requested_price",
        "sl",
        "tp",
        "time",
        "blank_2",
        "status",
        "comment",
    ]
    rows = rows[rows["open_time"].notna()].copy()
    rows["open_time"] = pd.to_datetime(rows["open_time"], format="%Y.%m.%d %H:%M:%S", errors="coerce")
    rows["time"] = pd.to_datetime(rows["time"], format="%Y.%m.%d %H:%M:%S", errors="coerce")
    rows["order"] = pd.to_numeric(rows["order"], errors="coerce").astype("Int64")
    rows["requested_price"] = pd.to_numeric(rows["requested_price"], errors="coerce")
    return rows.drop(columns=["blank_1", "blank_2"])


def parse_deals_section(raw: pd.DataFrame, deals_label_idx: int) -> pd.DataFrame:
    rows = raw.iloc[deals_label_idx + 2 :, :13].copy()
    rows.columns = [
        "time",
        "deal",
        "symbol",
        "type",
        "entry",
        "volume",
        "price",
        "order",
        "commission",
        "swap",
        "profit",
        "balance",
        "comment",
    ]
    rows = rows[rows["time"].notna()].copy()
    rows = rows[rows["symbol"].eq("XAUUSD")].copy()
    rows["time"] = pd.to_datetime(rows["time"], format="%Y.%m.%d %H:%M:%S", errors="coerce")
    for col in ["deal", "order"]:
        rows[col] = pd.to_numeric(rows[col], errors="coerce").astype("Int64")
    for col in ["volume", "price", "commission", "swap", "profit", "balance"]:
        rows[col] = pd.to_numeric(rows[col], errors="coerce")
    rows = enrich_strategy_columns(rows)
    rows["broker_minute"] = rows["time"].dt.floor("min")
    rows["utc_time_est"] = rows["time"] - pd.Timedelta(hours=3)
    return rows.reset_index(drop=True)


def reconstruct_positions_fifo(deals: pd.DataFrame, contract_size: float = 100.0, volume_epsilon: float = 1e-9) -> pd.DataFrame:
    normalized = enrich_strategy_columns(deals).copy()
    normalized = normalized.sort_values(["time", "deal"], kind="mergesort").reset_index(drop=True)
    open_positions: dict[str, deque[dict[str, object]]] = {"buy": deque(), "sell": deque()}
    rows: list[dict[str, object]] = []
    position_id = 1

    for deal in normalized.to_dict(orient="records"):
        entry = deal.get("entry")
        side = deal.get("type")
        volume = float(deal.get("volume") or 0.0)
        if entry == "in":
            open_positions[str(side)].append({**deal, "remaining_volume": volume})
            continue
        if entry != "out":
            continue
        closing_side = "buy" if side == "sell" else "sell" if side == "buy" else None
        if closing_side is None:
            continue
        remaining_to_close = volume
        while remaining_to_close > volume_epsilon:
            if not open_positions[closing_side]:
                raise ValueError(f"No open {closing_side} position available for exit deal {deal.get('deal')}")
            opened = open_positions[closing_side][0]
            available = float(opened["remaining_volume"])
            allocated = min(available, remaining_to_close)
            direction = "long" if closing_side == "buy" else "short"
            pnl_est = estimate_pnl(direction, float(opened["price"]), float(deal["price"]), allocated, contract_size)
            rows.append(
                {
                    "position_id": position_id,
                    "strategy": opened.get("strategy"),
                    "T": opened.get("T"),
                    "S": opened.get("S"),
                    "tag_symbol": opened.get("tag_symbol"),
                    "magic": opened.get("magic"),
                    "symbol": opened.get("symbol"),
                    "direction": direction,
                    "volume": allocated,
                    "entry_time": opened.get("time"),
                    "exit_time": deal.get("time"),
                    "entry_minute": pd.Timestamp(opened.get("time")).floor("min"),
                    "exit_minute": pd.Timestamp(deal.get("time")).floor("min"),
                    "utc_entry_est": opened.get("time") - pd.Timedelta(hours=3),
                    "utc_exit_est": deal.get("time") - pd.Timedelta(hours=3),
                    "entry_price": opened.get("price"),
                    "exit_price": deal.get("price"),
                    "entry_deal": opened.get("deal"),
                    "exit_deal": deal.get("deal"),
                    "entry_order": opened.get("order"),
                    "exit_order": deal.get("order"),
                    "entry_comment": opened.get("comment"),
                    "exit_comment": deal.get("comment"),
                    "exit_profit_reported": deal.get("profit"),
                    "pnl_est": pnl_est,
                    "holding_seconds": (deal.get("time") - opened.get("time")).total_seconds(),
                }
            )
            position_id += 1
            remaining_to_close -= allocated
            opened["remaining_volume"] = available - allocated
            if opened["remaining_volume"] <= volume_epsilon:
                open_positions[closing_side].popleft()

    leftover = sum(float(item["remaining_volume"]) for queue in open_positions.values() for item in queue)
    if leftover > volume_epsilon:
        raise ValueError(f"Unclosed volume remains after reconstruction: {leftover}")
    return pd.DataFrame(rows)


def estimate_pnl(direction: str, entry_price: float, exit_price: float, volume: float, contract_size: float) -> float:
    if direction == "long":
        return (exit_price - entry_price) * volume * contract_size
    if direction == "short":
        return (entry_price - exit_price) * volume * contract_size
    raise ValueError(f"Unknown direction: {direction}")


def assign_baskets(positions: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if positions.empty:
        return positions.assign(basket_id=pd.Series(dtype="int64")), pd.DataFrame()
    assigned = positions.sort_values(["strategy", "direction", "entry_time", "exit_time", "position_id"], kind="mergesort").copy()
    assigned["basket_id"] = pd.NA
    basket_rows: list[dict[str, object]] = []
    next_basket_id = 1

    for (_, _), group in assigned.groupby(["strategy", "direction"], dropna=False, sort=True):
        current_indices: list[int] = []
        current_end = None
        for idx, row in group.iterrows():
            entry_time = row["entry_time"]
            exit_time = row["exit_time"]
            if current_end is None or entry_time > current_end:
                if current_indices:
                    next_basket_id = finalize_basket(assigned, basket_rows, current_indices, next_basket_id)
                current_indices = [idx]
                current_end = exit_time
            else:
                current_indices.append(idx)
                current_end = max(current_end, exit_time)
        if current_indices:
            next_basket_id = finalize_basket(assigned, basket_rows, current_indices, next_basket_id)

    assigned = assigned.sort_values("position_id").reset_index(drop=True)
    baskets = pd.DataFrame(basket_rows).sort_values("basket_id").reset_index(drop=True)
    return assigned, baskets


def finalize_basket(assigned: pd.DataFrame, basket_rows: list[dict[str, object]], indices: list[int], basket_id: int) -> int:
    assigned.loc[indices, "basket_id"] = basket_id
    group = assigned.loc[indices].copy()
    first_entry = group["entry_time"].min()
    last_entry = group["entry_time"].max()
    first_exit = group["exit_time"].min()
    last_exit = group["exit_time"].max()
    basket_rows.append(
        {
            "basket_id": basket_id,
            "strategy": group["strategy"].iloc[0],
            "T": group["T"].iloc[0] if "T" in group else None,
            "S": group["S"].iloc[0] if "S" in group else None,
            "direction": group["direction"].iloc[0],
            "position_count": int(len(group)),
            "total_volume": float(group["volume"].sum()),
            "pnl_est": float(group["pnl_est"].sum()),
            "first_entry_time": first_entry,
            "last_entry_time": last_entry,
            "first_exit_time": first_exit,
            "last_exit_time": last_exit,
            "holding_seconds": (last_exit - first_entry).total_seconds(),
            "max_layers": max_layers(group),
        }
    )
    return basket_id + 1


def max_layers(group: pd.DataFrame) -> int:
    events: list[tuple[pd.Timestamp, int]] = []
    for row in group.itertuples(index=False):
        events.append((row.entry_time, 1))
        events.append((row.exit_time, -1))
    active = 0
    peak = 0
    for _, delta in sorted(events, key=lambda item: (item[0], -item[1])):
        active += delta
        peak = max(peak, active)
    return int(peak)
