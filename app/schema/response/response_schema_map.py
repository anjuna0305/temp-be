from app.model.db_model import User
from app.schema.response.response_schema import UserDataRes


def map_user_to_userdata(user: User) -> UserDataRes:
    print(user.username)
    user_data = UserDataRes(
        id=user.id,
        username=user.username,
        email=user.email,
        role=str(user.scopes)
    )
    return user_data
