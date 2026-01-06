import logging
import random
from datetime import datetime, timedelta
from uuid import uuid4

logger = logging.getLogger(__name__)

# Common Asana-style custom field names (scrape-compatible fallback)
CUSTOM_FIELD_NAMES = [
    "Priority",
    "Effort",
    "Story Points",
    "Severity",
    "Customer Impact",
    "Risk Level",
    "Time Estimate",
    "Confidence",
    "Release Version",
    "Approval Status",
]

# Field type distribution: enum > number > text > date
FIELD_TYPE_DISTRIBUTION = [
    ("enum", 0.45),
    ("number", 0.30),
    ("text", 0.15),
    ("date", 0.10),
]


def sample_field_type():
    r = random.random()
    cumulative = 0.0
    for field_type, prob in FIELD_TYPE_DISTRIBUTION:
        cumulative += prob
        if r <= cumulative:
            return field_type
    return "enum"


def random_early_date(org_created_at: str) -> str:
    """
    Generate a timestamp early in the organization lifecycle
    (within first 6–18 months).
    """
    org_start = datetime.fromisoformat(org_created_at)
    early_window_end = org_start + timedelta(days=random.randint(180, 540))
    return early_window_end.isoformat()


def generate_custom_field_definitions(
    conn,
    org_ids,
    n_fields: int = 8
):
    """
    Generate custom field definitions.

    Seed methodology implemented:
    - UUIDv4 field IDs
    - Organization-scoped
    - Asana-like field names
    - Field type distribution (enum > number > text > date)
    - Created early in org lifecycle
    """
    cursor = conn.cursor()
    fields = []

    org_id = org_ids[0]

    # Fetch organization creation time
    cursor.execute(
        "SELECT created_at FROM organizations WHERE org_id = ?",
        (org_id,)
    )
    org_created_at = cursor.fetchone()["created_at"]

    used_names = set()

    for _ in range(n_fields):
        field_id = str(uuid4())

        # Avoid duplicate field names
        name = random.choice(CUSTOM_FIELD_NAMES)
        while name in used_names:
            name = random.choice(CUSTOM_FIELD_NAMES)
        used_names.add(name)

        field_type = sample_field_type()
        created_at = random_early_date(org_created_at)

        fields.append((
            field_id,
            org_id,
            name,
            field_type,
            created_at
        ))

    cursor.executemany(
        """
        INSERT INTO custom_field_definitions (
            field_id,
            org_id,
            name,
            field_type,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        fields
    )

    conn.commit()
    logger.info(f"Generated {len(fields)} custom field definitions")

    return [
        {
            "field_id": f[0],
            "org_id": f[1],
            "name": f[2],
            "field_type": f[3],
            "created_at": f[4],
        }
        for f in fields
    ]
