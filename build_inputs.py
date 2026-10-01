"""
Assemble data/heat_risk_inputs.csv: one row per CDCR institution with indoor
heat data, holding every hazard, exposure and vulnerability input the index
uses, plus descriptive fields carried into the index output.

This is the only step that reads the upstream repos (see config.py). Re-run it
when upstream data changes; the diff of heat_risk_inputs.csv shows what moved
before the index is re-cut.

Usage:
    python3 build_inputs.py
"""

import pandas as pd

import config

YEAR = 2025
HAZARD_COLUMNS = [
    'loca2_days_over_avg_plus10_historic', 'loca2_days_over_avg_plus10_midcentury',
    'loca2_days_over_90_historic', 'loca2_days_over_90_midcentury',
    'loca2_nights_over_p95_historic', 'loca2_nights_over_p95_midcentury',
    'AQI_norm',
]


def code_aliases():
    xw = pd.read_csv(config.CDCR_CROSSWALK, dtype={'alias_codes': str})
    return {a: code for code, al in zip(xw['cdcr_code'], xw['alias_codes'].fillna(''))
            for a in filter(None, al.split(';'))}


def outdoor_78f_days():
    """May-October days with gridMET daily tmax above 78°F."""
    daily = pd.read_csv(config.GRIDMET_DATA / 'heat_activations_daily.csv', parse_dates=['date'])
    season = daily[(daily['date'].dt.year == YEAR) & daily['date'].dt.month.between(5, 10)]
    return (season['gridmet_tmax_f'] > 78).groupby(season['cdcr_code']).sum().rename(
        f'days_outdoor_above_78f_{YEAR}')


def main():
    inst = config.load_institutions().set_index('cdcr_code')

    indoor = pd.read_csv(config.CDCR_INDOOR_78F)
    indoor['cdcr_code'] = indoor['cdcr_code'].replace(code_aliases())
    indoor = indoor.set_index('cdcr_code')[f'days_indoor_above_78f_{YEAR}']

    # Institutions with CDCR indoor temperature data define the index universe
    df = inst.loc[inst.index.intersection(indoor.index)].join(indoor).join(outdoor_78f_days())
    df['ratio_indoor_to_outdoor'] = (
        df[f'days_indoor_above_78f_{YEAR}'] / df[f'days_outdoor_above_78f_{YEAR}']).round(3)

    # Surface UHI (Benz & Burney 2021 ΔT), negative values set to 0, scaled by the
    # maximum across these institutions
    dt = df['benz_uhi_dt'].clip(lower=0)
    df['uhi_normalized'] = (dt / dt.max()).round(4)

    hazard = pd.read_csv(config.HEAT_AIR_HAZARD).set_index('cdcr_code')[HAZARD_COLUMNS]
    df = df.join(hazard)

    columns = [
        'name', 'facilityid', 'latitude', 'longitude', 'tract_geoid',
        f'average_{YEAR}_population',
        # hazard
        *HAZARD_COLUMNS,
        # exposure
        f'days_indoor_above_78f_{YEAR}', f'days_outdoor_above_78f_{YEAR}', 'ratio_indoor_to_outdoor',
        'uhi_normalized', 'pct_hu_mechanical', 'pct_hu_evaporative', 'pct_hu_air_handlers',
        # vulnerability
        f'cchcs_high_risk_p1_pct_{YEAR}', f'cchcs_high_risk_p2_pct_{YEAR}', f'cchcs_medium_risk_pct_{YEAR}',
        f'cchcs_age_over_50_pct_{YEAR}', f'cchcs_mental_health_eop_pct_{YEAR}', f'cchcs_dpp_pct_{YEAR}',
        'race_peopleofcolor_pct', 'gender_female_pct',
        # descriptive
        f'rhu_pct_{YEAR}', 'dist_nearest_medical_mi', 'in_urban_area_2020',
        'california_model_facility', 'year_opened',
    ]
    out = df[columns].reset_index().sort_values('cdcr_code')
    out.to_csv(config.INPUTS, index=False)
    print(f'Wrote {len(out)} institutions to {config.INPUTS.relative_to(config.ROOT)}')


if __name__ == '__main__':
    main()
