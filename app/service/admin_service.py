import os
import tempfile
import zipfile

import magic
from sqlalchemy.ext.asyncio import AsyncSession

import app.crud.project_crud as project_crud
import app.crud.response_sentence_crud as response_crud
import app.crud.source_sentence_crud as source_crud
from app.exception import NotFoundError, BadRequestError
from app.model.db_model import Project, SourceSentence
from app.schema.request.request_schema import CreateProjectRequest
from app.schema.request.request_schema_map import create_project_to_project


async def create_new_project(
    db: AsyncSession, req_data: CreateProjectRequest
) -> Project:
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

        number_of_lines = 0
        for line in lines:
            if len(line) > 1:
                sentence = SourceSentence(
                    project_id=project_id,
                    source_sentence=line,
                )
                await source_crud.create(db, sentence)
                number_of_lines += 1
        return {f"{number_of_lines} number of lines added top project id {project_id}"}

    except Exception as e:
        raise e


async def get_responses(db: AsyncSession, project_id: int):
    temp_dir = tempfile.TemporaryDirectory()
    zip_dir = os.path.join(os.getcwd(), "tmp")
    zip_filename = os.path.join(zip_dir, "files.zip")

    try:
        # Generate multiple files (for demo, create two text files)
        source_sentences = await source_crud.get_by_project_id(db, project_id)
        source_sentences_filename = "source_sentences.txt"
        source_file_path = os.path.join(temp_dir.name, source_sentences_filename)
        with open(source_file_path, "w", encoding="utf-8") as source_sentence_file:
            for source_sentence in source_sentences:
                sentence = source_sentence.source_sentence
                sentence_id = source_sentence.sentence_id
                source_sentence_file.write(f"{sentence_id}\t{sentence}\n")

        for source_sentence in source_sentences:
            responses = await response_crud.get_by_source_sentence_id(
                db, source_sentence.sentence_id
            )
            file_path = os.path.join(
                temp_dir.name, f"{source_sentence.sentence_id}.txt"
            )
            with open(file_path, "w", encoding="utf-8") as file:
                for response in responses:
                    file.write(f"{response.response_sentence}\n")

        # Create a zip file
        response_files = os.listdir(temp_dir.name)
        print("dirs:  ", response_files)
        with zipfile.ZipFile(zip_filename, "w") as zipf:
            for response_file in response_files:
                zipf.write(os.path.join(temp_dir.name, response_file), response_file)

        temp_dir.cleanup()
        return zip_filename
    except Exception as e:
        raise e


async def get_projects(db: AsyncSession):
    try:
        projects = await project_crud.get_all(db)
        if projects:
            return projects
    except Exception as e:
        raise e


async def get_project_by_id(project_id: int, db: AsyncSession):
    try:
        projects = await project_crud.get_by_id(db, project_id)
        if projects:
            return projects
    except Exception as e:
        raise e


async def get_project_response_count(project_id: int, db: AsyncSession):
    try:
        response_count = await response_crud.get_response_count(db, project_id)
        return response_count

    except Exception as e:
        raise e


async def get_project_source_count(project_id: int, db: AsyncSession):
    try:
        result = await source_crud.get_count(db, project_id)
        return result
    except Exception as e:
        raise e


async def unpublish_project(project_id: int, db: AsyncSession):
    try:
        result = await project_crud.unpublish(project_id, db)
        return result
    except Exception as e:
        raise e


async def publish_project(project_id: int, db: AsyncSession):
    try:
        result = await project_crud.publish(project_id, db)
        return result
    except Exception as e:
        raise e