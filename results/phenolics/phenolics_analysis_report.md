# Phenolics Analysis Report

- Generated at: 2026-03-22T22:56:15
- Outcome coding: all concentration differences are `heat - control`.
- Acute A0/A0C rows were excluded from the main treatment-effect analysis.
- Primary models: mixed-effects models on row-level mean concentration.

## Inputs
- cranberry-data-group6/data_mixed/Phenolics_RawData.xlsx

## Preprocessing summary
- Raw rows: 128
- True standards: 49
- Non-standard rows estimated: 79
- Parsed successfully: 79 / 79
- Std-like non-standard rows retained: 3

## Pair counts
- Long-term complete pairs: 8
- Acute complete pairs: 24

## Mixed-model findings
- Long-term concentration model: smallest term p=0.01648 (C(cultivar):C(treatment_raw))
- Acute concentration model: smallest term p=0.001152 (C(cultivar):C(is_control))

## Outputs
- results/phenolics/phenolics_longterm_summary.csv
- results/phenolics/phenolics_acute_summary.csv
- results/phenolics/phenolics_longterm_mixedlm_coefficients.csv
- results/phenolics/phenolics_acute_mixedlm_coefficients.csv
- results/phenolics/phenolics_longterm_mixedlm_wald_terms.csv
- results/phenolics/phenolics_acute_mixedlm_wald_terms.csv
- results/phenolics/figures/phenolics_longterm_distribution.png
- results/phenolics/figures/phenolics_longterm_mean_se.png
- results/phenolics/figures/phenolics_longterm_mixedlm_fitted_means.png
- results/phenolics/figures/phenolics_longterm_diagnostics_mean_concentration.png
- results/phenolics/figures/phenolics_acute_mean_se.png
- results/phenolics/figures/phenolics_acute_mixedlm_fitted_means.png
- results/phenolics/figures/phenolics_acute_diagnostics_mean_concentration.png
- results/phenolics/phenolics_analysis_report.md
