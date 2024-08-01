from typing import Annotated

from fastapi import APIRouter, Depends, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

import app.service.admin_service as admin_service
from app.config.database.postgres_config import get_db
from app.schema.request.request_schema import CreateProjectRequest
import app.crud.response_sentence_crud as res_crud

router = APIRouter()


@router.get("/")
async def get_all_projects(db: AsyncSession = Depends(get_db)):
    return "hello"


@router.get("/user-id")
async def get_all_user_id(project_id: int, db: AsyncSession = Depends(get_db)):
    result = await res_crud.get_responded_users(db, project_id)
    return result
