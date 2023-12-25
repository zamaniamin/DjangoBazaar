from django.contrib.auth import get_user_model
from django.db import IntegrityError
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.core import serializers

User = get_user_model()


@extend_schema_view(
    create=extend_schema(
        tags=["Auth"],
        summary='Add or Register a new user',
        description="""## Register a new user by email and password, then send an OTP code to the user's email address.
    
Generate an account activation code for a user whose account is not yet enabled.

The account activation code generated by this endpoint is designed for one-time use and will expire after 5 minutes. 
If a new POST request is made to this endpoint, a new code will be generated if the previous code has expired. The newly
 generated code will be valid for another 5 minutes, while the previous code will no longer be valid.

Following the registration request, this endpoint will send an OTP code to the user's email address. It is essential to 
verify this OTP code using the `/accounts/register/verify` endpoint. Verification confirms the user's email address and 
activates their account.
 
Please note that users cannot log in to their accounts until their email addresses are verified.
""",
    ),
)
class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.UserCreateSerializer
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.validated_data

        try:
            user = User.objects.create(**user_data)
            user.set_password(user_data['password'])
            user.is_active = False
            user.save()

            response_body = {
                'user_id': user.id,
                'email': user.email,
            }

            return Response(response_body, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return Response({'error': 'User with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
