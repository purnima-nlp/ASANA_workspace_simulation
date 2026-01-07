import logging
import random
from datetime import datetime, timedelta
from uuid import uuid4

logger = logging.getLogger(__name__)

# LLM-compatible fallback comment templates
COMMENT_TEMPLATES = [
    "Looks good to me.",
    "Can you clarify the requirements here?",
    "I’ve pushed a fix for this.",
    "Blocking on input from another team.",
    "This should be ready for review.",
    "Any updates on this?",
    "Approved 👍",
    "Let’s sync offline on this.",
    "I’ll take this up next.",
    "Resolved, closing this task."
]


def random_comment_time(task_created_at: str, task_completed_at: str | None) -> str:
    """
    Generate a comment timestamp after task creation.
    Comments cluster near completion if task is completed.
    Safely handles temporal edge cases.
    """
    start = datetime.fromisoformat(task_created_at)
    now = datetime.utcnow()

    if task_completed_at:
        end = min(datetime.fromisoformat(task_completed_at), now)
    else:
        end = now

    delta_seconds = int((end - start).total_seconds())

    # ✅ FIX: guard against negative or zero ranges
    if delta_seconds <= 0:
        return start.isoformat()

    return (start + timedelta(seconds=random.randint(0, delta_seconds))).isoformat()


def generate_comments(
    conn,
    tasks,
    users,
    avg_comments_per_task: float = 1.8
):
    """
    Generate comments on tasks.

    Seed methodology implemented:
    - UUIDv4 comment IDs
    - Task-scoped comments
    - Author is usually assignee, else random user
    - Text variety (updates, questions, approvals)
    - created_at always after task creation
    """
    cursor = conn.cursor()
    comments = []

    user_ids = [u["user_id"] for u in users]

    for task in tasks:
        task_id = task["task_id"]

        # Poisson-like distribution for comment count
        n_comments = max(
            0,
            int(random.gauss(avg_comments_per_task, 1))
        )

        for _ in range(n_comments):
            # Prefer assignee if present
            if task["assignee_id"] and random.random() < 0.7:
                user_id = task["assignee_id"]
            else:
                user_id = random.choice(user_ids)

            comments.append((
                str(uuid4()),                     # comment_id
                task_id,                          # task_id
                user_id,                          # user_id
                random.choice(COMMENT_TEMPLATES), # body
                random_comment_time(
                    task["created_at"],
                    task["completed_at"]
                )                                 # created_at
            ))

    cursor.executemany(
        """
        INSERT INTO comments (
            comment_id,
            task_id,
            user_id,
            body,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        comments
    )

    conn.commit()
    logger.info(f"Generated {len(comments)} comments")

    return comments
