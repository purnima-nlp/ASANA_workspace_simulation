import logging
import random
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Enum value pools (Asana-style)
ENUM_VALUES = {
    "Priority": ["Low", "Medium", "High", "Critical"],
    "Severity": ["Minor", "Major", "Critical"],
    "Risk Level": ["Low", "Medium", "High"],
    "Approval Status": ["Pending", "Approved", "Rejected"],
}

DEFAULT_ENUM = ["Low", "Medium", "High"]


def generate_value(field, required: bool):
    """
    Generate a value consistent with field type and sparsity.
    """
    # Sparsity: optional fields often missing
    if not required and random.random() < 0.35:
        return None, None, None, None

    field_type = field["field_type"]
    field_name = field["name"]

    if field_type == "enum":
        values = ENUM_VALUES.get(field_name, DEFAULT_ENUM)
        return random.choice(values), None, None, None

    if field_type == "number":
        return None, random.randint(1, 20), None, None

    if field_type == "text":
        return None, None, random.choice(
            ["Low effort", "Needs review", "Customer facing", "Internal"]
        ), None

    if field_type == "date":
        future_days = random.randint(1, 90)
        return None, None, None, (
            datetime.utcnow() + timedelta(days=future_days)
        ).date().isoformat()

    return None, None, None, None


def generate_custom_field_values(
    conn,
    tasks,
    project_custom_fields,
    custom_fields
):
    """
    Generate task-level custom field values.

    Seed methodology implemented:
    - Only fields enabled on a task's project are populated
    - Required fields always populated
    - Optional fields are sparse
    - Values respect field type
    """
    cursor = conn.cursor()
    values = []

    # Lookup maps
    field_map = {f["field_id"]: f for f in custom_fields}

    project_field_map = {}
    for pcf in project_custom_fields:
        project_id, field_id, is_required = pcf
        project_field_map.setdefault(project_id, []).append(
            (field_id, bool(is_required))
        )

    # Build task -> project mapping
    cursor.execute(
        "SELECT task_id, project_id FROM task_projects"
    )
    task_project_map = cursor.fetchall()

    task_to_projects = {}
    for row in task_project_map:
        task_to_projects.setdefault(row["task_id"], set()).add(row["project_id"])

    for task in tasks:
        task_id = task["task_id"]

        for project_id in task_to_projects.get(task_id, []):
            for field_id, is_required in project_field_map.get(project_id, []):
                field = field_map[field_id]

                enum_val, num_val, text_val, date_val = generate_value(
                    field,
                    is_required
                )

                # Skip if optional and not populated
                if all(v is None for v in [enum_val, num_val, text_val, date_val]):
                    continue

                values.append((
                    task_id,
                    field_id,
                    text_val,
                    num_val,
                    date_val,
                    enum_val
                ))

    cursor.executemany(
        """
        INSERT INTO custom_field_values (
            task_id,
            field_id,
            value_text,
            value_number,
            value_date,
            value_enum
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        values
    )

    conn.commit()
    logger.info(f"Generated {len(values)} custom field values")

    return values
