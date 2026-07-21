import re

from django.db import transaction
from django.contrib.auth import get_user_model

from rest_framework import serializers

from account.services import OTPService
from account.tasks import send_verification_email

User = get_user_model()


# ========================= PASSWORD VALIDATION =========================
def validate_password(password):
    if len(password) < 8:
        raise serializers.ValidationError("Password must be at least 8 characters.")

    if not re.search(r"[A-Z]", password):
        raise serializers.ValidationError("Password must contain at least one uppercase letter.")

    if not re.search(r"[a-z]", password):
        raise serializers.ValidationError("Password must contain at least one lowercase letter.")

    if not re.search(r"\d", password):
        raise serializers.ValidationError("Password must contain at least one number.")

    return password


# ========================= SIGNUP =========================
class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    password2 = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = User
        fields = ["username", "email", "phone", "password", "password2"]

    def validate(self, attrs):
        password = attrs["password"]
        password2 = attrs["password2"]

        if password != password2:
            raise serializers.ValidationError(
                {"password2": "Passwords do not match."}
            )

        validate_password(password)

        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")

        with transaction.atomic():
            user = User.objects.create_user(
                password=password,
                is_active=False,
                is_verified=False,
                **validated_data,
            )

            # Generate & Save OTP
            otp = OTPService.generate()
            OTPService.save(user.email, otp)

            # Send OTP after successful commit
            transaction.on_commit(
                lambda: send_verification_email.delay(user.email, otp)
            )

        return user