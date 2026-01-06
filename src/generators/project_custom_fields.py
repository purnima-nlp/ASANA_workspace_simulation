import logging
import random

logger = logging.getLogger(__name__)


def generate_project_custom_fields(
    conn,
    projects,
    custom_fields
):
    """
    Generate project-specific custom field enablement.

    Seed methodology implemented:
    - Projects enable a subset of organization-level custom fields
    - Engineering projects more likely to have required fields
    - Non-engineering projects have fewer required fields
    """
    cursor = conn.cursor()
    project_custom_fields = []

    for project in projects:
        project_id = project["project_id"]
        project_type = project.get("project_type", "engineering")

        # Decide how many fields this project enables
        # Engineering projects track more metadata
        if project_type == "engineering":
            n_fields = random.randint(3, min(6, len(custom_fields)))
            required_prob = 0.5
        else:
            n_fields = random.randint(1, min(4, len(custom_fields)))
            required_prob = 0.2

        enabled_fields = random.sample(custom_fields, n_fields)

        for field in enabled_fields:
            field_id = field["field_id"]

            is_required = (
                1 if random.random() < required_prob else 0
            )

            project_custom_fields.append((
                project_id,
                field_id,
                is_required
            ))

    cursor.executemany(
        """
        INSERT INTO project_custom_fields (
            project_id,
            field_id,
            is_required
        )
        VALUES (?, ?, ?)
        """,
        project_custom_fields
    )

    conn.commit()
    logger.info(
        f"Generated {len(project_custom_fields)} project custom field mappings"
    )

    return project_custom_fields
