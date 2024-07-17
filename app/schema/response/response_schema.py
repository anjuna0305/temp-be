from pydantic import BaseModel


class UserDataRes(BaseModel):
    id: int
    username: str
    email: str
    role: str


class ProjectDataResponse(BaseModel):
    project_id: int
    project_name: str
    created_at: str
    is_published: bool
