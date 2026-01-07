import logging
import random
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def random_joined_at(user_created_at: str, team_created_at: str) -> str:
    """
    joined_at must be after BOTH user creation and team creation.
    """
    start = max(
        datetime.fromisoformat(user_created_at),
        datetime.fromisoformat(team_created_at)
    )
    now = datetime.utcnow()

    delta_seconds = int((now - start).total_seconds())
    return (start + timedelta(seconds=random.randint(0, delta_seconds))).isoformat()


def generate_team_memberships(conn, users, teams):
    """
    Generate team memberships.

    Seed methodology implemented:
    - Users belong to 1–3 teams
    - Team size distribution respected via teams' target_size
    - 5–10% team leads per team
    - joined_at after user & team creation
    """
    cursor = conn.cursor()
    memberships = []

    # Build lookup maps
    user_created_map = {u["user_id"]: u["created_at"] for u in users}
    team_created_map = {t["team_id"]: t["created_at"] for t in teams}

    user_ids = list(user_created_map.keys())
    user_id_set = set(user_ids)

    # Track current membership counts per team (USE SETS)
    team_members = {t["team_id"]: set() for t in teams}

    # First pass: assign users to teams (1–3 teams per user)
    for user_id in user_ids:
        n_teams = random.choices(
            [1, 2, 3],
            weights=[0.6, 0.3, 0.1]
        )[0]

        selected_teams = random.sample(teams, k=min(n_teams, len(teams)))

        for team in selected_teams:
            team_members[team["team_id"]].add(user_id)

    # Second pass: enforce team size targets (soft constraint)
    for team in teams:
        team_id = team["team_id"]
        target_size = team["target_size"]
        members = team_members[team_id]

        if len(members) > target_size:
            team_members[team_id] = set(random.sample(list(members), target_size))

        elif len(members) < target_size:
            needed = target_size - len(members)
            available_users = list(user_id_set - members)

            if available_users:
                additional_users = random.sample(
                    available_users,
                    k=min(needed, len(available_users))
                )
                members.update(additional_users)

    # Final pass: create membership rows and assign roles
    for team in teams:
        team_id = team["team_id"]
        members = list(team_members[team_id])

        if not members:
            continue

        # Determine number of leads (5–10%)
        n_leads = max(1, int(len(members) * random.uniform(0.05, 0.10)))
        leads = set(random.sample(members, n_leads))

        for user_id in members:
            role = "lead" if user_id in leads else "member"

            joined_at = random_joined_at(
                user_created_map[user_id],
                team_created_map[team_id]
            )

            memberships.append((
                team_id,
                user_id,
                role,
                joined_at
            ))

    cursor.executemany(
        """
        INSERT INTO team_memberships (
            team_id,
            user_id,
            role,
            joined_at
        )
        VALUES (?, ?, ?, ?)
        """,
        memberships
    )

    conn.commit()
    logger.info(f"Generated {len(memberships)} team memberships")

    return memberships

