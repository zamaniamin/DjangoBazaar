from django.contrib.auth.password_validation import validate_password
from jsonschema.exceptions import ValidationError
from rest_framework import serializers, status

from apps.core.models import User
from apps.core.services.token_service import TokenService


class UserSerializer(serializers.ModelSerializer):
    date_joined_formatted = serializers.DateTimeField(source='date_joined', format="%Y-%m-%d %H:%M:%S", read_only=True)
    last_login_formatted = serializers.DateTimeField(source='last_login', format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_active', 'date_joined_formatted',
                  'last_login_formatted']


class UserCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        password = data.get('password')
        password_confirm = data.pop('password_confirm')

        if password != password_confirm:
            raise serializers.ValidationError('Passwords do not match.')

        return data


class ActivationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            user = User.objects.get(email=attrs['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError(detail='User with this email does not exist.',
                                              code=status.HTTP_404_NOT_FOUND)

        if user.is_active:
            raise serializers.ValidationError(detail='User is already active.',
                                              code=status.HTTP_422_UNPROCESSABLE_ENTITY)

        if TokenService.otp_verification(attrs['email'], attrs['otp']):
            return user
        else:
            raise serializers.ValidationError(detail='Invalid OTP. Please enter the correct OTP.',
                                              code=status.HTTP_406_NOT_ACCEPTABLE)


class MeSerializer(serializers.ModelSerializer):
    date_joined_formatted = serializers.DateTimeField(source='date_joined', format="%Y-%m-%d %H:%M:%S", read_only=True)
    last_login_formatted = serializers.DateTimeField(source='last_login', format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_active', 'date_joined_formatted',
                  'last_login_formatted']
        read_only_fields = ['email', 'is_active']


class ResendActivationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        try:
            user = User.objects.get(email=attrs['email'])
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError(detail='User with this email does not exist.',
                                              code=status.HTTP_404_NOT_FOUND)


class ChangeEmailSerializer(serializers.Serializer):
    new_email = serializers.EmailField()

    def validate_new_email_uniqueness(self, value):
        # Check if the new email address is not already associated with another user
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email has already been taken.")
        return value

    def validate(self, data):
        self.validate_new_email_uniqueness(data['new_email'])
        return data['new_email']


class ChangeEmailConformationSerializer(serializers.Serializer):
    new_email = serializers.EmailField()
    otp = serializers.CharField(write_only=True)

    @staticmethod
    def validate_new_email_uniqueness(value):
        if User.objects.filter(email=value).exists():
            raise ValidationError("This email has already been taken.")
        return value

    def validate(self, data):
        email = self.validate_new_email_uniqueness(data['new_email'])
        if not TokenService.otp_verification(email, data['otp']):
            raise serializers.ValidationError("Invalid OTP. Please enter the correct OTP.",
                                              code=status.HTTP_406_NOT_ACCEPTABLE)
        return data['new_email']


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        try:
            user = User.objects.get(email=attrs['email'])
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError(detail='User with this email does not exist.',
                                              code=status.HTTP_404_NOT_FOUND)


class ResetPasswordConformationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
            if not TokenService.otp_verification(user.email, data['otp']):
                raise serializers.ValidationError("Invalid OTP. Please enter the correct OTP.",
                                                  code=status.HTTP_406_NOT_ACCEPTABLE)

            return user, data['new_password']
        except User.DoesNotExist:
            raise serializers.ValidationError(detail='User with this email does not exist.',
                                              code=status.HTTP_404_NOT_FOUND)
