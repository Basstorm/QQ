from __future__ import annotations

import numpy as np
import pandas as pd

ENTRY_CONTRAST_FEATURES = [
    "broker_entry_hour",
    "broker_entry_minute_mod_15",
    "m15_body_points",
    "m15_range_points",
    "m15_momentum_4_close_points",
    "m15_momentum_8_close_points",
    "m15_momentum_16_close_points",
    "m15_momentum_32_close_points",
    "m15_breakout_above_recent_high_8_points",
    "m15_breakout_below_recent_low_8_points",
    "m15_atr_14",
    "m15_range_atr_14_ratio",
    "m15_ema_8_slope_4",
    "m15_ema_21_slope_4",
    "m15_ema_50_slope_4",
    "m15_close_distance_to_ema_8",
    "m15_close_distance_to_ema_21",
    "m15_close_distance_to_ema_50",
    "m15_rsi_14",
    "m15_adx_14",
    "m15_dmp_14",
    "m15_dmn_14",
    "m15_macd_12_26_9",
    "m15_macd_hist_12_26_9",
    "entry_price_position_in_m15_range",
]

MANAGEMENT_CONTRAST_FEATURES = [
    "holding_minutes",
    "add_on_count",
    "position_count",
    "max_layers",
    "total_volume",
    "add_on_spacing_minutes_mean",
    "add_on_spacing_price_abs_mean",
    "close_span_minutes",
    "m1_mae_points",
    "m1_mfe_points",
    "m1_mae_atr_14",
    "m1_mfe_atr_14",
    "m1_time_to_mae_minutes",
    "m1_time_to_mfe_minutes",
]


