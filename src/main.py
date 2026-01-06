import os
import logging
from pathlib import Path

from dotenv import load_dotenv

from utils.db import get_db_connection, apply_schema, close_connection


def setup_logging():
    """
    Configure root logger.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )


def main():
    """
    Entry point for Asana seed data simulation.
    """
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Starting Asana seed data generation pipeline")

    # Load environment variables
    load_dotenv()

    db_path = os.getenv("DB_PATH")
    if not db_path:
        raise EnvironmentError(
            "DB_PATH not set. Please configure it in .env or .env.example"
        )

    schema_path = Path(__file__).parent.parent / "schema.sql"

    conn = None
    try:
        # Initialize database
        conn = get_db_connection(db_path)

        # Apply schema
        apply_schema(conn, schema_path)

        logger.info("Database initialization complete")

        # ============================
        # GENERATORS WILL BE CALLED HERE
        # ============================
        # Example (to be added next):
        # generate_organizations(conn)
        # generate_users(conn)
        # generate_teams(conn)
        #
        # For now, schema-only initialization is intentional.

        logger.info("Pipeline completed successfully")

    except Exception as e:
        logger.exception("Pipeline failed")
        raise e

    finally:
        if conn:
            close_connection(conn)


if __name__ == "__main__":
    main()

