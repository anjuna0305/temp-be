from typing import Annotated

from fastapi import APIRouter, Depends, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

import app.service.admin_service as admin_service
from app.config.database.postgres_config import get_db
from app.schema.request.request_schema import (
    CreateProjectRequest
)

router = APIRouter()


@router.post("/project/new")
async def crate_new_project(req_data: CreateProjectRequest, db: AsyncSession = Depends(get_db)):
    try:
        result = admin_service.create_new_project(db, req_data)
    except Exception as e:
        raise e


@router.post("/add_sentence")
async def add_source_sentence(project_id: int, file: Annotated[bytes, File()], db: AsyncSession = Depends(get_db)):
    try:
        result = await admin_service.add_source_sentence(db, project_id, file)
        return result
    except Exception as e:
        raise e


@router.get("/responses")
async def get_project_responses(project_id: int, db: AsyncSession = Depends(get_db)):
    try:
        zip_path = await admin_service.get_responses(db, project_id)
        return FileResponse(path=zip_path, filename="files.zip", media_type="application/zip")
    except Exception as e:
        raise e