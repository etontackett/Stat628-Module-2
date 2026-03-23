# Yield Analysis Report

- Generated at: 2026-03-22T20:23:13
- Outcome coding for paired summaries: all differences are `heat - control`.
- Primary model: mixed-effects model on row-level data.
- Long-term mixed model: fixed `cultivar * heat_trt`, random intercept `(1|cultivar:set_id)`.
- Acute mixed model: fixed `cultivar * heat_level * is_control`, random intercept `(1|cultivar:heat_level:replicate)`.

## Inputs
- cleaned_data/longterm_yield_analysis_locked.csv
- cleaned_data/acute_yield_analysis_locked.csv

## Key counts
- Long-term rows in yield model: 16
- Long-term pairs: 8
- Acute rows in yield model: 48
- Acute pairs: 24
- Acute pairs usable for later temperature models: 6

## Paired-summary quick check
- Long-term healthy weight summary:
  - overall: mean diff=-61.664, p=0.34048493770273314
  - MQ: mean diff=-125.912, p=0.294932692418296
  - St: mean diff=2.585, p=0.9710974326370292
- Long-term rotten-count proportion summary:
  - overall: mean diff=-0.03968, p=0.014648105351539811
  - MQ: mean diff=-0.03222, p=0.1320834101221743
  - St: mean diff=-0.04714, p=0.10646566452215074
- Acute healthy weight summary by heat level:
  - A: mean diff=-175.710, p=0.0487836132019266
  - B: mean diff=-64.003, p=0.5294503413510248
  - C: mean diff=-216.547, p=9.103429175884005e-05
  - D: mean diff=-165.075, p=0.235214951441294
  - MQ-A: mean diff=-225.693, p=0.15736493396753246
  - MQ-B: mean diff=-200.560, p=0.31976641000276007
  - MQ-C: mean diff=-249.870, p=0.003150206962065065
  - MQ-D: mean diff=-126.093, p=0.29802343159097533
  - St-A: mean diff=-125.727, p=0.3373756785999753
  - St-B: mean diff=72.553, p=0.3110781003792036
  - St-C: mean diff=-183.223, p=0.014484962285564555
  - St-D: mean diff=-204.057, p=0.5079464582634573
- Acute rotten-count proportion summary by heat level:
  - A: mean diff=0.12940, p=0.018006110513335286
  - B: mean diff=0.06941, p=0.023967828953087873
  - C: mean diff=0.08692, p=0.047632689905612625
  - D: mean diff=0.14532, p=0.06311408401321217
  - MQ-A: mean diff=0.11226, p=0.02650235984306656
  - MQ-B: mean diff=0.10348, p=0.08319235215773531
  - MQ-C: mean diff=0.15579, p=0.012478923947090853
  - MQ-D: mean diff=0.15308, p=0.17855615745971182
  - St-A: mean diff=0.14654, p=0.2071622831168456
  - St-B: mean diff=0.03533, p=0.11566332385563291
  - St-C: mean diff=0.01805, p=0.50077605611001
  - St-D: mean diff=0.13757, p=0.34985993236284685

## Mixed-model term tests
- Long-term smallest p by outcome:
  - healthy_weight_g: smallest term p=1.354e-05 (C(cultivar))
  - pct_rotten_count: smallest term p=0.03728 (C(heat_trt))
  - pct_rotten_weight: smallest term p=0.0007446 (C(cultivar))
- Acute smallest p by outcome:
  - healthy_weight_g: smallest term p=0.02449 (C(is_control))
  - pct_rotten_count: smallest term p=0.01831 (C(is_control))
  - pct_rotten_weight: smallest term p=0.07404 (C(is_control))

## Outputs
- results/yield/yield_longterm_summary.csv
- results/yield/yield_longterm_mixedlm_coefficients.csv
- results/yield/yield_longterm_mixedlm_wald_terms.csv
- results/yield/yield_acute_summary.csv
- results/yield/yield_acute_mixedlm_coefficients.csv
- results/yield/yield_acute_mixedlm_wald_terms.csv
- results/yield/yield_analysis_report.md