def feature_contrast_table(df: pd.DataFrame, strategy: str, feature_columns: list[str], top_n: int = 12) -> pd.DataFrame:
    available = [column for column in feature_columns if column in df.columns]
    rows = []
    target = df[df["strategy"].eq(strategy)]
    rest = df[~df["strategy"].eq(strategy)]
    for feature in available:
        target_values = pd.to_numeric(target[feature], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
        rest_values = pd.to_numeric(rest[feature], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
        if len(target_values) == 0 or len(rest_values) == 0:
            continue
        pooled = pd.concat([target_values, rest_values])
        scale = pooled.quantile(0.75) - pooled.quantile(0.25)
        if not np.isfinite(scale) or scale == 0:
            scale = pooled.std()
        if not np.isfinite(scale) or scale == 0:
            continue
        target_median = float(target_values.median())
        rest_median = float(rest_values.median())
        rows.append(
            {
                "feature": feature,
                "target_median": target_median,
                "rest_median": rest_median,
                "delta": target_median - rest_median,
                "effect_size": abs((target_median - rest_median) / scale),
                "target_q25": float(target_values.quantile(0.25)),
                "target_q75": float(target_values.quantile(0.75)),
            }
        )
    if not rows:
        return pd.DataFrame(columns=["feature", "target_median", "rest_median", "delta", "effect_size", "target_q25", "target_q75"])
    return pd.DataFrame(rows).sort_values(["effect_size", "feature"], ascending=[False, True]).head(top_n).reset_index(drop=True)


def classify_candidate_family(medians: dict[str, float]) -> tuple[str, str, list[str]]:
    evidence: list[str] = []
    momentum = medians.get("m15_momentum_16_close_points", 0.0)
    breakout_up = medians.get("m15_breakout_above_recent_high_8_points", 0.0)
    breakout_down = medians.get("m15_breakout_below_recent_low_8_points", 0.0)
    ema_distance = medians.get("m15_close_distance_to_ema_21", 0.0)
    adx = medians.get("m15_adx_14", np.nan)
    rsi = medians.get("m15_rsi_14", np.nan)
    atr_ratio = medians.get("m15_range_atr_14_ratio", np.nan)

    if momentum > 0 and breakout_up > 0 and ema_distance > 0:
        evidence.extend(["positive M15 momentum", "above recent-high breakout", "close above EMA21"])
        if np.isfinite(adx) and adx >= 25:
            evidence.append("ADX trend strength")
        return "trend breakout / momentum continuation", "medium" if len(evidence) >= 3 else "low", evidence
    if momentum < 0 and breakout_down > 0 and ema_distance < 0:
        evidence.extend(["negative M15 momentum", "below recent-low breakout", "close below EMA21"])
        if np.isfinite(adx) and adx >= 25:
            evidence.append("ADX trend strength")
        return "downtrend breakout / short momentum continuation", "medium" if len(evidence) >= 3 else "low", evidence
    if np.isfinite(rsi) and rsi < 40 and momentum < 0:
        evidence.extend(["low RSI", "negative M15 momentum"])
        return "oversold pullback / downtrend continuation context", "low", evidence
    if np.isfinite(rsi) and rsi > 60 and momentum > 0:
        evidence.extend(["high RSI", "positive M15 momentum"])
        return "overbought momentum / trend continuation context", "low", evidence
    if np.isfinite(atr_ratio) and atr_ratio > 1.2:
        evidence.append("range above ATR context")
        return "volatility expansion context", "low", evidence
    return "mixed / insufficient compact-feature signal", "low", ["compact features do not isolate a clear entry archetype"]


def strategy_profile(strategy: str, deal_features: pd.DataFrame, basket_features: pd.DataFrame) -> dict[str, object]:
    entries = deal_features[deal_features["strategy"].eq(strategy) & deal_features["is_initial_entry"].astype(bool)]
    baskets = basket_features[basket_features["strategy"].eq(strategy)]
    entry_medians = numeric_medians(entries, ENTRY_CONTRAST_FEATURES)
    label, confidence, evidence = classify_candidate_family(entry_medians)
    return {
        "strategy": strategy,
        "initial_entries": int(len(entries)),
        "baskets": int(len(baskets)),
        "direction_mix": value_share(baskets, "direction"),
        "session_mix": value_share(entries, "broker_entry_session"),
        "pnl_est": float(baskets["pnl_est"].sum()) if "pnl_est" in baskets else np.nan,
        "avg_holding_minutes": float(baskets["holding_minutes"].mean()) if "holding_minutes" in baskets else np.nan,
        "avg_add_on_count": float(baskets["add_on_count"].mean()) if "add_on_count" in baskets else np.nan,
        "avg_mae_points": float(baskets["m1_mae_points"].mean()) if "m1_mae_points" in baskets else np.nan,
        "avg_mfe_points": float(baskets["m1_mfe_points"].mean()) if "m1_mfe_points" in baskets else np.nan,
        "candidate_family": label,
        "confidence": confidence,
        "evidence": evidence,
        "entry_medians": entry_medians,
        "entry_contrast": feature_contrast_table(deal_features[deal_features["is_initial_entry"].astype(bool)], strategy, ENTRY_CONTRAST_FEATURES),
        "management_contrast": feature_contrast_table(basket_features, strategy, MANAGEMENT_CONTRAST_FEATURES),
    }


def numeric_medians(df: pd.DataFrame, feature_columns: list[str]) -> dict[str, float]:
    medians: dict[str, float] = {}
    for feature in feature_columns:
        if feature in df.columns:
            values = pd.to_numeric(df[feature], errors="coerce").replace([np.inf, -np.inf], np.nan)
            if values.notna().any():
                medians[feature] = float(values.median())
    return medians


def value_share(df: pd.DataFrame, column: str, top_n: int = 4) -> str:
    if column not in df or df.empty:
        return "n/a"
    counts = df[column].value_counts(normalize=True).head(top_n)
    return ", ".join(f"{idx}:{value:.2f}" for idx, value in counts.items())


def build_strategy_profiles_report(deal_features: pd.DataFrame, basket_features: pd.DataFrame) -> str:
    strategies = sorted(basket_features["strategy"].dropna().unique())
    lines = [
        "# Phase 4 Approximate Strategy Profiles",
        "",
        "## Scope and Caution",
        "",
        "- These are approximate, evidence-based profiles from backtest behavior and reconstructed feature tables, not source-code recovery.",
        "- Entry inference uses `is_initial_entry == True` rows to avoid mixing add-ons with initial M15 signal context.",
        "- Compact features are used first. If a strategy remains ambiguous, use the expanded indicator/parameter discovery fallback described in the project plan.",
        "",
        "## Expanded indicator fallback",
        "",
        "- If compact features cannot explain an `Sxx`, search a broad public-indicator universe, not only common defaults.",
        "- Include MA crossover/stacking features and broad `pandas-ta`/compatible indicator families with parameter grids.",
        "",
    ]
    for strategy in strategies:
        profile = strategy_profile(strategy, deal_features, basket_features)
        lines.extend(strategy_profile_section(profile))
    return "\n".join(lines) + "\n"


def strategy_profile_section(profile: dict[str, object]) -> list[str]:
    entry_contrast = profile["entry_contrast"]
    management_contrast = profile["management_contrast"]
    return [
        f"## {profile['strategy']}",
        "",
        f"- Initial entries / baskets: `{profile['initial_entries']}` / `{profile['baskets']}`.",
        f"- Direction mix: {profile['direction_mix']}.",
        f"- Broker-session mix: {profile['session_mix']}.",
        f"- PnL estimate: `{profile['pnl_est']:.2f}`.",
        f"- Avg holding minutes: `{profile['avg_holding_minutes']:.2f}`; avg add-ons/basket: `{profile['avg_add_on_count']:.2f}`.",
        f"- Avg M1 MAE/MFE points: `{profile['avg_mae_points']:.2f}` / `{profile['avg_mfe_points']:.2f}`.",
        f"- Candidate family: **{profile['candidate_family']}**.",
        f"- Confidence: `{profile['confidence']}`.",
        f"- Evidence: {', '.join(profile['evidence'])}.",
        "",
        "### Entry-context differentiators",
        "",
        contrast_markdown(entry_contrast),
        "",
        "### Management differentiators",
        "",
        contrast_markdown(management_contrast),
        "",
        "### Uncertainty",
        "",
        "- This profile is descriptive and approximate. It may reflect shared basket management or market-regime effects rather than the exact EA entry rule.",
        "- If the differentiators are weak or inconsistent, run the expanded indicator/parameter discovery fallback for this `Sxx`.",
        "",
    ]


def contrast_markdown(contrast: pd.DataFrame) -> str:
    if contrast.empty:
        return "No stable differentiating feature found."
    rows = [
        "| Feature | Strategy median | Rest median | Delta | Effect | IQR band |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in contrast.head(8).itertuples(index=False):
        rows.append(
            f"| `{row.feature}` | {row.target_median:.3f} | {row.rest_median:.3f} | {row.delta:.3f} | {row.effect_size:.2f} | [{row.target_q25:.3f}, {row.target_q75:.3f}] |"
        )
    return "\n".join(rows)
