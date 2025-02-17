from app.model.db_model import User, ResponseSentence, Project
from app.schema.request.request_schema import (
    SignInRequest,
    CreateResponseSentenceRequest,
    CreateProjectRequest
)


def sign_in_req_to_user(schema: SignInRequest) -> User:
    user: User = User(
        username=schema.username, email=schema.email, hashed_password=schema.password
    )
    return user


def create_response_sentence_request_to_response_sentence(
        schema: CreateResponseSentenceRequest, user_id: int
) -> ResponseSentence:
    response_sentence = ResponseSentence(
        project_id=schema.project_id,
        source_sentence_id=schema.source_id,
        response_sentence=schema.sentence,
        user_id=user_id,
    )
    return response_sentence


def create_project_to_project(schema: CreateProjectRequest) -> Project:
    project = Project(
        project_name=schema.project_name
    )
    return project
