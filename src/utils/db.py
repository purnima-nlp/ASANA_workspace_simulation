import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def get_db_connection(db_path: str) -> sqlite3.Connection:
    """
    Create and return a SQLite database connection with
    foreign key enforcement enabled.
    """
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row

    logger.info(f"Connected to SQLite database at {db_path}")
    return conn


def apply_schema(conn: sqlite3.Connection, schema_path: str) -> None:
    """
    Apply schema.sql to the connected SQLite database.
    """
    schema_path = Path(schema_path)

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    try:
        conn.executescript(schema_sql)
        conn.commit()
        logger.info("Database schema applied successfully")
    except sqlite3.Error as e:
        logger.exception("Failed to apply schema")
        raise e


def close_connection(conn: sqlite3.Connection) -> None:
    """
    Close the SQLite database connection.
    """
    if conn:
        conn.close()
        logger.info("Database connection closed")

