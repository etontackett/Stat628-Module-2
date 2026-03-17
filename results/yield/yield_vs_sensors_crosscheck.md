# Yield vs Sensor Cross-Check (4-channel + HOBO)

This report validates whether each yield row is supported by sensor metadata/files.

## Scope
- Yield files: long-term and acute (all rows + A0-removed subset).
- Sensor sources: 4 Channel + HOBO.
- Metadata source: Listofdates_HeatStressTreatments2024.xlsx, filtered to 2024 rows only.

## Summary
- Long-term yield rows checked: 16
- Acute yield rows checked (all): 60
- Acute yield rows checked (A0 removed): 48
- Long-term missing overview mappings: 1
- Long-term missing sensor files after mapping: 0
- Acute missing overview mappings: 2
- Acute missing sensor files after mapping: 28
- Acute rows with file present but no samples in treatment window: 22
- Overview anomalies (plot coding issues): 3
- Missing file references in overview (2024 rows): 68
- Filename resolution status counts (row-level): {'exact': 1305, 'alias': 48, 'unresolved': 139}
- Filename resolution output: /Users/liyuang/Desktop/STAT628/installment3/cleaned_data/sensor_filename_resolution.csv
- Row-level sensor flags output: /Users/liyuang/Desktop/STAT628/installment3/cleaned_data/yield_sensor_flags_longterm.csv, /Users/liyuang/Desktop/STAT628/installment3/cleaned_data/yield_sensor_flags_acute.csv

## Long-term missing overview mappings
- St plot OTC3 missing overview rows for 4 channel

## Long-term missing files
- None

## Acute missing overview mappings
- MQ BC rep2: missing overview (B3, HOBO sensor, Control 2)
- St BC rep2: missing overview (B3, HOBO sensor, Control 2)

## Acute missing files
- MQ A rep1: A4 HOBO sensor file not found
- MQ AC rep1: A4 HOBO sensor file not found
- MQ A rep2: A4 HOBO sensor file not found
- MQ AC rep2: A4 HOBO sensor file not found
- MQ A rep3: A4 HOBO sensor file not found
- MQ AC rep3: A4 HOBO sensor file not found
- MQ BC rep2: B1 4 channel file not found
- MQ D rep1: D1 4 channel file not found
- MQ D rep1: D1 HOBO sensor file not found
- MQ DC rep1: D1 HOBO sensor file not found
- MQ D rep2: D1 HOBO sensor file not found
- MQ DC rep2: D1 HOBO sensor file not found
- MQ D rep3: D1 HOBO sensor file not found
- MQ DC rep3: D1 HOBO sensor file not found
- St A rep1: A4 HOBO sensor file not found
- St AC rep1: A4 HOBO sensor file not found
- St A rep2: A4 HOBO sensor file not found
- St AC rep2: A4 HOBO sensor file not found
- St A rep3: A4 HOBO sensor file not found
- St AC rep3: A4 HOBO sensor file not found
- St BC rep2: B1 4 channel file not found
- St D rep1: D1 4 channel file not found
- St D rep1: D1 HOBO sensor file not found
- St DC rep1: D1 HOBO sensor file not found
- St D rep2: D1 HOBO sensor file not found
- St DC rep2: D1 HOBO sensor file not found
- St D rep3: D1 HOBO sensor file not found
- St DC rep3: D1 HOBO sensor file not found

## Acute missing in-window sensor data
- MQ A rep1: A2 HOBO sensor has no records inside window
- MQ A rep2: A3 HOBO sensor has no records inside window
- MQ B rep1: B1 HOBO sensor has no records inside window
- MQ BC rep1: B1 HOBO sensor has no records inside window
- MQ B rep2: B1 HOBO sensor has no records inside window
- MQ BC rep2: B1 HOBO sensor has no records inside window
- MQ B rep3: B1 HOBO sensor has no records inside window
- MQ B rep3: B3 HOBO sensor has no records inside window
- MQ BC rep3: B1 HOBO sensor has no records inside window
- St A rep1: A2 HOBO sensor has no records inside window
- St AC rep1: A1 HOBO sensor has no records inside window
- St A rep2: A1 HOBO sensor has no records inside window
- St AC rep2: A1 HOBO sensor has no records inside window
- St A rep3: A1 HOBO sensor has no records inside window
- St AC rep3: A1 HOBO sensor has no records inside window
- St B rep1: B1 HOBO sensor has no records inside window
- St BC rep1: B1 HOBO sensor has no records inside window
- St B rep2: B1 HOBO sensor has no records inside window
- St BC rep2: B1 HOBO sensor has no records inside window
- St B rep3: B1 HOBO sensor has no records inside window
- St B rep3: B3 HOBO sensor has no records inside window
- St BC rep3: B1 HOBO sensor has no records inside window

