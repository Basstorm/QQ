from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from qq_research.robust_vectorbt_backtest import (
    align_close_to_features,
    build_backtest_report,
    build_edge_signals,
    evaluate_rule_mask,
    load_m15_close,
    run_vectorbt_backtest,
    select_robust_rule_variants,
    summarize_portfolio,
)

OUTPUTS = PROJECT / "outputs"
M15_CSV = PROJECT / "xauusd_m15_2016_2025.csv"
FEATURE_MATRIX = OUTPUTS / "expanded_indicator_feature_matrix.parquet"
SYNTHESIS_CSV = OUTPUTS / "strategy_rule_synthesis.csv"
BACKTEST_CSV = OUTPUTS / "robust_vectorbt_backtest.csv"
BACKTEST_MD = OUTPUTS / "robust_vectorbt_backtest.md"


def main() -> None:
    feature_frame = pd.read_parquet(FEATURE_MATRIX)
    synthesis = pd.read_csv(SYNTHESIS_CSV)
    close = align_close_to_features(load_m15_close(M15_CSV), feature_frame)
    price = close.dropna()
    variants = select_robust_rule_variants(synthesis)
    rows = []
    for variant in variants.itertuples(index=False):
        raw_mask = evaluate_rule_mask(feature_frame, variant.rule)
        mask = pd.Series(raw_mask.to_numpy(), index=close.index).loc[price.index]
        entries, exits = build_edge_signals(mask)
        portfolio = run_vectorbt_backtest(price, entries, exits)
        rows.append(summarize_portfolio(variant.strategy, variant.variant, variant.rule, mask, entries, exits, portfolio))
    results = pd.DataFrame(rows)
    results.to_csv(BACKTEST_CSV, index=False)
    BACKTEST_MD.write_text(build_backtest_report(results), encoding="utf-8")
    print("Wrote outputs/robust_vectorbt_backtest.csv")
    print("Wrote outputs/robust_vectorbt_backtest.md")


if __name__ == "__main__":
    main()
