import re

from django.db import transaction
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

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
            raise serializers.ValidationError({"password2": "Passwords do not match."})

        validate_password(password)

        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")

        with transaction.atomic():
            user = User.objects.create_user(
                password=password, is_active=False, 
                is_verified=False, **validated_data,
            )

            # Generate & Save OTP
            otp = OTPService.generate()
            OTPService.save(user.email, otp)

            # Send OTP after successful commit
            transaction.on_commit(lambda: send_verification_email.delay(user.email, otp))

        return user
    
# ========================= EMAIL VERIFICATION =========================
class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(min_length=6, max_length=6, trim_whitespace=True)

    def validate(self, attrs):
        email = attrs["email"].strip().lower()
        otp = attrs["otp"].strip()

        user = User.objects.filter(email=email).first()

        if not user:
            raise serializers.ValidationError({"email": "User does not exist."})

        if user.is_verified:
            raise serializers.ValidationError({"email": "Email is already verified."})

        if not OTPService.verify(user.email, otp):
            raise serializers.ValidationError({"otp": "Invalid or expired OTP."})

        attrs["user"] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]

        with transaction.atomic():
            user.is_verified = True
            user.is_active = True
            user.save(update_fields=["is_verified", "is_active"])
            OTPService.delete(user.email)

        return user

# ========================= LOGIN =========================
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )
    keep_logged_in = serializers.BooleanField(
        required=False,
        default=False,
    )

    def validate(self, attrs):
        identifier = attrs["username"].strip()
        password = attrs["password"]

        # username/email/phone 
        user = User.objects.filter(
            Q(username=identifier) |
            Q(email=identifier) |
            Q(phone=identifier)
        ).first()

        if not user:
            raise serializers.ValidationError({"detail": "Invalid credentials."})

        # Django authentication
        user = authenticate(username=user.username, password=password)

        if user is None:
            raise serializers.ValidationError({"detail": "Invalid credentials."})

        if not user.is_verified:
            raise serializers.ValidationError({"detail": "Please verify your email first."})

        if not user.is_active:
            raise serializers.ValidationError({"detail": "Your account is inactive."})

        refresh = RefreshToken.for_user(user)

        return {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
            },
            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
        }

# ====================== LOGOUT ================================
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            raise serializers.ValidationError({"refresh": "Invalid or expired refresh token."})







