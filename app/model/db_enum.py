from enum import Enum


class UserRole(Enum):
    ADMIN = 'admin'
    USER = 'reg_user'

    def __str__(self):
        return self.value
