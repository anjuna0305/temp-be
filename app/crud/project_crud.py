from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.db_model import Project


async def get_by_name(db: AsyncSession, project_name: str):
    try:
        result = await db.execute(
            select(Project).where(project_name == Project.project_name)
        )
        return result.scalars().first()
    except Exception as e:
        raise e


async def get_by_id(db: AsyncSession, project_id: int):
    try:
        result = await db.execute(
            select(Project).where(project_id == Project.project_id)
        )
        return result.scalars().first()
    except Exception as e:
        raise e


async def create(db: AsyncSession, project: Project):
    try:
        db.add(project)
        await db.commit()
        await db.refresh(project)
        return project
    except Exception as e:
        raise e
