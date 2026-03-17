# Yield Raw Data: check and cleaning report

## Input files
- /Users/liyuang/Desktop/STAT628/installment3/cranberry-data-group6/data_longterm/LTYielddata2024.csv
- /Users/liyuang/Desktop/STAT628/installment3/cranberry-data-group6/data_acute/Acute HS-Yield_RawData 2024.xlsx

## Cleaning rules
- Keep only data rows (remove title/header/blank rows).
- Normalize cultivar labels to `St` and `MQ`.
- Convert count/weight fields to numeric.
- Validate arithmetic consistency:
  - `rotten_count + healthy_count == total_count`
  - `rotten_weight_g + healthy_weight_g ~= total_weight_g` (tolerance 0.05 g)
- Derive `pct_rotten_count` and `pct_rotten_weight`.
- Acute experiment: parse control status from treatment label suffix `C`.
- Acute experiment: mark A0/A0C rows with `drop_a0=1` and provide a separate file with A0 removed.

## Long-term yield checks
- Data rows processed: 16
- Missing value issues: 0
- Arithmetic issues: 0
- Duplicate key issues (`cultivar+plot_id`): 0
- Pairing issues by set (`OTC` + `Control`): 0
- Output rows: 16

## Acute yield checks
- Data rows processed: 60
- Missing value issues: 0
- Arithmetic issues: 0
- Duplicate key issues (`cultivar+treatment_raw+replicate`): 0
- Pairing issues (`cultivar+replicate+heat_level` requires treatment+control): 0
- Output rows (`acute_yield_clean_all.csv`): 60
- Output rows (`acute_yield_clean.csv`, A0 removed): 48

## Output files
- /Users/liyuang/Desktop/STAT628/installment3/cleaned_data/longterm_yield_clean.csv
- /Users/liyuang/Desktop/STAT628/installment3/cleaned_data/acute_yield_clean_all.csv
- /Users/liyuang/Desktop/STAT628/installment3/cleaned_data/acute_yield_clean.csv
- /Users/liyuang/Desktop/STAT628/installment3/cleaned_data/yield_cleaning_report.md
