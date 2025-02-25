from apps.core.models import User


# CRUD
class UserService:
    @classmethod
    def create_user(cls, **data):
        pass

    @classmethod
    def retrieve_user(cls, user: User, **data):
        pass

    @classmethod
    def list_users(cls, **data):
        pass

    @classmethod
    def update_user(cls, user: User, **data):
        pass

    @classmethod
    def delete_user(cls, user: User, **data):
        pass
