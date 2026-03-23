# Phenolics Report Core Draft

## Objective
This section evaluates whether heat treatment changes cranberry phenolics concentration in the long-term and acute experiments. We focus on gallic-acid-equivalent concentration as the outcome and compare how the treatment effect changes across cultivar and experiment type.

## Data and Methods
Phenolics analysis started from raw absorbance measurements in `cranberry-data-group6/data_mixed/Phenolics_RawData.xlsx`. The preprocessing pipeline had four essential steps:

1. Identify true standards and fit calibration lines separately for each date and lab replicate.
2. Convert non-standard absorbance readings into estimated concentration values.
3. Parse `Sample ID` to recover experiment type, cultivar, treatment status, heat level, and replicate.
4. Exclude acute `A0/A0C` rows from the main treatment-effect analysis.

Primary inference used mixed-effects regression on row-level mean concentration.

## Long-Term Results
In the long-term experiment, the most important result is the cultivar-by-treatment interaction. The observed mean plot already suggests this pattern: OTC increases concentration for `MQ` but decreases concentration for `St`.

![Long-term mean concentration](/Users/liyuang/Desktop/STAT628/installment3/results/phenolics/figures/phenolics_longterm_mean_se.png)

Figure 1. Observed long-term mean phenolics concentration with standard errors by treatment and cultivar.

Presentation note: `MQ` rises from Control to OTC, while `St` falls from Control to OTC. So the main long-term story is not a single average treatment effect; it is that the treatment response depends on cultivar.

### Long-Term Regression Results

| Term | p-value | Interpretation |
| --- | ---: | --- |
| `cultivar` | `0.0678` | Marginal evidence of baseline cultivar difference. |
| `treatment` | `0.0344` | OTC changes concentration overall. |
| `cultivar × treatment` | `0.0165` | The treatment effect differs across cultivars. |

Coefficient interpretation:

- For `MQ`, the estimated OTC effect is `+206.5`.
- For `St`, the estimated OTC effect is `206.5 - 331.1 = -124.6`.

Main takeaway: long-term phenolics shows a cultivar-specific treatment response. OTC increases concentration in `MQ` but decreases it in `St`.

![Long-term regression diagnostics](/Users/liyuang/Desktop/STAT628/installment3/results/phenolics/figures/phenolics_longterm_diagnostics_mean_concentration.png)

Figure 2. Long-term regression diagnostics for mean concentration. The left panel shows residuals versus fitted values, and the right panel shows the QQ plot.

Presentation note: This figure is for model checking rather than treatment interpretation. We mainly want residuals to stay roughly centered around zero and the QQ points to stay reasonably close to the reference line.

## Acute Results
In the acute experiment, the response is more complex than in long-term. The observed mean plot shows that heated-versus-control differences change across both cultivar and heat level.

![Acute mean concentration](/Users/liyuang/Desktop/STAT628/installment3/results/phenolics/figures/phenolics_acute_mean_se.png)

Figure 2. Observed acute mean phenolics concentration with standard errors by heat level, treatment status, and cultivar.

Presentation note: For `MQ`, control is usually above heated, especially at `A` and `D`. For `St`, the pattern changes by heat level: heated is higher at `A`, similar at `B`, and lower at `C` and `D`. This is why the acute model is mainly an interaction story.

### Acute Regression Results

| Term | p-value | Interpretation |
| --- | ---: | --- |
| `heat_level` | `0.1016` | No strong global heat-level main effect. |
| `cultivar` | `0.1264` | No strong global cultivar main effect. |
| `is_control` | `0.0248` | Heated and control plots differ overall. |
| `cultivar × is_control` | `0.00115` | The heated-versus-control contrast differs across cultivars. |
| `heat_level × cultivar × is_control` | `0.0265` | The cultivar-specific treatment effect changes across heat levels. |

Main takeaway: acute phenolics does not show one simple treatment effect. Instead, the treatment effect depends on both cultivar and heat level.

![Acute regression diagnostics](/Users/liyuang/Desktop/STAT628/installment3/results/phenolics/figures/phenolics_acute_diagnostics_mean_concentration.png)

Figure 4. Acute regression diagnostics for mean concentration. The left panel shows residuals versus fitted values, and the right panel shows the QQ plot.

Presentation note: This figure is also for model checking. The goal is to show that there is no major residual pattern and that the normality assumption is not badly violated.

## Conclusion
Across both experiments, phenolics is mainly an interaction-driven outcome. In the long-term experiment, OTC has opposite effects for `MQ` and `St`. In the acute experiment, the heated-versus-control contrast changes across both cultivar and heat level. This means the biologically important result is not just whether heat matters on average, but how the phenolics response depends on context.
