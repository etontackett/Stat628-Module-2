#!/usr/bin/env python3
"""Run first-pass yield analysis on locked long-term and acute datasets."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats


ROOT = Path(__file__).resolve().parents[1]
CLEAN_DIR = ROOT / "cleaned_data"

LT_PATH = CLEAN_DIR / "longterm_yield_analysis_locked.csv"
ACUTE_PATH = CLEAN_DIR / "acute_yield_analysis_locked.csv"

LT_PAIR_PATH = CLEAN_DIR / "yield_longterm_pair_differences.csv"
LT_SUMMARY_PATH = CLEAN_DIR / "yield_longterm_summary.csv"
LT_COEF_PATH = CLEAN_DIR / "yield_longterm_model_coefficients.csv"

ACUTE_PAIR_PATH = CLEAN_DIR / "yield_acute_pair_differences.csv"
ACUTE_SUMMARY_PATH = CLEAN_DIR / "yield_acute_summary.csv"
ACUTE_COEF_PATH = CLEAN_DIR / "yield_acute_model_coefficients.csv"

REPORT_PATH = CLEAN_DIR / "yield_analysis_report.md"

OUTCOMES = ["healthy_weight_g", "pct_rotten_count", "pct_rotten_weight"]


def paired_ttest_table(
    df: pd.DataFrame,
    group_cols: list[str],
    outcomes: list[str],
) -> pd.DataFrame:
    rows = []
    grouped = [(("overall",), df)] if not group_cols else list(df.groupby(group_cols))
    for key, sub in grouped:
        if not isinstance(key, tuple):
            key = (key,)
        for outcome in outcomes:
            vals = sub[outcome].dropna().to_numpy()
            if len(vals) < 2:
                t_stat = np.nan
                p_value = np.nan
                se = np.nan
            else:
                t_stat, p_value = stats.ttest_1samp(vals, 0.0)
                se = vals.std(ddof=1) / np.sqrt(len(vals))
            row = {
                "outcome": outcome,
                "n_pairs": int(len(vals)),
                "mean_diff_heat_minus_control": float(np.nanmean(vals)) if len(vals) else np.nan,
                "sd_diff": float(np.nanstd(vals, ddof=1)) if len(vals) > 1 else np.nan,
                "se_diff": se,
                "t_stat": t_stat,
                "p_value": p_value,
            }
            for col, value in zip(group_cols, key):
                row[col] = value
            rows.append(row)
    cols = group_cols + [
        "outcome",
        "n_pairs",
        "mean_diff_heat_minus_control",
        "sd_diff",
        "se_diff",
        "t_stat",
        "p_value",
    ]
    return pd.DataFrame(rows)[cols]


def coefficient_table(model, outcome: str, model_name: str) -> pd.DataFrame:
    ci = model.conf_int()
    out = pd.DataFrame(
        {
            "model_name": model_name,
            "outcome": outcome,
            "term": model.params.index,
            "estimate": model.params.values,
            "std_error": model.bse.values,
            "t_value": model.tvalues.values,
            "p_value": model.pvalues.values,
            "ci_low": ci[0].values,
            "ci_high": ci[1].values,
            "n_obs": int(model.nobs),
            "r_squared": getattr(model, "rsquared", np.nan),
        }
    )
    return out


def build_longterm_pairs(df: pd.DataFrame) -> pd.DataFrame:
    keep = df[df["include_in_yield_model"] == 1].copy()
    idx = ["cultivar", "set_id"]
    values = ["healthy_weight_g", "pct_rotten_count", "pct_rotten_weight", "plot_id"]
    wide = keep.pivot(index=idx, columns="heat_trt", values=values)
    wide.columns = [f"{v}_{k.lower()}" for v, k in wide.columns]
    wide = wide.reset_index()
    wide["healthy_weight_diff"] = wide["healthy_weight_g_otc"] - wide["healthy_weight_g_control"]
    wide["pct_rotten_count_diff"] = wide["pct_rotten_count_otc"] - wide["pct_rotten_count_control"]
    wide["pct_rotten_weight_diff"] = wide["pct_rotten_weight_otc"] - wide["pct_rotten_weight_control"]
    return wide


def build_acute_pairs(df: pd.DataFrame) -> pd.DataFrame:
    keep = df[df["include_in_yield_model"] == 1].copy()
    idx = ["cultivar", "heat_level", "replicate"]
    values = [
        "healthy_weight_g",
        "pct_rotten_count",
        "pct_rotten_weight",
        "include_in_temp_model",
        "sensor_missing_overview",
        "sensor_missing_files",
        "sensor_missing_window",
    ]
    wide = keep.pivot(index=idx, columns="is_control", values=values)
    wide.columns = [
        f"{v}_{'control' if int(k) == 1 else 'heat'}" for v, k in wide.columns
    ]
    wide = wide.reset_index()
    wide["healthy_weight_diff"] = wide["healthy_weight_g_heat"] - wide["healthy_weight_g_control"]
    wide["pct_rotten_count_diff"] = wide["pct_rotten_count_heat"] - wide["pct_rotten_count_control"]
    wide["pct_rotten_weight_diff"] = wide["pct_rotten_weight_heat"] - wide["pct_rotten_weight_control"]
    wide["temp_model_usable_pair"] = (
        (wide["include_in_temp_model_heat"] == 1)
        & (wide["include_in_temp_model_control"] == 1)
    ).astype(int)
    return wide


def main() -> None:
    lt = pd.read_csv(LT_PATH)
    acute = pd.read_csv(ACUTE_PATH)

    lt["include_in_yield_model"] = lt["include_in_yield_model"].astype(int)
    lt["include_in_temp_model"] = lt["include_in_temp_model"].astype(int)
    acute["include_in_yield_model"] = acute["include_in_yield_model"].astype(int)
    acute["include_in_temp_model"] = acute["include_in_temp_model"].astype(int)
    acute["sensor_missing_overview"] = acute["sensor_missing_overview"].astype(int)
    acute["sensor_missing_files"] = acute["sensor_missing_files"].astype(int)
    acute["sensor_missing_window"] = acute["sensor_missing_window"].astype(int)

    lt_pairs = build_longterm_pairs(lt)
    acute_pairs = build_acute_pairs(acute)

    lt_pairs.to_csv(LT_PAIR_PATH, index=False)
    acute_pairs.to_csv(ACUTE_PAIR_PATH, index=False)

    lt_summary = paired_ttest_table(
        lt_pairs.rename(
            columns={
                "healthy_weight_diff": "healthy_weight_g",
                "pct_rotten_count_diff": "pct_rotten_count",
                "pct_rotten_weight_diff": "pct_rotten_weight",
            }
        ),
        ["cultivar"],
        OUTCOMES,
    )
    lt_overall = paired_ttest_table(
        lt_pairs.rename(
            columns={
                "healthy_weight_diff": "healthy_weight_g",
                "pct_rotten_count_diff": "pct_rotten_count",
                "pct_rotten_weight_diff": "pct_rotten_weight",
            }
        ),
        [],
        OUTCOMES,
    )
    lt_summary = pd.concat([lt_overall, lt_summary], ignore_index=True, sort=False)
    lt_summary.to_csv(LT_SUMMARY_PATH, index=False)

    acute_summary = paired_ttest_table(
        acute_pairs.rename(
            columns={
                "healthy_weight_diff": "healthy_weight_g",
                "pct_rotten_count_diff": "pct_rotten_count",
                "pct_rotten_weight_diff": "pct_rotten_weight",
            }
        ),
        ["cultivar", "heat_level"],
        OUTCOMES,
    )
    acute_overall = paired_ttest_table(
        acute_pairs.rename(
            columns={
                "healthy_weight_diff": "healthy_weight_g",
                "pct_rotten_count_diff": "pct_rotten_count",
                "pct_rotten_weight_diff": "pct_rotten_weight",
            }
        ),
        ["heat_level"],
        OUTCOMES,
    )
    acute_summary = pd.concat([acute_overall, acute_summary], ignore_index=True, sort=False)
    acute_summary.to_csv(ACUTE_SUMMARY_PATH, index=False)

    lt_models = []
    for outcome in ["healthy_weight_diff", "pct_rotten_count_diff", "pct_rotten_weight_diff"]:
        model = smf.ols(f"{outcome} ~ C(cultivar)", data=lt_pairs).fit()
        lt_models.append(coefficient_table(model, outcome, "longterm_pair_diff"))
    pd.concat(lt_models, ignore_index=True).to_csv(LT_COEF_PATH, index=False)

    acute_models = []
    for outcome in ["healthy_weight_diff", "pct_rotten_count_diff", "pct_rotten_weight_diff"]:
        model = smf.ols(f"{outcome} ~ C(heat_level) * C(cultivar)", data=acute_pairs).fit()
        acute_models.append(coefficient_table(model, outcome, "acute_pair_diff"))
    pd.concat(acute_models, ignore_index=True).to_csv(ACUTE_COEF_PATH, index=False)

    lt_hw = lt_summary[lt_summary["outcome"] == "healthy_weight_g"].copy()
    lt_rot = lt_summary[lt_summary["outcome"] == "pct_rotten_count"].copy()
    acute_hw = acute_summary[acute_summary["outcome"] == "healthy_weight_g"].copy()
    acute_rot = acute_summary[acute_summary["outcome"] == "pct_rotten_count"].copy()

    report_lines = [
        "# Yield Analysis Report",
        "",
        f"- Generated at: {datetime.now().isoformat(timespec='seconds')}",
        "- Outcome coding: all differences are `heat - control`.",
        "- Long-term unit of analysis: paired set difference within cultivar/set.",
        "- Acute unit of analysis: paired difference within cultivar/heat level/replicate.",
        "",
        "## Inputs",
        f"- {LT_PATH}",
        f"- {ACUTE_PATH}",
        "",
        "## Key counts",
        f"- Long-term rows in yield model: {int(lt['include_in_yield_model'].sum())}",
        f"- Long-term pairs: {len(lt_pairs)}",
        f"- Acute rows in yield model: {int(acute['include_in_yield_model'].sum())}",
        f"- Acute pairs: {len(acute_pairs)}",
        f"- Acute pairs usable for later temperature models: {int(acute_pairs['temp_model_usable_pair'].sum())}",
        "",
        "## First-pass findings",
        "- Long-term healthy weight summary:",
    ]
    for _, row in lt_hw.fillna("").iterrows():
        label = row["cultivar"] if row.get("cultivar", "") else "overall"
        report_lines.append(
            f"  - {label}: mean diff={row['mean_diff_heat_minus_control']:.3f}, p={row['p_value'] if row['p_value'] != '' else np.nan}"
        )
    report_lines.append("- Long-term rotten-count proportion summary:")
    for _, row in lt_rot.fillna("").iterrows():
        label = row["cultivar"] if row.get("cultivar", "") else "overall"
        report_lines.append(
            f"  - {label}: mean diff={row['mean_diff_heat_minus_control']:.5f}, p={row['p_value'] if row['p_value'] != '' else np.nan}"
        )
    report_lines.append("- Acute healthy weight summary by heat level:")
    for _, row in acute_hw.fillna("").iterrows():
        label = (
            f"{row['cultivar']}-{row['heat_level']}"
            if row.get("cultivar", "") and row.get("heat_level", "")
            else row.get("heat_level", "overall")
        )
        report_lines.append(
            f"  - {label}: mean diff={row['mean_diff_heat_minus_control']:.3f}, p={row['p_value'] if row['p_value'] != '' else np.nan}"
        )
    report_lines.append("- Acute rotten-count proportion summary by heat level:")
    for _, row in acute_rot.fillna("").iterrows():
        label = (
            f"{row['cultivar']}-{row['heat_level']}"
            if row.get("cultivar", "") and row.get("heat_level", "")
            else row.get("heat_level", "overall")
        )
        report_lines.append(
            f"  - {label}: mean diff={row['mean_diff_heat_minus_control']:.5f}, p={row['p_value'] if row['p_value'] != '' else np.nan}"
        )
    report_lines.extend(
        [
            "",
            "## Outputs",
            f"- {LT_PAIR_PATH}",
            f"- {LT_SUMMARY_PATH}",
            f"- {LT_COEF_PATH}",
            f"- {ACUTE_PAIR_PATH}",
            f"- {ACUTE_SUMMARY_PATH}",
            f"- {ACUTE_COEF_PATH}",
            f"- {REPORT_PATH}",
            "",
        ]
    )

    REPORT_PATH.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"Wrote: {LT_PAIR_PATH}")
    print(f"Wrote: {LT_SUMMARY_PATH}")
    print(f"Wrote: {LT_COEF_PATH}")
    print(f"Wrote: {ACUTE_PAIR_PATH}")
    print(f"Wrote: {ACUTE_SUMMARY_PATH}")
    print(f"Wrote: {ACUTE_COEF_PATH}")
    print(f"Wrote: {REPORT_PATH}")


if __name__ == "__main__":
    main()
