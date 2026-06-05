"""Seed database with demo data on startup.

Flow:
  1. Create users in Keycloak (get real UUIDs)
  2. Insert DB records using those UUIDs
"""

from db.seed._interactions import seed_interactions
from db.seed._keycloak import seed_keycloak_users
from db.seed._relationships import seed_relationships
from db.seed._subjects_tags import seed_subjects_and_tags
from db.seed._users import seed_users
from db.session import AsyncSessionLocal
from models.tables import Subject
from sqlalchemy import func, select


async def _table_empty() -> bool:
    """Return True if the subjects table is empty."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(func.count()).select_from(Subject))
        return result.scalar() == 0


async def seed_database() -> None:
    """
    Seed the database and create Keycloak users on startup.

    Keycloak users (teach / sud) are created every time the app starts,
    even if the DB already has data — this ensures login always works.
    """
    # Always ensure Keycloak users exist (needed for login)
    user_uuids = await seed_keycloak_users()

    # Seed DB only if empty
    if await _table_empty():
        print("Seed: populating demo data …")

        async with AsyncSessionLocal() as session:
            seed_subjects_and_tags(session)
            await session.flush()

            seed_users(session, user_uuids)
            await session.flush()

            seed_relationships(session, user_uuids)
            await seed_interactions(session, user_uuids)

            await session.commit()

        print("Seed: demo data inserted successfully.")
    else:
        print("Seed: database already contains data — skipping DB seed.")
