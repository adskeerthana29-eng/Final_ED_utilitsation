
import sqlite3

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple, Union

from database.connection import (
    get_connection,
    resolve_db_path,
)

from database.schema import (
    TABLE_EHR_HISTORICAL_DATA,
    TABLE_CURRENT_PATIENT_DATA,
    COLUMN_NAMES,
    EXPECTED_COLUMNS,
    TOTAL_EXPECTED_ROWS,
)


# ==========================================================
# Custom Exceptions
# ==========================================================

class DatabaseValidationError(Exception):
    """Base validation exception."""
    pass


class DatabaseNotFoundError(DatabaseValidationError):
    """Database file not found."""
    pass


class TableNotFoundError(DatabaseValidationError):
    """Table missing."""
    pass


class SchemaMismatchError(DatabaseValidationError):
    """Schema mismatch."""
    pass


class DataIntegrityError(DatabaseValidationError):
    """Data integrity failure."""
    pass


# ==========================================================
# Validation Result
# ==========================================================

@dataclass
class ValidationResult:

    is_valid: bool

    db_path: str

    file_exists: bool = False

    file_size_bytes: int = 0

    historical_table_exists: bool = False

    current_table_exists: bool = False

    expected_column_count: int = len(EXPECTED_COLUMNS)

    actual_column_count: int = 0

    actual_columns: List[str] = field(default_factory=list)

    missing_columns: List[str] = field(default_factory=list)

    extra_columns: List[str] = field(default_factory=list)

    row_count: int = 0

    expected_row_count: int = TOTAL_EXPECTED_ROWS

    errors: List[str] = field(default_factory=list)

    warnings: List[str] = field(default_factory=list)

    def summary(self):

        status = "PASSED" if self.is_valid else "FAILED"

        report = [

            "=" * 60,

            f"DATABASE VALIDATION : {status}",

            "=" * 60,

            f"Database : {self.db_path}",

            f"File Exists : {self.file_exists}",

            f"Historical Table : {self.historical_table_exists}",

            f"Current Table : {self.current_table_exists}",

            f"Columns : {self.actual_column_count}/{self.expected_column_count}",

            f"Rows : {self.row_count}",

        ]

        if self.missing_columns:

            report.append(
                f"Missing Columns : {', '.join(self.missing_columns)}"
            )

        if self.extra_columns:

            report.append(
                f"Extra Columns : {', '.join(self.extra_columns)}"
            )

        if self.errors:

            report.append("")

            report.append("Errors")

            report.extend(self.errors)

        if self.warnings:

            report.append("")

            report.append("Warnings")

            report.extend(self.warnings)

        report.append("=" * 60)

        return "\n".join(report)
# ==========================================================
# Helper Functions
# ==========================================================

def check_file_exists(
    db_path: Path,
) -> Tuple[bool, int]:
    """
    Check whether the database file exists.
    """

    if db_path.is_file():
        return True, db_path.stat().st_size

    return False, 0


def check_table_exists(
    conn: sqlite3.Connection,
    table_name: str,
) -> bool:
    """
    Check whether a table exists.
    """

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name=?
        """,
        (table_name,),
    )

    return cursor.fetchone() is not None


def get_actual_columns(
    conn: sqlite3.Connection,
    table_name: str,
):

    cursor = conn.cursor()

    cursor.execute(
        f"PRAGMA table_info({table_name})"
    )

    rows = cursor.fetchall()

    return [

        (row[0], row[1], row[2])

        for row in rows
    ]


def get_table_row_count(
    conn: sqlite3.Connection,
    table_name: str,
) -> int:

    cursor = conn.cursor()

    cursor.execute(
        f"""
        SELECT COUNT(*)
        FROM {table_name}
        """
    )

    return cursor.fetchone()[0]


# ==========================================================
# Column Validation
# ==========================================================

def validate_columns(
    conn: sqlite3.Connection,
    result: ValidationResult,
):

    columns = get_actual_columns(
        conn,
        TABLE_EHR_HISTORICAL_DATA,
    )

    actual_column_names = [

        column[1]

        for column in columns

    ]

    result.actual_columns = actual_column_names

    result.actual_column_count = len(
        actual_column_names
    )

    expected = set(COLUMN_NAMES)

    actual = set(actual_column_names)

    result.missing_columns = [

        column

        for column in COLUMN_NAMES

        if column not in actual

    ]

    result.extra_columns = [

        column

        for column in actual_column_names

        if column not in expected

    ]

    if result.missing_columns:

        result.errors.append(
            "Missing required columns."
        )

        result.is_valid = False

    if result.extra_columns:

        result.warnings.append(
            "Unexpected extra columns detected."
        )
# ==========================================================
# Main Validation Function
# ==========================================================

def validate_database(
    db_path: Optional[Union[str, Path]] = None,
    expected_rows: int = TOTAL_EXPECTED_ROWS,
    raise_on_error: bool = False,
) -> ValidationResult:
    """
    Validate the SQLite database.
    """

    resolved_path = resolve_db_path(db_path)

    result = ValidationResult(
        is_valid=True,
        db_path=str(resolved_path),
        expected_row_count=expected_rows,
    )

    # ------------------------------------------------------
    # Check database file
    # ------------------------------------------------------

    file_exists, file_size = check_file_exists(
        resolved_path
    )

    result.file_exists = file_exists
    result.file_size_bytes = file_size

    if not file_exists:

        result.is_valid = False

        result.errors.append(
            f"Database file not found: {resolved_path}"
        )

        if raise_on_error:
            raise DatabaseNotFoundError(result.errors[-1])

        return result

    # ------------------------------------------------------
    # Connect Database
    # ------------------------------------------------------

    conn = None

    try:

        conn = get_connection(
            resolved_path,
            read_only=True,
            row_factory=False,
        )

        # ----------------------------------------------
        # Historical Table
        # ----------------------------------------------

        result.historical_table_exists = check_table_exists(
            conn,
            TABLE_EHR_HISTORICAL_DATA,
        )

        if not result.historical_table_exists:

            result.is_valid = False

            result.errors.append(
                f"Table '{TABLE_EHR_HISTORICAL_DATA}' not found."
            )

        # ----------------------------------------------
        # Current Table
        # ----------------------------------------------

        result.current_table_exists = check_table_exists(
            conn,
            TABLE_CURRENT_PATIENT_DATA,
        )

        if not result.current_table_exists:

            result.is_valid = False

            result.errors.append(
                f"Table '{TABLE_CURRENT_PATIENT_DATA}' not found."
            )

        # ----------------------------------------------
        # Validate Historical Table Schema
        # ----------------------------------------------

        if result.historical_table_exists:

            validate_columns(
                conn,
                result,
            )

            result.row_count = get_table_row_count(
                conn,
                TABLE_EHR_HISTORICAL_DATA,
            )

            if result.row_count != expected_rows:

                result.warnings.append(
                    f"Expected {expected_rows} rows but found {result.row_count}."
                )

        # ----------------------------------------------
        # Raise Exceptions
        # ----------------------------------------------

        if raise_on_error and not result.is_valid:

            raise SchemaMismatchError(
                "\n".join(result.errors)
            )

    except sqlite3.Error as e:

        result.is_valid = False

        result.errors.append(str(e))

        if raise_on_error:

            raise DatabaseValidationError(str(e))

    finally:

        if conn:

            conn.close()

    return result