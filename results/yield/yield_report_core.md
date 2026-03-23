# Yield Report Core Draft

## Objective
This section evaluates whether heat treatment changes cranberry yield outcomes in the long-term and acute experiments. We analyze three outcomes separately: healthy fruit weight, rotten fruit proportion by count, and rotten fruit proportion by weight. The main question is whether heated plots differ from control plots, and whether those differences are consistent across experiment type and cultivar.

## Data and Methods
The yield analysis used the locked datasets after cleaning and pairing checks:

- `cleaned_data/longterm_yield_analysis_locked.csv`
- `cleaned_data/acute_yield_analysis_locked.csv`

We first summarized paired differences as `heat - control` to show the direction and rough magnitude of treatment effects. The primary inference used mixed-effects models because both experiments have grouped and paired structure.

- Long-term: outcome ~ cultivar * treatment, with set-level grouping
- Acute: outcome ~ cultivar * heat level * control status, with paired-unit grouping

## Long-Term Results
In the long-term experiment, treatment effects are present but mixed across outcomes. The mixed-effects regressions show significant treatment effects for healthy fruit weight, rotten-count proportion, and rotten-weight proportion, while cultivar effects are especially important for healthy fruit weight and rotten-weight proportion. However, the cultivar-by-treatment interaction is not strongly significant, so the long-term yield story is driven more by main effects than by strong cultivar-specific treatment responses.

Overall, long-term heated plots tend to have lower healthy fruit weight and somewhat lower rotten proportions than control plots.

### Long-Term Regression Summary
The primary long-term regression used a mixed-effects model for each outcome:

- `healthy_weight_g ~ cultivar * treatment`
- `pct_rotten_count ~ cultivar * treatment`
- `pct_rotten_weight ~ cultivar * treatment`

Key term-level Wald test results:

| Outcome | Significant terms | Interpretation |
| --- | --- | --- |
| `healthy_weight_g` | `cultivar` (`p = 1.35e-05`), `treatment` (`p = 0.0426`) | Long-term healthy fruit weight differs by cultivar and is lower under treatment overall. |
| `pct_rotten_count` | `treatment` (`p = 0.0373`) | Heated plots show a lower rotten-count proportion overall. |
| `pct_rotten_weight` | `cultivar` (`p = 7.45e-04`), `treatment` (`p = 0.0167`) | Rotten-weight proportion differs by cultivar and is lower under treatment overall. |

The cultivar-by-treatment interaction was not significant for any long-term yield outcome, so the main report emphasis should stay on the treatment and cultivar main effects rather than on cultivar-specific treatment responses.

![Long-term healthy fruit weight mean and standard error](/Users/liyuang/Desktop/STAT628/installment3/results/yield/figures/yield_longterm_healthy_weight_mean_se.png)

Figure 1. Observed long-term mean healthy fruit weight with standard errors by treatment and cultivar. This figure shows the raw group-level pattern before model-based adjustment.

Presentation note: MQ has much higher healthy fruit weight than St overall, and MQ drops under OTC. St changes very little from Control to OTC. So the visual pattern suggests both a strong cultivar difference and a treatment effect, which is consistent with the regression table below.

### Long-Term Regression Results

| Outcome | Cultivar p-value | Treatment p-value | Interaction p-value | Main takeaway |
| --- | ---: | ---: | ---: | --- |
| `healthy_weight_g` | `1.35e-05` | `0.0426` | `0.1434` | Healthy fruit weight differs by cultivar and is lower under treatment overall. |
| `pct_rotten_count` | `0.1458` | `0.0373` | `0.4952` | Rotten-count proportion is lower under treatment overall. |
| `pct_rotten_weight` | `7.45e-04` | `0.0167` | `0.1698` | Rotten-weight proportion differs by cultivar and is lower under treatment overall. |

The long-term interaction term was not significant for any of the three yield outcomes, so the main report emphasis should remain on the cultivar and treatment main effects.

![Long-term healthy weight regression diagnostics](/Users/liyuang/Desktop/STAT628/installment3/results/yield/figures/yield_longterm_diagnostics_healthy_weight_g.png)

Figure 2. Long-term regression diagnostics for `healthy_weight_g`. The left panel shows residuals versus fitted values, and the right panel shows the QQ plot. We use the healthy-weight model as the representative long-term diagnostic figure in the main report.

