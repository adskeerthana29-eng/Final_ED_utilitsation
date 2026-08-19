#!/usr/bin/env python3
"""
CLI Database Verification Script

Verifies

• Database file
• ehr_historical_data
• current_patient_data
• Schema
• Record count
• Summary statistics
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database.connection import (
    get_db_connection,
    resolve_db_path,
)

from database.validation import validate_database

from database.schema import (
    TABLE_EHR_HISTORICAL_DATA,
    TABLE_CURRENT_PATIENT_DATA,
)

from database.queries import (
    get_table_schema,
    get_overall_summary_metrics,
    get_sex_distribution,
    get_diagnosis_category_counts,
    get_all_records,
    get_record_by_patient_id,
)


def format_table(headers, rows):

    widths = [len(h) for h in headers]

    string_rows = [
        [str(item) for item in row]
        for row in rows
    ]

    for row in string_rows:

        for i, cell in enumerate(row):

            widths[i] = max(
                widths[i],
                len(cell),
            )

    header = " | ".join(
        headers[i].ljust(widths[i])
        for i in range(len(headers))
    )

    separator = "-+-".join(
        "-" * w
        for w in widths
    )

    body = []

    for row in string_rows:

        body.append(
            " | ".join(
                row[i].ljust(widths[i])
                for i in range(len(row))
            )
        )

    return "\n".join(
        [
            header,
            separator,
            *body,
        ]
    )
def run_verification():

    db_path = resolve_db_path()

    print("=" * 70)
    print("ED UTILIZATION NAVIGATOR - DATABASE VERIFICATION")
    print("=" * 70)

    print(f"\nDatabase : {db_path}\n")

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    report = validate_database(db_path)

    print(report.summary())

    if not report.is_valid:
        print("\nDatabase validation failed.")
        return

    # --------------------------------------------------
    # Open Connection
    # --------------------------------------------------

    with get_db_connection(
        db_path,
        read_only=True,
    ) as conn:

        # ----------------------------------------------
        # Historical Table Schema
        # ----------------------------------------------

        print("\n" + "=" * 70)
        print("EHR HISTORICAL DATA SCHEMA")
        print("=" * 70)

        schema = get_table_schema(
            conn,
            TABLE_EHR_HISTORICAL_DATA,
        )

        rows = []

        for column in schema:

            rows.append(
                [
                    column["cid"] + 1,
                    column["name"],
                    column["type"],
                    "YES" if column["is_pk"] else "",
                ]
            )

        print(
            format_table(
                ["#", "Column", "Type", "PK"],
                rows,
            )
        )

        # ----------------------------------------------
        # Summary Statistics
        # ----------------------------------------------

        print("\n" + "=" * 70)
        print("SUMMARY STATISTICS")
        print("=" * 70)

        metrics = get_overall_summary_metrics(conn)

        for key, value in metrics.items():

            print(f"{key:<35} : {value}")

        # ----------------------------------------------
        # Gender Distribution
        # ----------------------------------------------

        print("\n" + "=" * 70)
        print("GENDER DISTRIBUTION")
        print("=" * 70)

        gender = get_sex_distribution(conn)

        gender_rows = []

        for row in gender:

            gender_rows.append(
                [
                    row["gender"],
                    row["count"],
                    row["percentage"],
                ]
            )

        print(
            format_table(
                ["Gender", "Count", "%"],
                gender_rows,
            )
        )

        # ----------------------------------------------
        # Diagnosis Distribution
        # ----------------------------------------------

        print("\n" + "=" * 70)
        print("PAST DIAGNOSIS DISTRIBUTION")
        print("=" * 70)

        diagnosis = get_diagnosis_category_counts(conn)

        diagnosis_rows = []

        for row in diagnosis:

            diagnosis_rows.append(
                [
                    row["past_diagnosis"],
                    row["count"],
                    row["percentage"],
                ]
            )

        print(
            format_table(
                ["Past Diagnosis", "Count", "%"],
                diagnosis_rows,
            )
        )

        # ----------------------------------------------
        # Sample Patient
        # ----------------------------------------------

        print("\n" + "=" * 70)
        print("SAMPLE PATIENT")
        print("=" * 70)

        patients = get_all_records(
            conn,
            limit=1,
        )

        if patients:

            patient = get_record_by_patient_id(
                conn,
                patients[0]["patient_id"],
            )

            print(
                json.dumps(
                    patient,
                    indent=4,
                )
            )

        # ----------------------------------------------
        # Current Patient Table Count
        # ----------------------------------------------

        cursor = conn.cursor()

        cursor.execute(
            f"""
            SELECT COUNT(*)
            FROM {TABLE_CURRENT_PATIENT_DATA}
            """
        )

        current_count = cursor.fetchone()[0]

        print("\n" + "=" * 70)
        print("CURRENT PATIENT TABLE")
        print("=" * 70)

        print(
            f"Current Patient Records : {current_count}"
        )

    print("\n" + "=" * 70)
    print("DATABASE VERIFIED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    run_verification()