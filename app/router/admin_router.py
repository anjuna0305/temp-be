from typing import Annotated

from fastapi import APIRouter, Depends, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

import app.service.admin_service as admin_service
from app.config.database.postgres_config import get_db
from app.schema.request.request_schema import CreateProjectRequest

router = APIRouter()


@router.get("/project")
async def get_all_projects(db: AsyncSession = Depends(get_db)):
    try:
        result = await admin_service.get_projects(db)
        return result
    except Exception as e:
        raise e


@router.get("/project/{project_id}")
async def get_all_projects(project_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await admin_service.get_project_by_id(project_id, db)
        return result
    except Exception as e:
        raise e


@router.patch("/project/{project_id}/publish")
async def get_all_projects(project_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await admin_service.publish_project(project_id, db)
        return result
    except Exception as e:
        raise e


@router.patch("/project/{project_id}/unpublish")
async def get_all_projects(project_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await admin_service.unpublish_project(project_id, db)
        return result
    except Exception as e:
        raise e


@router.get("/project/{project_id}/source_sentence_count")
async def get_all_projects(project_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await admin_service.get_project_source_count(project_id, db)
        return result
    except Exception as e:
        raise e


@router.get("/project/{project_id}/response_count")
async def get_all_projects(project_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await admin_service.get_project_response_count(project_id, db)
        return result
    except Exception as e:
        raise e


@router.post("/project/new")
async def crate_new_project(
    req_data: CreateProjectRequest, db: AsyncSession = Depends(get_db)
):
    try:
        result = await admin_service.create_new_project(db, req_data)
        return result
    except Exception as e:
        raise e


@router.post("/add_sentence")
async def add_source_sentence(
    project_id: int, file: Annotated[bytes, File()], db: AsyncSession = Depends(get_db)
):
    try:
        result = await admin_service.add_source_sentence(db, project_id, file)
        return result
    except Exception as e:
        raise e


@router.get("/responses")
async def get_project_responses(project_id: int, db: AsyncSession = Depends(get_db)):
    try:
        zip_path = await admin_service.get_responses(db, project_id)
        return FileResponse(
            path=zip_path, filename="files.zip", media_type="application/zip"
        )
    except Exception as e:
        raise e


@router.get("/responsed-users/{project_id}")
async def get_project_responses(project_id: int, db: AsyncSession = Depends(get_db)):
    try:
        users = await admin_service.get_responsed_users(db, project_id)
        return users
    except Exception as e:
        raise e


@router.get("/responses/{project_id}")
async def get_project_responses(
    project_id: int,
    user_id: int = Query(None, description="The ID of the user. Optional."),
    db: AsyncSession = Depends(get_db),
):
    try:
        if user_id is None:
            print("function called 4!\n\n\n\n\n\n")
            zip_path = await admin_service.get_responses_by_users(db, project_id)
        else:
            print("function called 1!\n\n\n\n\n\n")
            zip_path = await admin_service.get_responses_by_user_id(
                db, project_id, user_id
            )

        return FileResponse(
            path=zip_path, filename="files.zip", media_type="application/zip"
        )
    except Exception as e:
        raise e
