from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.db_model import User


async def get_by_username(db: AsyncSession, username: str):
    try:
        result = await db.execute(select(User).where(username == User.username))
        return result.scalars().first()
    except Exception as e:
        raise e


async def get_by_email(db: AsyncSession, email: str):
    try:
        result = await db.execute(select(User).where(email == User.email))
        return result.scalars().first()
    except Exception as e:
        raise e


async def get_by_id(db: AsyncSession, id: int):
    try:
        result = await db.execute(select(User).where(id == User.id))
        return result.scalars().first()
    except Exception as e:
        raise e


async def create_user(db: AsyncSession, user: User):
    try:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    except Exception as e:
        raise e
