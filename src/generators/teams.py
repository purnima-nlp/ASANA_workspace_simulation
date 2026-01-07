import logging
import random
from datetime import datetime, timedelta
from uuid import uuid4

logger = logging.getLogger(__name__)

# Functional team name templates (scrape-compatible, realistic)
TEAM_NAME_TEMPLATES = [
    "Backend Engineering",
    "Frontend Engineering",
    "Platform Engineering",
    "Infrastructure",
    "Data Engineering",
    "Machine Learning",
    "Product Engineering",
    "Growth Marketing",
    "Marketing Operations",
    "Customer Success",
    "Sales Operations",
    "Developer Experience",
    "Security Engineering",
    "QA & Release",
    "Internal Tools"
]

# Team size distribution (will be used later in team_memberships)
TEAM_SIZE_BUCKETS = [
    ("small", 0.25, (5, 10)),
    ("medium", 0.50, (10, 30)),
    ("large", 0.25, (30, 80)),
]


def random_created_at(org_created_at: str) -> str:
    """
    Generate a team creation timestamp after organization creation.
    Teams tend to form during re-org events, not uniformly.
    """
    org_start = datetime.fromisoformat(org_created_at)
    now = datetime.utcnow()

    # Re-org clustering: prefer mid-life of organization
    org_lifetime_days = (now - org_start).days
    midpoint = org_start + timedelta(days=org_lifetime_days // 2)

    # Bias creation around midpoint ± 1 year
    window_start = max(org_start, midpoint - timedelta(days=365))
    window_end = min(now, midpoint + timedelta(days=365))

    delta_seconds = int((window_end - window_start).total_seconds())
    return (window_start + timedelta(seconds=random.randint(0, delta_seconds))).isoformat()


def sample_team_size():
    """
    Sample a team size bucket according to industry distribution.
    """
    r = random.random()
    cumulative = 0.0
    for _, prob, size_range in TEAM_SIZE_BUCKETS:
        cumulative += prob
        if r <= cumulative:
            return random.randint(*size_range)

    # Fallback (should not happen)
    return random.randint(10, 30)


def generate_teams(conn, org_ids, n_teams: int = 40):
    """
    Generate teams for the organization.

    Seed methodology implemented:
    - UUIDv4 team IDs
    - Functional team names (safe for > template count)
    - Organization-scoped
    - Created after org creation, clustered around re-org events
    - Team size distribution recorded for downstream membership generation
    """
    cursor = conn.cursor()
    teams = []

    org_id = org_ids[0]

    # Fetch organization creation time
    cursor.execute(
        "SELECT created_at FROM organizations WHERE org_id = ?",
        (org_id,)
    )
    org_created_at = cursor.fetchone()["created_at"]

    # Track how many times each base name has been used
    name_counts = {}

    for _ in range(n_teams):
        team_id = str(uuid4())

        base_name = random.choice(TEAM_NAME_TEMPLATES)
        count = name_counts.get(base_name, 0)

        if count == 0:
            name = base_name
        else:
            name = f"{base_name} {count + 1}"

        name_counts[base_name] = count + 1

        created_at = random_created_at(org_created_at)

        teams.append({
            "team_id": team_id,
            "org_id": org_id,
            "name": name,
            "created_at": created_at,
            "target_size": sample_team_size()
        })

    cursor.executemany(
        """
        INSERT INTO teams (
            team_id,
            org_id,
            name,
            created_at
        )
        VALUES (?, ?, ?, ?)
        """,
        [
            (t["team_id"], t["org_id"], t["name"], t["created_at"])
            for t in teams
        ]
    )

    conn.commit()
    logger.info(f"Generated {len(teams)} teams")

    # Return full team metadata for team_memberships generator
    return teams

