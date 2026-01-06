import logging
import random
from datetime import datetime, timedelta
from uuid import uuid4

logger = logging.getLogger(__name__)

# YC / Crunchbase–style B2B SaaS company names
# (scrape-compatible fallback; can be replaced by cached scraper output)
COMPANY_NAMES = [
    "CloudNova",
    "DataFlux",
    "ScaleOps",
    "InfraStack",
    "Productify",
    "GrowthLoop",
    "MetricHive",
    "Launchpad Systems",
    "SignalWorks",
    "VertexAI Labs"
]


def random_created_at(min_years_ago=3, max_years_ago=7) -> str:
    """
    Generate an ISO-8601 timestamp between 3–7 years in the past.
    """
    now = datetime.utcnow()
    days_ago = random.randint(min_years_ago * 365, max_years_ago * 365)
    return (now - timedelta(days=days_ago)).isoformat()


def generate_organizations(conn, n_orgs: int = 1):
    """
    Generate organization/workspace records.

    Seed methodology:
    - UUIDv4 org_id
    - YC/Crunchbase-style SaaS names
    - Enterprise plan
    - Created 3–7 years ago
    - Always active
    """
    cursor = conn.cursor()
    rows = []

    for _ in range(n_orgs):
        rows.append((
            str(uuid4()),                 # org_id
            random.choice(COMPANY_NAMES), # name
            "enterprise",                 # plan_type
            random_created_at(),          # created_at
            1                             # is_active
        ))

    cursor.executemany(
        """
        INSERT INTO organizations (
            org_id,
            name,
            plan_type,
            created_at,
            is_active
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        rows
    )

    conn.commit()
    logger.info(f"Generated {len(rows)} organization(s)")

    # Return org_ids for downstream generators
    return [row[0] for row in rows]