Presentation note: This diagnostic figure is not about treatment direction. It is there to show that the model is reasonably well behaved. We mainly want residuals to stay roughly centered around zero and the QQ points to stay reasonably close to the reference line.

## Acute Results
The acute experiment shows a clearer short-term stress pattern than the long-term experiment. In the paired summaries, heated plots usually have lower healthy fruit weight and higher rotten proportions than their matched controls. In the mixed-effects models, the most stable signal is the treatment-versus-control contrast itself. In contrast, the global heat-level terms and higher-order interactions are not strongly significant overall.

This supports the interpretation that acute heating acts mainly as a short-term stressor on yield.

### Acute Regression Summary
The primary acute regression also used mixed-effects models, with each outcome modeled as a function of cultivar, heat level, and control status:

- `healthy_weight_g ~ cultivar * heat_level * is_control`
- `pct_rotten_count ~ cultivar * heat_level * is_control`
- `pct_rotten_weight ~ cultivar * heat_level * is_control`

Key term-level Wald test results:

| Outcome | Significant terms | Interpretation |
| --- | --- | --- |
| `healthy_weight_g` | `is_control` (`p = 0.0245`) | Control plots retain more healthy fruit weight than heated plots. |
| `pct_rotten_count` | `is_control` (`p = 0.0183`) | Heated plots have higher rotten-count proportion than controls. |
| `pct_rotten_weight` | no term below `0.05`; `is_control` is borderline (`p = 0.0740`) | Rotten-weight proportion shows the same direction but weaker evidence. |

Across acute outcomes, the heat-level main effect and higher-order interaction terms were not strongly significant overall. That means the most stable acute regression signal is the treated-versus-control contrast itself, not a strong global difference among levels `A-D`.

![Acute healthy fruit weight mean and standard error](/Users/liyuang/Desktop/STAT628/installment3/results/yield/figures/yield_acute_healthy_weight_mean_se.png)

Figure 3. Observed acute mean healthy fruit weight with standard errors by heat level, control status, and cultivar. This figure illustrates the most interpretable acute outcome pattern: control plots generally retain more healthy fruit weight than heated plots.

Presentation note: In the acute experiment, the main visual pattern is that control plots usually sit above heated plots, especially for MQ. That is why the regression emphasizes the treated-versus-control contrast rather than a strong overall heat-level effect.

### Acute Regression Results

| Outcome | Cultivar p-value | Heat-level p-value | Control-vs-heated p-value | Highest-order interaction p-value | Main takeaway |
| --- | ---: | ---: | ---: | ---: | --- |
| `healthy_weight_g` | `0.7395` | `0.3563` | `0.0245` | `0.3767` | Control plots retain more healthy fruit weight than heated plots. |
| `pct_rotten_count` | `0.6777` | `0.5644` | `0.0183` | `0.3086` | Heated plots show higher rotten-count proportion than controls. |
| `pct_rotten_weight` | `0.9383` | `0.3146` | `0.0740` | `0.7025` | Rotten-weight proportion follows the same direction, but evidence is weaker. |

Across acute outcomes, the most stable regression signal is the control-versus-heated contrast rather than a strong global difference among heat levels `A-D`.

![Acute healthy weight regression diagnostics](/Users/liyuang/Desktop/STAT628/installment3/results/yield/figures/yield_acute_diagnostics_healthy_weight_g.png)

Figure 4. Acute regression diagnostics for `healthy_weight_g`. The left panel shows residuals versus fitted values, and the right panel shows the QQ plot. We use the healthy-weight model as the representative acute diagnostic figure in the main report.

Presentation note: This figure is only for model checking. The goal is to show that there is no major residual pattern and that the normality assumption is not badly violated.

## Conclusion
Overall, the yield analysis shows that heat treatment affects cranberry outcomes, but the pattern depends on experiment type. In the acute experiment, heat behaves like a short-term stressor: healthy fruit weight tends to fall and rotten proportions tend to rise. In the long-term experiment, treatment effects are still present, but the pattern is more mixed across outcomes and is also shaped by cultivar differences. Across both experiments, the most defensible report emphasis is the main treatment effect rather than a complex interaction story.
