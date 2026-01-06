import logging
import random

logger = logging.getLogger(__name__)


def generate_task_tags(
    conn,
    tasks,
    tags,
    max_tags_per_task: int = 2
):
    """
    Generate task–tag associations.

    Seed methodology implemented:
    - Tags applied sparsely
    - Most tasks have 0–2 tags
    - Small subset of tasks heavily tagged
    - No duplicate (task_id, tag_id) pairs
    """
    cursor = conn.cursor()
    task_tags = []

    tag_ids = [t["tag_id"] for t in tags]

    for task in tasks:
        task_id = task["task_id"]

        # Decide how many tags to apply
        r = random.random()
        if r < 0.55:
            n_tags = 0
        elif r < 0.85:
            n_tags = 1
        else:
            n_tags = random.randint(2, max_tags_per_task)

        if n_tags == 0:
            continue

        selected_tags = random.sample(
            tag_ids,
            k=min(n_tags, len(tag_ids))
        )

        for tag_id in selected_tags:
            task_tags.append((
                task_id,
                tag_id
            ))

    cursor.executemany(
        """
        INSERT INTO task_tags (
            task_id,
            tag_id
        )
        VALUES (?, ?)
        """,
        task_tags
    )

    conn.commit()
    logger.info(f"Generated {len(task_tags)} task–tag associations")

    return task_tags
