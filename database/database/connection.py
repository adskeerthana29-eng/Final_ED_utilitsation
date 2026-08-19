"""
Database connection manager for ED-Utilization-Navigator.

Provides safe, configurable connections and context managers for SQLite.
Default database: ed_utilization.db (in project root or configured via ED_NAVIGATOR_DB_PATH).
"""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional, Union

# Default database filename
DEFAULT_DB_FILENAME = "ed_utilization.db"
ENV_DB_PATH_KEY = "ED_NAVIGATOR_DB_PATH"


def get_project_root() -> Path:
    """Returns the root directory of the ED-Utilization-Navigator project."""
    # Parent directory of the database package is the project root.
    return Path(__file__).resolve().parent.parent


def resolve_db_path(db_path: Optional[Union[str, Path]] = None) -> Path:
    """
    Resolves the SQLite database path in priority order:
    1. Explicit argument `db_path`
    2. Environment variable `ED_NAVIGATOR_DB_PATH`
    3. Default `ed_utilization.db` in project root
    """
    if db_path is not None:
        target = Path(db_path)
    elif os.environ.get(ENV_DB_PATH_KEY):
        target = Path(os.environ[ENV_DB_PATH_KEY])
    else:
        target = get_project_root() / DEFAULT_DB_FILENAME

    if not target.is_absolute():
        target = (get_project_root() / target).resolve()

    return target


def get_connection(
    db_path: Optional[Union[str, Path]] = None,
    read_only: bool = False,
    row_factory: bool = True,
    timeout: float = 10.0,
) -> sqlite3.Connection:
    """
    Creates and returns an active SQLite database connection.

    Args:
        db_path: Path to SQLite database file. If None, resolves to default.
        read_only: If True, opens connection in strict SQLite read-only mode.
        row_factory: If True, sets sqlite3.Row for dictionary-like column access.
        timeout: Lock wait timeout in seconds.

    Returns:
        sqlite3.Connection: Active database connection.
    """
    resolved_path = resolve_db_path(db_path)

    if read_only:
        if not resolved_path.exists():
            raise FileNotFoundError(f"Database file not found: {resolved_path}")
        # Use SQLite URI mode for strict read-only enforcement
        uri_path = f"file:{resolved_path.as_posix()}?mode=ro"
        conn = sqlite3.connect(uri_path, uri=True, timeout=timeout)
    else:
        conn = sqlite3.connect(str(resolved_path), timeout=timeout)

    if row_factory:
        conn.row_factory = sqlite3.Row

    # Ensure foreign keys are enabled (for future multi-table relational support)
    conn.execute("PRAGMA foreign_keys = ON;")

    return conn


@contextmanager
def get_db_connection(
    db_path: Optional[Union[str, Path]] = None,
    read_only: bool = False,
    row_factory: bool = True,
) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for database connections. Automatically closes connection upon exit.

    Example:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM ehr_historical_data")
    """
    conn = get_connection(db_path=db_path, read_only=read_only, row_factory=row_factory)
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def get_db_cursor(
    db_path: Optional[Union[str, Path]] = None,
    read_only: bool = False,
    row_factory: bool = True,
) -> Generator[sqlite3.Cursor, None, None]:
    """
    Context manager for database cursors. Automatically handles cursor and connection closing.

    Example:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM ehr_historical_data LIMIT 5")
            rows = cursor.fetchall()
    """
    with get_db_connection(db_path=db_path, read_only=read_only, row_factory=row_factory) as conn:
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()
