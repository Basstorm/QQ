from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from qq_research.expanded_indicator_discovery import (
    build_entry_label_frame,
    compute_indicator_feature_frame,
    discover_callable_indicator_names,
    normalize_m15,
    score_features_for_strategy,
)

OUTPUTS = PROJECT / "outputs"
M15_CSV = PROJECT / "xauusd_m15_2016_2025.csv"
BASKET_FEATURES = OUTPUTS / "basket_features.parquet"
FEATURE_MATRIX = OUTPUTS / "expanded_indicator_feature_matrix.parquet"
SCORES_CSV = OUTPUTS / "expanded_indicator_scores.csv"
REPORT_MD = OUTPUTS / "expanded_indicator_discovery_report.md"


def build_scores(feature_frame: pd.DataFrame, labels: pd.DataFrame) -> pd.DataFrame:
    score_frames = []
    for strategy in [column for column in labels.columns if column != "time"]:
        score_frames.append(score_features_for_strategy(feature_frame, labels[strategy], strategy, top_n=40, min_valid=100))
    return pd.concat(score_frames, ignore_index=True) if score_frames else pd.DataFrame()


def build_report(scores: pd.DataFrame, feature_frame: pd.DataFrame, labels: pd.DataFrame) -> str:
    callable_names = discover_callable_indicator_names()
    lines = [
        "# Expanded Indicator / Parameter Discovery Report",
        "",
        "## Scope",
        "",
        "- This is a broad first-pass search over public technical-indicator features using `pandas-ta-classic` plus explicit MA stacking/crossover features.",
        "- It scores each feature separately for each explicit `Sxx`, comparing that strategy's initial-entry M15 bars against the M15 background.",
        "- Positive counts are unique M15 bars with at least one initial basket entry for that `Sxx`; multiple entries on the same M15 bar collapse to one positive bar.",
        "- High AUC lift is evidence of separation, not proof of the exact EA rule. Combined multi-condition searches can build on these ranked candidates.",
        "",
        "## Indicator Universe Notes",
        "",
        f"- `pandas-ta-classic` exposes `{len(callable_names)}` lowercase callable names in this environment.",
        "- First-pass computed families include MA slope/distance/spread/stacking/cross, RSI, CCI, CMO, ROC, MOM, ADX/DMI, AROON, Bollinger Bands, Donchian, Keltner Channels, CHOP, Fisher, AO, BOP, CMF, and EFI.",
        "- This is intentionally broader than the compact Phase 4 feature set but still not exhaustive. The next pass can add more families from the callable universe.",
        "",
        "## Output Files",
        "",
        "- `outputs/expanded_indicator_feature_matrix.parquet`",
        "- `outputs/expanded_indicator_scores.csv`",
        "- `outputs/expanded_indicator_discovery_report.md`",
        "",
        "## Data Summary",
        "",
        f"- M15 feature rows: `{len(feature_frame)}`.",
        f"- Generated feature columns: `{feature_frame.shape[1] - 1}`.",
        "",
        "## Top Candidates by Strategy",
        "",
    ]
    for strategy in sorted(scores["strategy"].dropna().unique()):
        strategy_scores = scores[scores["strategy"].eq(strategy)].head(12)
        positives = int(labels[strategy].sum()) if strategy in labels else 0
        lines.extend(
            [
                f"### {strategy}",
                "",
                f"- Initial-entry positives: `{positives}`.",
                "",
                "| Feature | Direction | AUC | AUC lift | Positive median | Background median |",
                "|---|---|---:|---:|---:|---:|",
            ]
        )
        for row in strategy_scores.itertuples(index=False):
            lines.append(f"| `{row.feature}` | {row.direction} | {row.auc:.4f} | {row.auc_lift:.4f} | {row.positive_median:.4f} | {row.background_median:.4f} |")
        lines.append("")
    lines.extend(
        [
            "## Next Use",
            "",
            "- For low-confidence compact profiles, inspect top features here and build two/three-condition candidate rules per `Sxx`.",
            "- MA crossover/stacking features such as `ema_8_gt_ema_21`, `ema_8_cross_above_ema_21`, and bars-since-cross are included in the score table when they separate entries.",
            "- Treat all findings as hypotheses requiring false-positive/false-negative validation against non-entry M15 bars.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    OUTPUTS.mkdir(exist_ok=True)
    m15 = normalize_m15(pd.read_csv(M15_CSV))
    basket_features = pd.read_parquet(BASKET_FEATURES)
    start = pd.to_datetime(basket_features["entry_m15_time"]).min() - pd.Timedelta(days=30)
    end = pd.to_datetime(basket_features["entry_m15_time"]).max() + pd.Timedelta(days=1)
    m15 = m15[m15["time"].between(start, end)].reset_index(drop=True)
    feature_frame = compute_indicator_feature_frame(m15)
    labels = build_entry_label_frame(feature_frame["time"], basket_features)
    scores = build_scores(feature_frame, labels)
    feature_frame.to_parquet(FEATURE_MATRIX, index=False)
    scores.to_csv(SCORES_CSV, index=False)
    REPORT_MD.write_text(build_report(scores, feature_frame, labels), encoding="utf-8")
    print("Wrote outputs/expanded_indicator_feature_matrix.parquet")
    print("Wrote outputs/expanded_indicator_scores.csv")
    print("Wrote outputs/expanded_indicator_discovery_report.md")


if __name__ == "__main__":
    main()
