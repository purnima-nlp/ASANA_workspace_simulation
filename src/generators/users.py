import logging
import random
from datetime import datetime, timedelta
from uuid import uuid4

from faker import Faker

logger = logging.getLogger(__name__)
fake = Faker()

# Role distribution as per methodology
ROLE_DISTRIBUTION = (
    ["admin"] * 5 +
    ["member"] * 85 +
    ["guest"] * 10
)

# Active user probability range (92–96%)
ACTIVE_PROBABILITY_RANGE = (0.92, 0.96)


def random_created_at(org_created_at: str) -> str:
    """
    Generate a user creation timestamp after organization creation.
    Simulates hiring bursts over the organization's lifetime.
    """
    org_start = datetime.fromisoformat(org_created_at)
    now = datetime.utcnow()

    # Hiring bursts: skew toward recent years
    if random.random() < 0.6:
        # Recent hires (last 2 years)
        start = max(org_start, now - timedelta(days=2 * 365))
    else:
        # Older hires
        start = org_start

    delta_seconds = int((now - start).total_seconds())
    return (start + timedelta(seconds=random.randint(0, delta_seconds))).isoformat()


def generate_users(conn, org_ids, n_users: int = 800):
    """
    Generate users for the organization.

    Seed methodology implemented:
    - UUIDv4 user IDs
    - Email + full name realism
    - Role distribution (admin/member/guest)
    - Hiring timeline over org lifetime
    - Realistic attrition (92–96% active)
    """
    cursor = conn.cursor()
    users = []

    # Single organization assumed, but supports extension
    org_id = org_ids[0]

    # Fetch organization creation time
    cursor.execute(
        "SELECT created_at FROM organizations WHERE org_id = ?",
        (org_id,)
    )
    org_created_at = cursor.fetchone()["created_at"]

    active_probability = random.uniform(*ACTIVE_PROBABILITY_RANGE)

    for _ in range(n_users):
        user_id = str(uuid4())
        full_name = fake.name()
        first, last = full_name.lower().split(" ", 1)

        email = f"{first}.{last}{random.randint(1,9999)}@example.com"

        role = random.choice(ROLE_DISTRIBUTION)
        created_at = random_created_at(org_created_at)

        is_active = 1 if random.random() < active_probability else 0

        users.append((
            user_id,
            org_id,
            email,
            full_name,
            role,
            created_at,
            is_active
        ))

    cursor.executemany(
        """
        INSERT INTO users (
            user_id,
            org_id,
            email,
            full_name,
            role,
            created_at,
            is_active
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        users
    )

    conn.commit()
    logger.info(f"Generated {len(users)} users")

    return [user[0] for user in users]
