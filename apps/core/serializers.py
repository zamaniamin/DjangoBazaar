from django.contrib.auth.password_validation import validate_password
from jsonschema.exceptions import ValidationError
from rest_framework import serializers, status

from apps.core.models import User
from apps.core.services.token_service import TokenService


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.

    Attributes:
        date_joined (datetime): Formatted date and time when the user joined (read-only).
        last_login (datetime): Formatted date and time of the last login (read-only).

    """
    date_joined = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    last_login = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'last_login']


class UserCreateSerializer(serializers.Serializer):
    """
    Serializer for user creation.

    Attributes:
        email (str): Email field for the user.
        password (str): Password field for the user (write-only).
        password_confirm (str): Password confirmation field (write-only).

    Methods:
        validate(data): Custom validation method to ensure password and password confirmation match.

    Raises:
        serializers.ValidationError: If passwords do not match.

    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validate the provided data.

        Args:
            data (dict): Dictionary containing user creation data.

        Returns:
            dict: Validated data.

        Raises:
            serializers.ValidationError: If passwords do not match.

        """
        password = data.get('password')
        password_confirm = data.pop('password_confirm')

        if password != password_confirm:
            raise serializers.ValidationError('Passwords do not match.')

        return data


class ActivationSerializer(serializers.Serializer):
    """
    Serializer for user activation.

    Attributes:
        email (str): Email field for user activation.
        otp (str): One-time password (OTP) field for user activation (write-only).

    Methods:
        validate(attrs): Custom validation method to check user existence, activation status, and OTP validity.

    Raises:
        serializers.ValidationError: If the user does not exist, is already active, or if the OTP is invalid.

    """
    email = serializers.EmailField()
    otp = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """
        Validate the provided data.

        Args:
            attrs (dict): Dictionary containing user activation data.

        Returns:
            User: Validated user if successful.

        Raises:
            serializers.ValidationError: If the user does not exist, is already active, or if the OTP is invalid.

        """
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
    date_joined = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    last_login = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_active', 'date_joined',
                  'last_login']
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

    @staticmethod
    def validate_new_email_uniqueness(value):
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


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate_current_password(self, value):
        is_password_valid = self.context['request'].user.check_password(value)
        if is_password_valid:
            return value
        else:
            raise serializers.ValidationError(detail='invalid_password.', code=status.HTTP_404_NOT_FOUND)
