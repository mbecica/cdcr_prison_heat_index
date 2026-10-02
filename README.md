# CDCR Prison Heat Index

A relative heat risk index for 31 California Department of Corrections and Rehabilitation (CDCR) adult prisons, for a current and a mid-century (2041–2070) climate. It combines projected heat and air quality hazard, indoor heat exposure, and the health and demographic vulnerability of each prison's population. The index is published as the [Prison Heat Index](https://marybecica.com/prison-heat-index/); its [methodology page](https://marybecica.com/prison-heat-index/methodology/) presents the same method for a general audience, with validation against indoor temperature records.

Inputs come from two related repositories: [ca_prison_climate_justice](https://github.com/mbecica/ca_prison_climate_justice) (facility locations and climate hazards) and [cdcr_facility_data](https://github.com/mbecica/cdcr_facility_data) (population, health care, and cooling data).

## Outputs

| File | Contents |
| :--- | :--- |
| `data/CDCR_heat_risk_index_additive_25_25_50.csv` | Component scores, risk score, and risk tier for each prison and period, with the input values behind them |
| `data/CDCR_heat_risk_sensitivity.csv` | Mid-century scores and ranks under three weighting schemes, with the Vulnerable Communities Platform comparison |
| `data/CDCR_heat_risk_index_multiplicative.csv` | The index under an alternate multiplicative formulation (H × E × V) |
| `data/heat_risk_inputs.csv` | Every input to the index, one row per prison |
| `app_export/output/prison_heat_index.json`, `prison_boundaries.geojson` | Data for the Prison Heat Index website |
| `gridmet/data/` | Observed daily maximum temperatures and heat threshold counts at each prison, 2016–2025 |
| `data/archive/`, `app_export/output/archive/` | Earlier versions of the index outputs |

## Framework

Risk = 0.25 × Hazard + 0.25 × Exposure + 0.50 × Vulnerability, following Ovienmhada et al. (2024). Each component is an equal-weight average of sub-indicators, each min-max normalized to 0–1 across the 31 prisons. The final score is divided by its maximum across both periods and scaled to 0–100, so the two periods share one scale and the lowest-risk prison keeps a positive score.

Vulnerability is double-weighted because cooling in prisons is controlled by staff, who withhold air conditioning, water, and shade as punishment (Brunn et al., 2025). The additive form keeps a prison with full mechanical air conditioning from scoring zero, so the index answers where people are most at risk if cooling fails. Under a multiplicative form, CHCF, which has the highest vulnerability in the system and no indoor heat days, would score zero.

Adaptive capacity is not a separate component. Following Ovienmhada et al. (2024), incarcerated people are treated as having effectively no adaptive capacity: they cannot relocate, buy cooling, choose their housing, or leave during a heat event.

Exposure and vulnerability use 2025 values in both periods; only the hazard changes.

### Hazard

A hot-day term and a warm-night term are each divided by their maximum across the 31 prisons and both periods, averaged, and multiplied by an air quality modifier. Counts come from a LOCA2-CA daily extraction at each prison's grid cell (14 models, each weighted equally; SSP3-7.0), documented in ca_prison_climate_justice. The current period uses the 1981–2010 model climate.

| Sub-indicator | Variable | Description | Source |
| :--- | :--- | :--- | :--- |
| Hot days | `loca2_days_over_avg_plus10`, `loca2_days_over_90` | Equal blend of days above the prison's mean summer daily maximum plus 10°F (1981–2010 baseline) and days above 90°F, each scaled to its maximum before blending | LOCA2-CA daily (SSP3-7.0), Cal-Adapt |
| Warm nights | `loca2_nights_over_p95` | April–October nights above the 95th percentile of the prison's 1961–1990 April–October minimum temperatures (OEHHA convention) | LOCA2-CA daily (SSP3-7.0), Cal-Adapt |
| Air quality | `AQI_norm` | Multiplier `1 + 0.30 × AQI_norm/100`, held at current values in both periods. `AQI_norm` is the mean of the CalEnviroScreen ozone, PM2.5, and diesel percentiles. | CalEnviroScreen 5.0, 2025 |

The 0.30 air quality coefficient and the 50% hot-day blend weight are design parameters; the sensitivity notebook sweeps both.

### Exposure

| Sub-indicator | Variable | Description | Source |
| :--- | :--- | :--- | :--- |
| Indoor 78°F days | `days_indoor_above_78f_2025` | Days in May–October 2025 with indoor temperatures above 78°F, the lower bound of CDCR's Stage I heat activation. Where the report gives housing-unit values, they are combined to a facility value. | CDCR Air Cooling Pilot Supplemental Report, Jan 2026 |
| Indoor/outdoor ratio | `ratio_indoor_to_outdoor` | Indoor 78°F days divided by outdoor 78°F days (gridMET daily maximum, May–October 2025): how much a prison's buildings amplify or damp outdoor heat. PBSP's ratio (15.75) reflects about four outdoor 78°F days a year on the Crescent City coast and is kept uncapped. | CDCR report and gridMET |
| Urban heat island | `uhi_normalized` | Benz & Burney (2021) surface heat island anomaly, with negative values set to 0 and divided by the maximum across the 31 prisons (CIM, 7.247°C). CCI and PVSP have no value and take the mean. | Benz & Burney (2021) |
| No air conditioning | `1 − pct_hu_mechanical` | Share of housing units without mechanical cooling. Evaporative cooling and ventilation both count as no air conditioning. | CDCR Air Cooling Pilot Supplemental Report, Jan 2026 |

### Vulnerability

| Sub-indicator | Variable | Description | Source |
| :--- | :--- | :--- | :--- |
| Medical acuity | `medical_acuity` | Share of the population in CCHCS High Risk Priority 1, Priority 2, or Medium Risk tiers, which capture chronic and acute conditions that raise heat sensitivity | CCHCS dashboard, 2025 |
| Age 50+ | `cchcs_age_over_50_pct_2025` | Share aged 50 or older, the threshold used in research on accelerated aging in prison | CCHCS dashboard, 2025 |
| Mental health | `cchcs_mental_health_eop_pct_2025` | Share in the Enhanced Outpatient Program, a proxy for psychotropic medications that impair thermoregulation | CCHCS dashboard, 2025 |
| Disability | `cchcs_dpp_pct_2025` | Share in the Disability Placement Program: mobility, vision, hearing, and other impairments that limit response to heat | CCHCS dashboard, 2025 |
| Race | `race_peopleofcolor_pct` | Share identifying as people of color, following Ovienmhada et al. (2024) | CDCR Population Data Set, 2025 |
| Gender | `gender_female_pct` | Share of women; women's prisons differ in medical infrastructure, and pregnancy and reproductive health conditions add heat sensitivity | CDCR Population Data Set, 2025 |

### Variables not scored

These are carried in the output as descriptive columns where data exists.

- **Restricted housing (`rhu_pct_2025`).** People in restricted housing average about one hour out of cell a day and cannot move to cooler areas, and Cloud et al. (2023) identify solitary confinement as a heat vulnerability factor. No study quantifies its heat health effect relative to the general prison population, so an equal-weight sub-indicator cannot be justified. Two outliers (COR 13.6%, SAC 12.7%) would also dominate a min-max scaled term.
- **Capacity utilization (`capacity_percent_2025`).** Crowding limits ventilation and movement, but in testing it did not explain indoor/outdoor ratio variance beyond air conditioning (OLS coefficient 0.002, p = 0.60) and did not change any clustering assignment. The indoor temperature data appears to capture its effect.
- **Security level.** Did not explain indoor/outdoor ratio variance (OLS coefficient −0.081, p = 0.68).
- **Isolation (`dist_nearest_medical_mi`, `in_urban_area_2020`).** Abdala et al. (2023) identify distance from hospitals as a vulnerability factor, but among these prisons the median distance to the nearest medical facility is 0.52 miles and the maximum 1.51 miles (KVSP), too little variation to rank on.
- **Work assignments.** Kitchen, laundry, and outdoor work add heat exposure; days above 80°F raise workplace injury risk by 3% and days above 90°F by 10% (Alahmad et al., 2025). Facility-level work assignment rates are not public.
- **Psychotropic medication.** Facility-level prescription rates are not public; Enhanced Outpatient Program enrollment and the CCHCS risk tiers stand in for them.

## Scoring and tiers

Scores are classified into four tiers (Highest, High, Moderate, Lowest) by Jenks natural breaks (k = 4), computed separately for each period. A tier is relative within its period: "Highest" in the current period is a lower absolute risk than "Highest" at mid-century, and the absolute change between periods is carried by the score. Because exposure and vulnerability are constant and the hazard spread is narrower in the current period, a prison high on exposure and vulnerability (RJD, PBSP) can sit a tier higher in the current period than at mid-century even though its score rises.

The tiers rank prisons against each other. All incarcerated people face elevated heat risk compared with the general population, and a lower tier does not mean a prison is safe.

## Sensitivity analysis

`index/sensitivity_analysis.ipynb` compares mid-century rankings under three weightings: equal multiplicative (H × E × V), the additive 25/25/50 default, and multiplicative with vulnerability squared (H × E × V²). Spearman rank correlations are 0.90 (equal multiplicative vs. additive), 0.95 (equal multiplicative vs. V²), and 0.97 (additive vs. V²). CHCF moves the most, from 26th under equal multiplicative weighting to 9th under the additive default, because its medical complexity drives vulnerability despite full air conditioning. The notebook also sweeps the air quality coefficient and hot-day blend weight.

For comparison, the sensitivity file includes the VCP `ExHeatHealth_Idx` for the census tracts around each prison with group-quarters population of 25% or less. Its Spearman correlation with this index is −0.17.

## Observed temperatures

`gridmet/` extracts observed daily maximum temperatures at each prison from gridMET (4 km, Abatzoglou 2013). The 2025 May–October counts supply the outdoor half of the exposure ratio. All 34 CDCR institutions are covered for every year, including those that have since closed.

| File | Contents | Years |
| :--- | :--- | :--- |
| `heat_activations_daily.csv` | Daily `gridmet_tmax_f` and threshold flags | 2016–2025 |
| `heat_activations_annual.csv` | Annual threshold counts | 2016–2025 |
| `heat_activations_monthly.csv` | Monthly counts of days at or above 90°F and 95°F | 2016–2025 |
| `summer_avg_tmax_annual.csv` | Mean June–August daily maximum (°F) | 1990–2025 |

| Threshold | Definition |
| :--- | :--- |
| `gridmet_over_90f` | Daily maximum ≥ 90°F, the outdoor trigger for Stage I of CDCR's Heat Pathology Plan |
| `gridmet_over_95f` | Daily maximum ≥ 95°F; Stage III is triggered by indoor temperature, so this is a proxy only |
| `gridmet_over_avg_base1991_2020` | Daily maximum ≥ the prison's 1991–2020 mean June–August maximum |
| `gridmet_over_avg_plus10_base1991_2020` | Daily maximum ≥ that mean plus 10°F, the threshold associated with a 5.2% increase in all-cause mortality (Skarha et al., 2023) |

The 1991–2020 baseline is fixed across all years. These observed counts are not interchangeable with the LOCA2-CA counts in the hazard component, which use a 1981–2010 model baseline.

## Output columns

`data/CDCR_heat_risk_index_additive_25_25_50.csv`, two rows per prison:

| Column | Description |
| :--- | :--- |
| `cdcr_code`, `name` | CDCR institution code and name |
| `latitude`, `longitude` | Facility centroid |
| `average_2025_population` | 2025 average population |
| `time_period` | `current` or `midcentury` |
| `hazard_score`, `exposure_score`, `vulnerability_score` | Component scores (0–1) |
| `risk_score` | Risk score (0–100), normalized across both periods |
| `risk_category` | `Highest`, `High`, `Moderate`, or `Lowest` |
| `AQI_norm`, `ratio_indoor_to_outdoor`, `days_indoor_above_78f_2025`, `uhi_normalized` | Hazard and exposure inputs |
| `pct_hu_mechanical`, `pct_hu_evaporative`, `pct_hu_air_handlers` | Housing unit cooling shares |
| `medical_acuity`, `cchcs_age_over_50_pct_2025`, `cchcs_mental_health_eop_pct_2025`, `cchcs_dpp_pct_2025`, `race_peopleofcolor_pct`, `gender_female_pct` | Vulnerability inputs |
| `rhu_pct_2025`, `dist_nearest_medical_mi`, `in_urban_area_2020`, `california_model_facility`, `year_opened` | Descriptive, not scored |
| `index_version` | Version of the index that produced the row |

## Versions

The current version is v0.3. Each output carries an `index_version` column (or `meta.index_version` in the JSON), and earlier versions are kept in `data/archive/` and `app_export/output/archive/`. The notebooks archive the existing output before writing a new version.

## Reproducing the index

The three repositories must be checked out side by side; paths are set in `config.py`.

1. `python3 build_inputs.py` assembles `data/heat_risk_inputs.csv` from the two upstream repositories and `gridmet/data/`.
2. Run `index/heat_risk_index.ipynb`, then `index/sensitivity_analysis.ipynb`.
3. `python3 index/generate_heat_risk_report.py` writes maps and a summary report to `reports/` (not tracked).
4. `python3 app_export/build_app_data.py` writes the website data to `app_export/output/` and copies it into a sibling `website` checkout.

To refresh observed temperatures, run `python3 gridmet/extract_gridmet_heat.py` (downloads about 6 GB of gridMET data), then `gridmet/extract_gridmet_summer_avg.py`.

## License and citation

Code is MIT and data is CC BY 4.0; see [LICENSE.md](LICENSE.md). To cite the index, see [CITATION.cff](CITATION.cff).

## References

Abatzoglou, J. T. (2013). Development of gridded surface meteorological data for ecological applications and modelling. *International Journal of Climatology*, 33(1), 121–131. https://doi.org/10.1002/joc.3413

Abdala, A., Bhola, A., Gutierrez, G., Henderson, E., & O'Neill, M. (2023). *Hidden hazards: The impacts of climate change on incarcerated people in California state prisons*. Ella Baker Center for Human Rights. https://ellabakercenter.org/reports/hiddenhazards/

Alahmad, B., Kessler, W., Alwadi, Y., Schwartz, J., Wagner, G. R., & Michaels, D. (2025). A nationwide analysis of heat and workplace injuries in the United States. *Environmental Health*, 24, 65. https://doi.org/10.1186/s12940-025-01231-1

Benz, S. A., & Burney, J. A. (2021). Widespread race and class disparities in surface urban heat islands across the United States. *Earth's Future*, 9(7), e2021EF002016. https://doi.org/10.7910/DVN/1F72FB

Brunn, K., Toledo, O., Tran, C. C., Vasudevan, A., & Venkat, B. J. (2025). Carceral heat exposure as harmful design: An integrative model for understanding the health impacts of heat on incarcerated people in the United States. *Social Science & Medicine*, 367, 117679. https://doi.org/10.1016/j.socscimed.2025.117679

California Department of Corrections and Rehabilitation. (2026, January). *Air Cooling Pilot Program Supplemental Report*. https://www.cdcr.ca.gov/fpcm/wp-content/uploads/sites/184/2026/02/Air_Cooling_Document_for_Legislature.pdf

Cloud, D. H., Williams, B., Haardörfer, R., Brinkley-Rubinstein, L., & Cooper, H. L. F. (2023). Extreme heat and suicide watch incidents among incarcerated men. *JAMA Network Open*, 6(8), e2328380. https://doi.org/10.1001/jamanetworkopen.2023.28380

Ovienmhada, U., Hines, M., Krisch, M., Diongue, A. T., Minchew, B., & Wood, D. R. (2024). Spatiotemporal facility-level patterns of summer heat exposure, vulnerability, and risk in United States prison landscapes. *GeoHealth*, 8(9), e2024GH001108. https://doi.org/10.1029/2024GH001108

Skarha, J., Spangler, K., Dosa, D., Rich, J. D., Savitz, D. A., & Zanobetti, A. (2023). Heat-related mortality in U.S. state and private prisons: A case-crossover analysis. *PLOS ONE*, 18(3), e0281389. https://doi.org/10.1371/journal.pone.0281389
