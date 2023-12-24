from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.core.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        password = data.get('password')
        password_confirm = data.pop('confirm_password')

        if password != password_confirm:
            raise serializers.ValidationError("Passwords do not match.")

        return data