## Overview anomalies
- Acute unexpected plot index: test=C1 cultivar=MQ plot=Control 4
- Acute unexpected plot index: test=B2 cultivar=St plot=Control 4
- Acute unexpected plot index: test=B3 cultivar=St plot=Control 4

## Overview missing file references (sample)
- Acute | 4 channel | cultivar=MQ | test=B1 | plot=Control 2 | file=Set5_Acute20240807
- Acute | 4 channel | cultivar=St | test=B1 | plot=Control 2 | file=Set5_Acute20240807
- Acute | HOBO sensor | cultivar=MQ | test=C1 | plot=Control 4 | file=F 20240815
- Acute | HOBO sensor | cultivar=St | test=B2 | plot=Control 4 | file=F 20240822
- Acute | HOBO sensor | cultivar=St | test=B3 | plot=Control 4 | file=F 20240905
- Acute | 4 channel | cultivar=MQ | test=D1 | plot=OTC 1 | file=Set1_Acute20240918
- Acute | HOBO sensor | cultivar=MQ | test=D1 | plot=OTC 1 | file=A 20240918
- Acute | HOBO sensor | cultivar=MQ | test=D1 | plot=OTC 2 | file=E 20240918
- Acute | HOBO sensor | cultivar=MQ | test=D1 | plot=OTC 3 | file=C 20240918
- Acute | HOBO sensor | cultivar=MQ | test=D1 | plot=Control 1 | file=D 20240918
- Acute | HOBO sensor | cultivar=MQ | test=D1 | plot=Control 2 | file=OTCModel1 20240918
- Acute | HOBO sensor | cultivar=MQ | test=D1 | plot=Control 3 | file=F 20240918
- Acute | 4 channel | cultivar=St | test=D1 | plot=OTC 1 | file=Set1_Acute20240918
- Acute | HOBO sensor | cultivar=St | test=D1 | plot=OTC 1 | file=A 20240918
- Acute | HOBO sensor | cultivar=St | test=D1 | plot=OTC 2 | file=E 20240918
- Acute | HOBO sensor | cultivar=St | test=D1 | plot=OTC 3 | file=C 20240918
- Acute | HOBO sensor | cultivar=St | test=D1 | plot=Control 1 | file=D 20240918
- Acute | HOBO sensor | cultivar=St | test=D1 | plot=Control 2 | file=OTCModel1 20240918
- Acute | HOBO sensor | cultivar=St | test=D1 | plot=Control 3 | file=F 20240918
- Acute | HOBO sensor | cultivar=St | test=A4 | plot=OTC 1 | file=A 20240924
- Acute | HOBO sensor | cultivar=St | test=A4 | plot=OTC 2 | file=E 20240924
- Acute | HOBO sensor | cultivar=St | test=A4 | plot=OTC 3 | file=C 20240924
- Acute | HOBO sensor | cultivar=St | test=A4 | plot=Control 1 | file=D 20240924
- Acute | HOBO sensor | cultivar=St | test=A4 | plot=Control 2 | file=OTCModel1 20240924
- Acute | HOBO sensor | cultivar=St | test=A4 | plot=Control 3 | file=F 20240924
- Acute | HOBO sensor | cultivar=MQ | test=A4 | plot=OTC 1 | file=A 20240924
- Acute | HOBO sensor | cultivar=MQ | test=A4 | plot=OTC 2 | file=E 20240924
- Acute | HOBO sensor | cultivar=MQ | test=A4 | plot=OTC 3 | file=C 20240924
- Acute | HOBO sensor | cultivar=MQ | test=A4 | plot=Control 1 | file=D 20240924
- Acute | HOBO sensor | cultivar=MQ | test=A4 | plot=Control 2 | file=OTCModel1 20240924
- ... and 38 more
