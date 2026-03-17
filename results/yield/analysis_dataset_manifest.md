# Analysis Dataset Manifest

- Generated at: 2026-03-05T15:34:42
- Lock version: `v1_2026-03-05`

## Inputs
- /Users/liyuang/Desktop/STAT628/installment3/cleaned_data/longterm_yield_clean.csv
- /Users/liyuang/Desktop/STAT628/installment3/cleaned_data/acute_yield_clean.csv
- /Users/liyuang/Desktop/STAT628/installment3/cleaned_data/yield_sensor_flags_longterm.csv
- /Users/liyuang/Desktop/STAT628/installment3/cleaned_data/yield_sensor_flags_acute.csv

## Locked outputs
- /Users/liyuang/Desktop/STAT628/installment3/cleaned_data/longterm_yield_analysis_locked.csv
- rows: 16
- include_in_yield_model=1 rows: 16
- include_in_temp_model=1 rows: 15
- sha256: `05cb0b2cf46dd51df6ebd874e2caf66d06d6298eb9d1fb6df0c1cfb066d6205b`

- /Users/liyuang/Desktop/STAT628/installment3/cleaned_data/acute_yield_analysis_locked.csv
- rows: 48
- include_in_yield_model=1 rows: 48
- include_in_temp_model=1 rows: 12
- sha256: `70929e9e22694802dab339cc909f3e85a6b98a79859efeb1c5e7c52c0b6a75b8`

## Notes
- `acute_yield_clean.csv` already excludes A0/A0C.
- `include_in_yield_model` keeps all rows in these locked files.
- `include_in_temp_model` excludes rows with sensor mapping/file/window issues.
