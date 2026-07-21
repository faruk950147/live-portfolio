import re

from django import forms
from django.db import transaction
from django.contrib.auth import get_user_model

from account.services import OTPService
from account.tasks import send_verification_email

User = get_user_model()


# ========================= PASSWORD VALIDATION =========================
def validate_password_strength(password):
    if not password:
        raise forms.ValidationError("Password is required.")

    if len(password) < 8:
        raise forms.ValidationError("Password must be at least 8 characters.")

    if not re.search(r"[A-Z]", password):
        raise forms.ValidationError("Password must contain at least one uppercase letter.")

    if not re.search(r"[a-z]", password):
        raise forms.ValidationError("Password must contain at least one lowercase letter.")

    if not re.search(r"\d", password):
        raise forms.ValidationError("Password must contain at least one number.")

    return password


# ========================= BASE STYLED FORM =========================
class StyledForm(forms.Form):
    def __init__(self, *args, **kwargs):
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

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password != password2:
            raise forms.ValidationError("Passwords do not match.")

        validate_password_strength(password)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        user.set_password(self.cleaned_data["password"])
        user.is_active = False
        user.is_verified = False

        if commit:
            with transaction.atomic():
                user.save()
                # Generate and save OTP
                otp = OTPService.generate()
                OTPService.save(user.email, otp)

                # Send OTP after successful commit
                transaction.on_commit(
                    lambda: send_verification_email.delay(
                        user.email,
                        otp
                    )
                )

        return user