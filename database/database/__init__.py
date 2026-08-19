"""
Database package for ED-Utilization-Navigator.

Provides safe, modular, and parameterized SQLite data access.
"""

# ==========================================================
# Connection
# ==========================================================

from database.connection import (
    DEFAULT_DB_FILENAME,
    ENV_DB_PATH_KEY,
    get_connection,
    get_db_connection,
    get_db_cursor,
    get_project_root,
    resolve_db_path,
)

# ==========================================================
# Schema
# ==========================================================

from database.schema import (
    TABLE_EHR_HISTORICAL_DATA,
    TABLE_CURRENT_PATIENT_DATA,
    TOTAL_EXPECTED_ROWS,
    EXPECTED_COLUMNS,
    COLUMN_NAMES,
    COLUMN_TYPES,
    SORTABLE_COLUMNS,
    FILTERABLE_COLUMNS,
    ALLOWED_SORT_ORDERS,
)

# ==========================================================
# Validation
# ==========================================================

from database.validation import (
    ValidationResult,
    DatabaseValidationError,
    DatabaseNotFoundError,
    TableNotFoundError,
    SchemaMismatchError,
    DataIntegrityError,
    check_file_exists,
    check_table_exists,
    get_actual_columns,
    get_table_row_count,
    validate_database,
)

# ==========================================================
# Queries
# ==========================================================

from database.queries import (
    get_table_schema,
    get_column_names,
    get_total_records_count,
    get_all_records,
    get_record_by_patient_id,
    get_records_by_patient_ids,
    search_patients,
    filter_records,
    get_current_patient,
    get_complete_patient_profile,
    get_overall_summary_metrics,
    get_gender_distribution,
    get_region_distribution,
    get_diagnosis_distribution,
    get_triage_distribution,
    get_ed_visit_statistics,
    get_care_management_statistics,
    get_pcp_statistics,
    get_dashboard_charts,
    get_high_risk_patients,
    get_recommendation_statistics,
    patient_exists,
    current_encounter_exists,
    get_database_health,
)

__all__ = [

    # Connection
    "DEFAULT_DB_FILENAME",
    "ENV_DB_PATH_KEY",
    "get_connection",
    "get_db_connection",
    "get_db_cursor",
    "get_project_root",
    "resolve_db_path",

    # Schema
    "TABLE_EHR_HISTORICAL_DATA",
    "TABLE_CURRENT_PATIENT_DATA",
    "TOTAL_EXPECTED_ROWS",
    "EXPECTED_COLUMNS",
    "COLUMN_NAMES",
    "COLUMN_TYPES",
    "SORTABLE_COLUMNS",
    "FILTERABLE_COLUMNS",
    "ALLOWED_SORT_ORDERS",

    # Validation
    "ValidationResult",
    "DatabaseValidationError",
    "DatabaseNotFoundError",
    "TableNotFoundError",
    "SchemaMismatchError",
    "DataIntegrityError",
    "check_file_exists",
    "check_table_exists",
    "get_actual_columns",
    "get_table_row_count",
    "validate_database",

    # Queries
    "get_table_schema",
    "get_column_names",
    "get_total_records_count",
    "get_all_records",
    "get_record_by_patient_id",
    "get_records_by_patient_ids",
    "search_patients",
    "filter_records",
    "get_current_patient",
    "get_complete_patient_profile",
    "get_overall_summary_metrics",
    "get_gender_distribution",
    "get_region_distribution",
    "get_diagnosis_distribution",
    "get_triage_distribution",
    "get_ed_visit_statistics",
    "get_care_management_statistics",
    "get_pcp_statistics",
    "get_dashboard_charts",
    "get_high_risk_patients",
    "get_recommendation_statistics",
    "patient_exists",
    "current_encounter_exists",
    "get_database_health",
]