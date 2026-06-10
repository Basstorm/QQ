from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from qq_research.strategy_discovery import (
    add_cluster_assignments,
    build_cluster_report,
    choose_best_k,
    cluster_feature_summary,
    cluster_strategy_overlap,
    run_kmeans_sweep,
    select_clustering_features,
)

OUTPUTS = PROJECT / "outputs"
BASKET_FEATURES = OUTPUTS / "basket_features.parquet"
ASSIGNMENTS_PARQUET = OUTPUTS / "strategy_cluster_assignments.parquet"
REPORT_MD = OUTPUTS / "strategy_clusters_report.md"
DIAGNOSTICS_DIR = OUTPUTS / "cluster_diagnostics"


def build_phase3_outputs(basket_features: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, int, list[str]]:
    features = basket_features.copy()
    features["direction_sign"] = features["direction"].map({"long": 1, "short": -1})
    feature_columns = select_clustering_features(features)
    diagnostics, labels_by_k = run_kmeans_sweep(features, feature_columns)
    best_k = choose_best_k(diagnostics)
    assignments = add_cluster_assignments(features, labels_by_k, best_k)
    overlap = cluster_strategy_overlap(assignments, "cluster_best")
    feature_summary = cluster_feature_summary(features.assign(cluster_best=assignments["cluster_best"]), "cluster_best", feature_columns)
    return assignments, diagnostics, overlap, feature_summary, best_k, feature_columns


def write_outputs(
    assignments: pd.DataFrame,
    diagnostics: pd.DataFrame,
    overlap: pd.DataFrame,
    feature_summary: pd.DataFrame,
    best_k: int,
    feature_columns: list[str],
) -> None:
    OUTPUTS.mkdir(exist_ok=True)
    DIAGNOSTICS_DIR.mkdir(exist_ok=True)
    assignments.to_parquet(ASSIGNMENTS_PARQUET, index=False)
    diagnostics.to_csv(DIAGNOSTICS_DIR / "kmeans_diagnostics.csv", index=False)
    overlap.to_csv(DIAGNOSTICS_DIR / "best_cluster_strategy_overlap.csv", index=False)
    feature_summary.to_csv(DIAGNOSTICS_DIR / "best_cluster_feature_summary.csv", index=False)
    pd.Series(feature_columns, name="feature").to_csv(DIAGNOSTICS_DIR / "clustering_feature_columns.csv", index=False)
    report = build_cluster_report(assignments, diagnostics, overlap, best_k, feature_columns, feature_summary)
    REPORT_MD.write_text(report, encoding="utf-8")


def main() -> None:
    basket_features = pd.read_parquet(BASKET_FEATURES)
    assignments, diagnostics, overlap, feature_summary, best_k, feature_columns = build_phase3_outputs(basket_features)
    write_outputs(assignments, diagnostics, overlap, feature_summary, best_k, feature_columns)
    print("Wrote outputs/strategy_cluster_assignments.parquet")
    print("Wrote outputs/strategy_clusters_report.md")
    print("Wrote outputs/cluster_diagnostics/")


if __name__ == "__main__":
    main()
