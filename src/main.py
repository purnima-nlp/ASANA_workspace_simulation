import os
import logging
from pathlib import Path

from dotenv import load_dotenv

from utils.db import get_db_connection, apply_schema, close_connection

# Generators
from generators.organizations import generate_organizations
from generators.users import generate_users
from generators.teams import generate_teams
from generators.team_memberships import generate_team_memberships
from generators.projects import generate_projects
from generators.sections import generate_sections
from generators.tasks import generate_tasks
from generators.task_projects import generate_task_projects
from generators.comments import generate_comments
from generators.custom_field_definitions import generate_custom_field_definitions
from generators.project_custom_fields import generate_project_custom_fields
from generators.custom_field_values import generate_custom_field_values
from generators.tags import generate_tags
from generators.task_tags import generate_task_tags


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )


def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting Asana seed data generation pipeline")

    load_dotenv()

    db_path = os.getenv("DB_PATH")
    if not db_path:
        raise EnvironmentError("DB_PATH not set in .env")

    schema_path = Path(__file__).parent.parent / "schema.sql"

    conn = None
    try:
        # ---------------------------
        # Initialize DB
        # ---------------------------
        conn = get_db_connection(db_path)
        apply_schema(conn, schema_path)
        logger.info("Database initialized")

        # ---------------------------
        # Core hierarchy
        # ---------------------------
        org_ids = generate_organizations(conn)
        users = generate_users(conn, org_ids, n_users=800)
        teams = generate_teams(conn, org_ids, n_teams=40)
        generate_team_memberships(conn, users, teams)

        # ---------------------------
        # Projects & structure
        # ---------------------------
        projects = generate_projects(conn, teams, projects_per_team=4)
        sections = generate_sections(conn, projects)

        # ---------------------------
        # Tasks & placement
        # ---------------------------
        tasks = generate_tasks(
            conn,
            org_ids,
            users,
            teams,
            projects,
            n_tasks_per_project=40
        )
        generate_task_projects(conn, tasks, projects, sections)

        # ---------------------------
        # Discussion
        # ---------------------------
        generate_comments(conn, tasks, users)

        # ---------------------------
        # Custom fields
        # ---------------------------
        custom_fields = generate_custom_field_definitions(conn, org_ids, n_fields=8)
        project_custom_fields = generate_project_custom_fields(
            conn, projects, custom_fields
        )
        generate_custom_field_values(
            conn, tasks, project_custom_fields, custom_fields
        )

        # ---------------------------
        # Tags
        # ---------------------------
        tags = generate_tags(conn, org_ids, n_tags=12)
        generate_task_tags(conn, tasks, tags)

        logger.info("Pipeline completed successfully")

    except Exception:
        logger.exception("Pipeline failed")
        raise

    finally:
        if conn:
            close_connection(conn)


if __name__ == "__main__":
    main()
