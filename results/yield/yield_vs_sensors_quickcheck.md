# Yield vs Sensors Quick Check (4-channel + HOBO)

Note: this is a mapping/existence consistency check using overview metadata + sensor file inventory (not a full signal-quality check).

## Rows checked
- Long-term yield rows: 16
- Acute yield rows (all): 60
- Acute yield rows (A0 removed): 48

## Main results
- Long-term missing overview mapping: 1
- Long-term missing mapped files: 0
- Acute missing overview mapping (A0 removed): 2
- Acute missing mapped files (A0 removed): 32

## Acute missing mapped files breakdown
- By sensor: {'HOBO sensor': 24, '4 channel': 8}
- By test window: {'A4': 12, 'B1': 6, 'D1': 14}
- By cultivar: {'MQ': 16, 'St': 16}

## Long-term issues
- Missing overview mapping: ('OTC3', '4 channel')
- No missing mapped files

## Acute missing overview mappings (A0 removed)
- ('MQ', 'BC', 2, 'B3', 'HOBO sensor', 'Control 2')
- ('St', 'BC', 2, 'B3', 'HOBO sensor', 'Control 2')

## Acute missing mapped files (first 30)
- ('MQ', 'A', 1, 'A4', 'HOBO sensor', 'OTC 1', 'A 20240924')
- ('MQ', 'AC', 1, 'A4', 'HOBO sensor', 'Control 1', 'D 20240924')
- ('MQ', 'A', 2, 'A4', 'HOBO sensor', 'OTC 2', 'E 20240924')
- ('MQ', 'AC', 2, 'A4', 'HOBO sensor', 'Control 2', 'OTCModel1 20240924')
- ('MQ', 'A', 3, 'A4', 'HOBO sensor', 'OTC 3', 'C 20240924')
- ('MQ', 'AC', 3, 'A4', 'HOBO sensor', 'Control 3', 'F 20240924')
- ('MQ', 'B', 2, 'B1', '4 channel', 'OTC 2', 'Set2_Acute20240807')
- ('MQ', 'BC', 2, 'B1', '4 channel', 'Control 2', 'Set5_Acute20240807')
- ('MQ', 'BC', 3, 'B1', '4 channel', 'Control 3', 'Set6_Acute20240807')
- ('MQ', 'D', 1, 'D1', '4 channel', 'OTC 1', 'Set1_Acute20240918')
- ('MQ', 'D', 1, 'D1', 'HOBO sensor', 'OTC 1', 'A 20240918')
- ('MQ', 'DC', 1, 'D1', 'HOBO sensor', 'Control 1', 'D 20240918')
- ('MQ', 'D', 2, 'D1', 'HOBO sensor', 'OTC 2', 'E 20240918')
- ('MQ', 'DC', 2, 'D1', 'HOBO sensor', 'Control 2', 'OTCModel1 20240918')
- ('MQ', 'D', 3, 'D1', 'HOBO sensor', 'OTC 3', 'C 20240918')
- ('MQ', 'DC', 3, 'D1', 'HOBO sensor', 'Control 3', 'F 20240918')
- ('St', 'A', 1, 'A4', 'HOBO sensor', 'OTC 1', 'A 20240924')
- ('St', 'AC', 1, 'A4', 'HOBO sensor', 'Control 1', 'D 20240924')
- ('St', 'A', 2, 'A4', 'HOBO sensor', 'OTC 2', 'E 20240924')
- ('St', 'AC', 2, 'A4', 'HOBO sensor', 'Control 2', 'OTCModel1 20240924')
- ('St', 'A', 3, 'A4', 'HOBO sensor', 'OTC 3', 'C 20240924')
- ('St', 'AC', 3, 'A4', 'HOBO sensor', 'Control 3', 'F 20240924')
- ('St', 'B', 2, 'B1', '4 channel', 'OTC 2', 'Set2_Acute20240807')
- ('St', 'BC', 2, 'B1', '4 channel', 'Control 2', 'Set5_Acute20240807')
- ('St', 'BC', 3, 'B1', '4 channel', 'Control 3', 'Set6_Acute20240807')
- ('St', 'D', 1, 'D1', '4 channel', 'OTC 1', 'Set1_Acute20240918')
- ('St', 'D', 1, 'D1', 'HOBO sensor', 'OTC 1', 'A 20240918')
- ('St', 'DC', 1, 'D1', 'HOBO sensor', 'Control 1', 'D 20240918')
- ('St', 'D', 2, 'D1', 'HOBO sensor', 'OTC 2', 'E 20240918')
- ('St', 'DC', 2, 'D1', 'HOBO sensor', 'Control 2', 'OTCModel1 20240918')
- ... and 2 more

## Overview anomalies (acute plot coding)
- ('unexpected_plot_index', 'C1', 'MQ', 'Control 4')
- ('unexpected_plot_index', 'B2', 'St', 'Control 4')
- ('unexpected_plot_index', 'B3', 'St', 'Control 4')