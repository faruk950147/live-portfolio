import re
from typing import Any

from django import forms
from django.db import transaction
from django.contrib.auth import get_user_model

from account.services import OTPService
from account.tasks import send_verification_email

User = get_user_model()


# ========================= PASSWORD VALIDATION =========================
def validate_password_strength(password: str) -> str:
    if not password:
        raise forms.ValidationError("Password is required.")

    if len(password) < 8:
        raise forms.ValidationError("Password must be at least 8 characters.")

    if not re.search(r"[A-Z]", password):
        raise forms.ValidationError(
            "Password must contain at least one uppercase letter."
        )

    if not re.search(r"[a-z]", password):
        raise forms.ValidationError(
            "Password must contain at least one lowercase letter."
        )

    if not re.search(r"\d", password):
        raise forms.ValidationError(
            "Password must contain at least one number."
        )

    return password


# ========================= BASE STYLED FORM =========================
class StyledForm(forms.Form):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            if isinstance(
                field.widget,
                (
                    forms.TextInput,
                    forms.PasswordInput,
                    forms.EmailInput,
                    forms.NumberInput,
                    forms.Textarea,
                ),
            ):
                field.widget.attrs.setdefault("class", "form-control")


# ========================= SIGNUP FORM =========================
class SignupForm(StyledForm, forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ["username", "email", "phone", "password", "password2"]

    def clean_username(self) -> str:
        username = self.cleaned_data.get("username")

        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Username already exists.")

        return username

    def clean_email(self) -> str:
        email = self.cleaned_data.get("email")

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Email already exists.")

        return email

    def clean_phone(self) -> str:
        phone = self.cleaned_data.get("phone")

        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("Phone number already exists.")

        return phone

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password != password2:
            raise forms.ValidationError("Passwords do not match.")

        validate_password_strength(password)

        return cleaned_data

    def save(self, commit: bool = True) -> User:
        user = super().save(commit=False)

        user.set_password(self.cleaned_data["password"])
        user.is_active = False
        user.is_verified = False

        if commit:
            with transaction.atomic():
                user.save()

                otp = OTPService.generate()
                OTPService.save(user.email, otp)

                transaction.on_commit(
                    lambda: send_verification_email.delay(user.email, otp)
                )

        return user