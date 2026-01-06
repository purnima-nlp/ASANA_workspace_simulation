import logging
import random
from datetime import datetime, timedelta
from uuid import uuid4
import math

logger = logging.getLogger(__name__)

# -------- Task name templates (LLM-compatible fallback) -------- #

ENGINEERING_TASKS = [
    "API – Refactor – Authentication",
    "Backend – Optimize – Query Performance",
    "Infra – Migrate – Kubernetes Cluster",
    "ML – Improve – Model Accuracy",
    "Platform – Fix – Rate Limiting Bug",
]

MARKETING_TASKS = [
    "Campaign – Launch – Q{q} Growth",
    "Content – Publish – Blog Series",
    "SEO – Optimize – Landing Pages",
    "Email – Design – Drip Campaign",
]

OPERATIONS_TASKS = [
    "Ops – Review – Internal Processes",
    "Compliance – Audit – Security Controls",
    "Support – Triage – Escalations",
]

TASK_POOLS = {
    "engineering": ENGINEERING_TASKS,
    "marketing": MARKETING_TASKS,
    "operations": OPERATIONS_TASKS,
}

PRIORITY_WEIGHTS = {
    "engineering": ["high", "medium", "medium", "low"],
    "marketing": ["medium", "medium", "low"],
    "operations": ["medium", "low"],
}


# -------- Helper functions -------- #

def weekday_biased_date(start: datetime, end: datetime) -> datetime:
    """
    Bias task creation toward Mon–Wed.
    """
    while True:
        delta = end - start
        candidate = start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))
        if candidate.weekday() <= 2:  # Mon–Wed
            return candidate


def sample_due_date(created_at: datetime):
    r = random.random()
    if r < 0.10:
        return None
    elif r < 0.35:
        return created_at + timedelta(days=random.randint(1, 7))
    elif r < 0.75:
        return created_at + timedelta(days=random.randint(8, 30))
    elif r < 0.95:
        return created_at + timedelta(days=random.randint(31, 90))
    else:
        return created_at - timedelta(days=random.randint(1, 14))  # overdue


def sample_completed_at(created_at: datetime):
    # Log-normal-ish distribution
    days = int(math.exp(random.uniform(0.5, 2.5)))
    return created_at + timedelta(days=days)


def sample_description():
    r = random.random()
    if r < 0.20:
        return None
    elif r < 0.70:
        return "Follow up on this task and ensure timely completion."
    else:
        return (
            "- Review requirements\n"
            "- Coordinate with stakeholders\n"
            "- Implement changes\n"
            "- Validate results"
        )


# -------- Main generator -------- #

def generate_tasks(
    conn,
    org_ids,
    users,
    teams,
    projects,
    n_tasks_per_project: int = 40
):
    """
    Generate tasks with realistic distributions, hierarchy, and temporal logic.
    """
    cursor = conn.cursor()
    tasks = []

    org_id = org_ids[0]

    # Map users by team for weighted assignment
    team_users = {}
    for team in teams:
        team_users[team["team_id"]] = [
            u["user_id"] for u in users
            if u["user_id"]  # simple, refined later via memberships
        ]

    now = datetime.utcnow()

    # -------- First pass: create top-level tasks -------- #
    for project in projects:
        project_type = project.get("project_type", "engineering")
        team_id = project["team_id"]

        for _ in range(n_tasks_per_project):
            task_id = str(uuid4())

            created_at = weekday_biased_date(
                now - timedelta(days=180),
                now
            )

            due_date = sample_due_date(created_at)

            completed = random.random() < 0.65
            completed_at = sample_completed_at(created_at) if completed else None

            if completed_at and completed_at > now:
                completed_at = None

            status = (
                "completed" if completed_at
                else "in_progress" if due_date and due_date < now
                else "todo"
            )

            name = random.choice(
                TASK_POOLS.get(project_type, ENGINEERING_TASKS)
            ).format(q=random.randint(1, 4))

            priority = random.choice(
                PRIORITY_WEIGHTS.get(project_type, ["medium"])
            )

            assignee_id = random.choice(users)["user_id"] if random.random() < 0.85 else None

            tasks.append({
                "task_id": task_id,
                "org_id": org_id,
                "parent_task_id": None,
                "name": name,
                "description": sample_description(),
                "assignee_id": assignee_id,
                "due_date": due_date.date().isoformat() if due_date else None,
                "priority": priority,
                "status": status,
                "created_at": created_at.isoformat(),
                "completed_at": completed_at.isoformat() if completed_at else None,
            })

    # -------- Second pass: create subtasks (25–35%) -------- #
    n_subtasks = int(len(tasks) * random.uniform(0.25, 0.35))
    parents = random.sample(tasks, n_subtasks)

    for parent in parents:
        subtask = parent.copy()
        subtask["task_id"] = str(uuid4())
        subtask["parent_task_id"] = parent["task_id"]
        subtask["name"] = f"Subtask – {parent['name']}"
        subtask["created_at"] = (
            datetime.fromisoformat(parent["created_at"]) +
            timedelta(days=random.randint(0, 3))
        ).isoformat()

        tasks.append(subtask)

    # -------- Insert into DB -------- #
    cursor.executemany(
        """
        INSERT INTO tasks (
            task_id,
            org_id,
            parent_task_id,
            name,
            description,
            assignee_id,
            due_date,
            priority,
            status,
            created_at,
            completed_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                t["task_id"],
                t["org_id"],
                t["parent_task_id"],
                t["name"],
                t["description"],
                t["assignee_id"],
                t["due_date"],
                t["priority"],
                t["status"],
                t["created_at"],
                t["completed_at"],
            )
            for t in tasks
        ]
    )

    conn.commit()
    logger.info(f"Generated {len(tasks)} tasks")

    return tasks
