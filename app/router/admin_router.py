from typing import Annotated

from fastapi import APIRouter, Depends, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
import tempfile
import zipfile
import os

import app.service.admin_service as admin_service
from app.config.database.postgres_config import get_db
from app.schema.request.request_schema import (
    CreateProjectRequest
)
from app.exception import InternalServerError

router = APIRouter()


@router.post("/project")
async def crate_new_project(req_data: CreateProjectRequest, db: AsyncSession = Depends(get_db)):
    try:
        result = admin_service.create_new_project(db, req_data)
    except Exception as e:
        raise e


# @router.post("/files/")
# async def create_file(file: Annotated[bytes, File()]):
#     print(f"element type {type(file)}")
#     print_file(file)
#     return {"file_size": len(file)}


def print_file(file: bytes):
    print(len(file))


@router.post("/files/")
async def create_file(project_id: int, file: Annotated[bytes, File()], db: AsyncSession = Depends(get_db)):
    try:
        result = await admin_service.add_source_sentence(db, project_id, file)
        return result
    except Exception as e:
        raise e


@router.get("/download-files/")
async def download_files():
    # Generate multiple files (for demo, create two text files)
    file1_content = "Content of file 1"
    file2_content = "Content of file 2"

    with tempfile.TemporaryDirectory() as temp_dir:
        # Write files to temporary directory
        file1_path = os.path.join(temp_dir, "file1.txt")
        file2_path = os.path.join(temp_dir, "file2.txt")

        with open(file1_path, 'w', encoding='utf-8') as file1:
            file1.write(file1_content)

        with open(file2_path, 'w', encoding='utf-8') as file2:
            file2.write(file2_content)

        # Create a zip file
        zip_filename = os.path.join(temp_dir, "files.zip")
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            zipf.write(file1_path, "file1.txt")
            zipf.write(file2_path, "file2.txt")

        if os.path.exists(zip_filename):
            print("file exits")
            return FileResponse(zip_filename, filename="files.zip", media_type="application/zip")
        else:
            return InternalServerError()