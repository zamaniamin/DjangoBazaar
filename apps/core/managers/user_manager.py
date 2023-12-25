from django.contrib.auth import get_user_model


class UserManager:
    User = get_user_model()

    @classmethod
    def create(cls, **user_data):
        new_user = cls.User.objects.create(**user_data)
        new_user.set_password(user_data['password'])
        new_user.is_active = False
        new_user.save()
        return new_user
