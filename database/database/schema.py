
from typing import Dict, List, Set, Tuple


TABLE_EHR_HISTORICAL_DATA = "ehr_historical_data"
TABLE_CURRENT_PATIENT_DATA = "current_patient_data"

TOTAL_EXPECTED_ROWS = 10000



EXPECTED_COLUMNS: List[Tuple[str, str]] = [
    ("patient_id", "TEXT"),
    ("name", "TEXT"),
    ("phone_number", "TEXT"),
    ("gender", "TEXT"),
    ("region", "TEXT"),
    ("past_diagnosis", "TEXT"),
    ("triage_acuity", "INTEGER"),
    ("prior_ed_visits", "INTEGER"),
    ("ed_visit_last_30_days", "INTEGER"),
    ("days_since_last_ed_visit", "INTEGER"),
    ("alternative_care_access", "TEXT"),
    ("care_management_contact_last_90_days", "INTEGER"),
    ("pcp_visit_last_12_months", "INTEGER"),
    ("days_since_last_pcp_visit", "INTEGER"),
]


COLUMN_NAMES: List[str] = [column[0] for column in EXPECTED_COLUMNS]

COLUMN_TYPES: Dict[str, str] = {
    column[0]: column[1]
    for column in EXPECTED_COLUMNS
}



SORTABLE_COLUMNS: Set[str] = set(COLUMN_NAMES)

ALLOWED_SORT_ORDERS: Set[str] = {
    "ASC",
    "DESC"
}

FILTERABLE_COLUMNS: Dict[str, str] = {

    "patient_id": "TEXT",
    "name": "TEXT",
    "gender": "TEXT",
    "region": "TEXT",
    "past_diagnosis": "TEXT",
    "alternative_care_access": "TEXT",

    "triage_acuity": "INTEGER",
    "prior_ed_visits": "INTEGER",
    "ed_visit_last_30_days": "INTEGER",
    "days_since_last_ed_visit": "INTEGER",
    "care_management_contact_last_90_days": "INTEGER",
    "pcp_visit_last_12_months": "INTEGER",
    "days_since_last_pcp_visit": "INTEGER",
}


RANGE_SUFFIXES: Tuple[str, str] = (
    "_min",
    "_max",
)