from app.model.db_model import User, Project
from app.schema.response.response_schema import UserDataRes, ProjectDataResponse


def map_user_to_userdata(user: User) -> UserDataRes:
    user_data = UserDataRes(
        id=user.id,
        username=user.username,
        email=user.email,
        role=str(user.scopes)
    )
    return user_data


def map_project_to_projectdataresponse(project: Project) -> ProjectDataResponse:
    project_data = ProjectDataResponse(
        project_id=project.project_id,
        project_name=project.project_name,
        created_at=project.created_at
    )
    return project_data
