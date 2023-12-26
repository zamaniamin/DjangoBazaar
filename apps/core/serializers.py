from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, status

from apps.core.models import User
from apps.core.services.token_service import TokenService


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class UserCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        password = data.get("password")
        password_confirm = data.pop("password_confirm")

        if password != password_confirm:
            raise serializers.ValidationError("Passwords do not match.")

        return data


class ActivationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            user = User.objects.get(email=attrs["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError(detail="User with this email does not exist.",
                                              code=status.HTTP_404_NOT_FOUND)

        if user.is_active:
            raise serializers.ValidationError(detail="User is already active.",
                                              code=status.HTTP_422_UNPROCESSABLE_ENTITY)

        if TokenService.validate_otp_token(attrs["otp"]):
            return user
        else:
            raise serializers.ValidationError(detail="Invalid OTP. Please enter the correct OTP.",
                                              code=status.HTTP_406_NOT_ACCEPTABLE)
