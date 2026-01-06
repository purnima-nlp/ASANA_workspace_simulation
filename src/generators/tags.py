import logging
import random
from uuid import uuid4

logger = logging.getLogger(__name__)

# Common workflow / domain tags (scrape-compatible fallback)
TAG_NAMES = [
    "backend",
    "frontend",
    "urgent",
    "design",
    "bug",
    "tech-debt",
    "customer-request",
    "blocked",
    "performance",
    "security",
    "documentation",
    "refactor",
    "release",
    "qa",
]


def generate_tags(conn, org_ids, n_tags: int = 12):
    """
    Generate organization-level tags.

    Seed methodology implemented:
    - UUIDv4 tag IDs
    - Organization-scoped
    - Common workflow and domain labels
    - Small, reusable tag vocabulary
    """
    cursor = conn.cursor()
    tags = []

    org_id = org_ids[0]

    # Limit tags to realistic vocabulary size
    selected_tags = random.sample(
        TAG_NAMES,
        k=min(n_tags, len(TAG_NAMES))
    )

    for name in selected_tags:
        tags.append((
            str(uuid4()),  # tag_id
            org_id,        # org_id
            name           # name
        ))

    cursor.executemany(
        """
        INSERT INTO tags (
            tag_id,
            org_id,
            name
        )
        VALUES (?, ?, ?)
        """,
        tags
    )

    conn.commit()
    logger.info(f"Generated {len(tags)} tags")

    return [
        {
            "tag_id": t[0],
            "org_id": t[1],
            "name": t[2],
        }
        for t in tags
    ]
