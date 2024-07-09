import magic
from sqlalchemy.ext.asyncio import AsyncSession

import app.crud.project_crud as project_crud
import app.crud.source_sentence_crud as source_crud
from app.exception import NotFoundError, BadRequestError
from app.model.db_model import Project, SourceSentence
from app.schema.request.request_schema import CreateProjectRequest
from app.schema.request.request_schema_map import create_project_to_project


async def create_new_project(db: AsyncSession, req_data: CreateProjectRequest) -> Project:
    try:
        project_object = create_project_to_project(req_data)
        result = await project_crud.create(db, project_object)
        return result
    except Exception as e:
        raise e


async def add_source_sentence(db: AsyncSession, project_id: int, file: bytes):
    try:
        project = await project_crud.get_by_id(db, project_id)
        if not project:
            NotFoundError(detail="Invalid project id.")

        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(file)

        if not mime_type.startswith("text"):
            raise BadRequestError(detail="Uploaded file is not a text file.")

        decoded_content = file.decode("utf-8")
        lines = decoded_content.splitlines()

        for line in lines:
            if len(line) > 1:
                sentence = SourceSentence(
                    project_id=project_id,
                    source_sentence=line,
                )
                await source_crud.create(db, sentence)
        return {"file_size": len(file)}

    except Exception as e:
        raise e
