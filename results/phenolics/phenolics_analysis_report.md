# Phenolics Analysis Report

- Generated at: 2026-03-19T12:04:33
- Outcome coding: all concentration differences are `heat - control`.
- Acute A0/A0C rows were excluded from treatment-effect analysis.
- Primary models: mixed-effects models on row-level concentration data.

## Inputs
- /Users/liyuang/Desktop/STAT628/installment3/cranberry-data-group6/data_mixed/Phenolics_RawData.xlsx

## Calibration and concentration estimation
- Standards identified: 49
- Non-standard rows estimated: 79
- Std-like non-standard rows retained (e.g., STD1): 3

## Pair counts
- Long-term pairs: 8
- Acute complete pairs: 24
- Acute pairs missing one side: 0

## Paired-summary quick check
- Long-term concentration summary:
  - overall: mean diff=40.958, p=0.6847936480609327
  - MQ: mean diff=206.524, p=0.16573608585121863
  - St: mean diff=-124.608, p=0.3478302208766053
- Acute concentration summary by heat level:
  - A: mean diff=8.168, p=0.976260101929666
  - B: mean diff=-54.569, p=0.532404229275772
  - C: mean diff=-84.880, p=0.5431922642338567
  - D: mean diff=-150.905, p=0.1080037616224902
  - MQ-A: mean diff=-335.421, p=0.47060951720126454
  - MQ-B: mean diff=-129.546, p=0.12476515606984913
  - MQ-C: mean diff=14.932, p=0.9595526950755591
  - MQ-D: mean diff=-191.496, p=0.35704516137440456
  - St-A: mean diff=351.757, p=0.336217368046126
  - St-B: mean diff=20.407, p=0.9090404156380234
  - St-C: mean diff=-184.693, p=0.15349146034490715
  - St-D: mean diff=-110.313, p=0.13939842822214604

## Mixed-model findings
- Long-term concentration model: smallest term p=0.01648 (C(cultivar):C(treatment_raw))
- Acute concentration model: smallest term p=0.001152 (C(cultivar):C(is_control))

## Outputs
- /Users/liyuang/Desktop/STAT628/installment3/results/phenolics/phenolics_longterm_summary.csv
- /Users/liyuang/Desktop/STAT628/installment3/results/phenolics/phenolics_acute_summary.csv
- /Users/liyuang/Desktop/STAT628/installment3/results/phenolics/phenolics_longterm_mixedlm_coefficients.csv
- /Users/liyuang/Desktop/STAT628/installment3/results/phenolics/phenolics_acute_mixedlm_coefficients.csv
- /Users/liyuang/Desktop/STAT628/installment3/results/phenolics/phenolics_longterm_mixedlm_wald_terms.csv
- /Users/liyuang/Desktop/STAT628/installment3/results/phenolics/phenolics_acute_mixedlm_wald_terms.csv
- /Users/liyuang/Desktop/STAT628/installment3/results/phenolics/figures/phenolics_longterm_concentration_diff.png
- /Users/liyuang/Desktop/STAT628/installment3/results/phenolics/figures/phenolics_acute_concentration_diff_boxplot.png
- /Users/liyuang/Desktop/STAT628/installment3/results/phenolics/phenolics_analysis_report.md
