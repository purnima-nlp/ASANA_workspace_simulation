import logging
import random
from datetime import datetime, timedelta
from uuid import uuid4

logger = logging.getLogger(__name__)

# Project type templates (scrape + LLM compatible fallback)
PROJECT_TEMPLATES = {
    "engineering": [
        "Q{q} Platform Stability Sprint",
        "Core API Refactor – Q{q}",
        "Infra Reliability Improvements",
        "Tech Debt Reduction Sprint",
        "ML Pipeline Optimization"
    ],
    "product": [
        "New Feature Launch – {name}",
        "Beta Release: {name}",
        "Product Roadmap Q{q}",
        "User Feedback Integration"
    ],
    "marketing": [
        "Q{q} Growth Campaign",
        "Product Launch Marketing – {name}",
        "SEO & Content Revamp",
        "Demand Gen Campaign"
    ],
    "operations": [
        "Internal Tools Cleanup",
        "Operational Backlog",
        "Process Automation Initiative",
        "Compliance & Security Tasks"
    ],
}

PROJECT_TYPE_DISTRIBUTION = [
    ("engineering", 0.45),
    ("product", 0.25),
    ("marketing", 0.20),
    ("operations", 0.10),
]


def sample_project_type():
    r = random.random()
    cumulative = 0.0
    for project_type, prob in PROJECT_TYPE_DISTRIBUTION:
        cumulative += prob
        if r <= cumulative:
            return project_type
    return "engineering"


def random_quarter_date(years_back: int = 3) -> str:
    """
    Generate a timestamp clustered around quarterly planning cycles.
    """
    now = datetime.utcnow()
    start_year = now.year - years_back
    year = random.randint(start_year, now.year)

    quarter_start_month = random.choice([1, 4, 7, 10])
    quarter_start = datetime(year, quarter_start_month, 1)

    offset_days = random.randint(0, 30)
    created_at = quarter_start + timedelta(days=offset_days)

    return min(created_at, now).isoformat()


def maybe_due_date(created_at: str) -> str | None:
    """
    ~60% of projects have due dates, aligned to quarter/sprint horizons.
    """
    if random.random() > 0.6:
        return None

    start = datetime.fromisoformat(created_at)

    # Project durations: 1–6 months
    duration_days = random.choice([30, 60, 90, 120, 180])
    return (start + timedelta(days=duration_days)).date().isoformat()


def generate_project_name(project_type: str) -> str:
    template = random.choice(PROJECT_TEMPLATES[project_type])
    quarter = random.randint(1, 4)
    feature_name = random.choice(
        ["Atlas", "Nova", "Pulse", "Horizon", "Vertex"]
    )

    return template.format(q=quarter, name=feature_name)


def generate_projects(conn, teams, projects_per_team: int = 4):
    """
    Generate projects owned by teams.

    Seed methodology implemented:
    - UUIDv4 project IDs
    - One owning team per project
    - Realistic project names by type
    - 65% active / 35% archived
    - Created around quarterly planning cycles
    - ~60% projects have due dates
    """
    cursor = conn.cursor()
    projects = []

    for team in teams:
        team_id = team["team_id"]

        for _ in range(projects_per_team):
            project_type = sample_project_type()
            created_at = random_quarter_date()
            status = "active" if random.random() < 0.65 else "archived"

            projects.append({
                "project_id": str(uuid4()),
                "team_id": team_id,
                "name": generate_project_name(project_type),
                "status": status,
                "created_at": created_at,
                "due_date": maybe_due_date(created_at),
                "project_type": project_type,
            })

    cursor.executemany(
        """
        INSERT INTO projects (
            project_id,
            team_id,
            name,
            status,
            created_at,
            due_date
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                p["project_id"],
                p["team_id"],
                p["name"],
                p["status"],
                p["created_at"],
                p["due_date"],
            )
            for p in projects
        ]
    )

    conn.commit()
    logger.info(f"Generated {len(projects)} projects")

    return projects
