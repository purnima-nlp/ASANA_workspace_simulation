import logging
import random
from uuid import uuid4

logger = logging.getLogger(__name__)

# Standard workflow sections
STANDARD_SECTIONS = [
    "To Do",
    "In Progress",
    "Blocked",
    "Done"
]

# Optional non-standard sections to increase diversity
NON_STANDARD_SECTIONS = [
    "Design Review",
    "QA",
    "Code Review",
    "Ready for Release",
    "Waiting on Dependencies",
    "Backlog"
]


def generate_sections(conn, projects):
    """
    Generate sections for each project.

    Seed methodology implemented:
    - UUIDv4 section IDs
    - Project-scoped sections
    - Common workflow templates
    - Sequential ordering
    - Occasional non-standard sections for realism
    """
    cursor = conn.cursor()
    sections = []

    for project in projects:
        project_id = project["project_id"]

        # Decide whether to include non-standard sections
        include_non_standard = random.random() < 0.3  # ~30% projects

        section_names = STANDARD_SECTIONS.copy()

        if include_non_standard:
            extra_sections = random.sample(
                NON_STANDARD_SECTIONS,
                k=random.randint(1, 2)
            )
            # Insert extras between In Progress and Done
            insert_pos = section_names.index("In Progress") + 1
            section_names[insert_pos:insert_pos] = extra_sections

        for position, name in enumerate(section_names, start=1):
            sections.append((
                str(uuid4()),   # section_id
                project_id,     # project_id
                name,           # name
                position        # position
            ))

    cursor.executemany(
        """
        INSERT INTO sections (
            section_id,
            project_id,
            name,
            position
        )
        VALUES (?, ?, ?, ?)
        """,
        sections
    )

    conn.commit()
    logger.info(f"Generated {len(sections)} sections")

    return sections
