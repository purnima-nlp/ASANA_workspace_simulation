import logging
import random
from datetime import datetime, timedelta
from uuid import uuid4

from utils.config import USE_SCRAPERS
from scrapers.company_names import get_company_names

logger = logging.getLogger(__name__)

# Fallback YC / Crunchbase–style B2B SaaS company names
FALLBACK_COMPANY_NAMES = [
    "CloudNova",
    "DataFlux",
    "ScaleOps",
    "InfraStack",
    "Productify",
    "GrowthLoop",
    "MetricHive",
    "Launchpad Systems",
    "SignalWorks",
    "VertexAI Labs",
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
    - Company names sampled from public tech company corpus
      (scraped when enabled, fallback otherwise)
    - Enterprise plan
    - Created 3–7 years ago
    - Always active
    """
    cursor = conn.cursor()
    rows = []

    # ----------------------------
    # Choose company name source
    # ----------------------------
    if USE_SCRAPERS:
        company_names = get_company_names(limit=100)
        logger.info(
            f"Using scraped company names ({len(company_names)} available)"
        )
    else:
        company_names = FALLBACK_COMPANY_NAMES
        logger.info("Using fallback company names")

    for _ in range(n_orgs):
        rows.append((
            str(uuid4()),                       # org_id
            random.choice(company_names),       # name
            "enterprise",                       # plan_type
            random_created_at(),                # created_at
            1                                   # is_active
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

