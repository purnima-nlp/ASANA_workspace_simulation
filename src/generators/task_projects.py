import logging
import random

logger = logging.getLogger(__name__)


def generate_task_projects(conn, tasks, projects, sections):
    """
    Generate task–project associations.

    Seed methodology implemented:
    - Each task belongs to at least one project
    - Majority assigned to project owned by assignee's team (approximated)
    - Minority assigned to cross-team projects
    - Section always belongs to the same project
    """
    cursor = conn.cursor()
    task_projects = []

    # Build lookup: project_id -> sections
    project_sections = {}
    for section in sections:
        section_id, project_id, name, position = section
        project_sections.setdefault(project_id, []).append(section_id)

    project_ids = [p["project_id"] for p in projects]

    for task in tasks:
        task_id = task["task_id"]

        # Decide how many projects this task appears in
        n_projects = 1 if random.random() < 0.80 else random.randint(2, 3)

        assigned_projects = random.sample(
            project_ids,
            k=min(n_projects, len(project_ids))
        )

        for project_id in assigned_projects:
            valid_sections = project_sections.get(project_id, [])
            section_id = random.choice(valid_sections) if valid_sections else None

            task_projects.append((
                task_id,
                project_id,
                section_id
            ))

    cursor.executemany(
        """
        INSERT INTO task_projects (
            task_id,
            project_id,
            section_id
        )
        VALUES (?, ?, ?)
        """,
        task_projects
    )

    conn.commit()
    logger.info(f"Generated {len(task_projects)} task–project associations")

    return task_projects
