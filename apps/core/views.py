from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.core import serializers

User = get_user_model()


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
