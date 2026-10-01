"""
Paths to this repo's inputs. Data from the two upstream repos is read from
sibling checkouts in the same parent directory as this repo:

    cdcr_facility_data/          CDCR institution data
    ca_prison_climate_justice/   facility list, site attributes, climate hazards
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
SIBLINGS = ROOT.parent

CDCR_REPO = SIBLINGS / 'cdcr_facility_data'
CPCJ_REPO = SIBLINGS / 'ca_prison_climate_justice'
WEBSITE_REPO = SIBLINGS / 'website'

# cdcr_facility_data
CDCR_FACILITIES = CDCR_REPO / 'data' / 'cdcr_facilities.csv'
CDCR_INDOOR_78F = CDCR_REPO / 'sources' / 'CDCR_indoor_78f_days_2025.csv'
CDCR_CROSSWALK = CDCR_REPO / 'crosswalk' / 'institutions.csv'

# ca_prison_climate_justice
CA_FACILITIES = CPCJ_REPO / 'data_sources' / 'facilities' / 'ca_facilities.csv'
HEAT_AIR_HAZARD = CPCJ_REPO / 'data' / 'hazards' / 'heat_air_hazard.csv'
ALL_HAZARDS = CPCJ_REPO / 'data' / 'allfacilities_climate_hazards.csv'
VCP_TRACTS = CPCJ_REPO / 'data_sources' / 'hazards' / 'VCP_Tracts.geojson'

# this repo
GRIDMET_DATA = ROOT / 'gridmet' / 'data'
INPUTS = ROOT / 'data' / 'heat_risk_inputs.csv'
INDEX_CSV = ROOT / 'data' / 'CDCR_heat_risk_index_additive_25_25_50.csv'
SENSITIVITY_CSV = ROOT / 'data' / 'CDCR_heat_risk_sensitivity.csv'
ARCHIVE = ROOT / 'data' / 'archive'
CA_OUTLINE = ROOT / 'data' / 'ca_outline_simple.json'
REPORTS = ROOT / 'reports'

FEMA_COLUMNS = [
    'facilityid', 'address', 'city', 'state', 'zip', 'county', 'type', 'securelvl',
    'geometry', 'latitude', 'longitude', 'tract_geoid',
    'dist_nearest_medical_mi', 'in_urban_area_2020', 'benz_uhi_dt',
]


def load_institutions():
    """CDCR institutions (cdcr_facility_data) joined to their FEMA facility
    record and site attributes (ca_prison_climate_justice) on facilityid."""
    cdcr = pd.read_csv(CDCR_FACILITIES)
    fema = pd.read_csv(CA_FACILITIES, usecols=FEMA_COLUMNS)
    return cdcr.merge(fema, on='facilityid', how='left')
