from pydantic import BaseModel


class UserDataRes(BaseModel):
    id: int
    username: str
    email: str
    role: str
