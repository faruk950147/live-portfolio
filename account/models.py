from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from validation.validators import (
    phone_validator,
    username_validator,
    validate_image_size,
    validate_file_extension,
)

from mixins.mixing import ImageTagMixin
from account.utils import normalize_phone_number


# ===========================
# USER MANAGER
# ===========================
class UserManager(BaseUserManager):
    def create_user(self, username, email, phone, password=None, **extra_fields):
        if not username:
            raise ValueError(_("Username is required"))

        if not email:
            raise ValueError(_("Email is required"))

        if not phone:
            raise ValueError(_("Phone number is required"))

        user = self.model(
            username=username.strip().casefold(),
            email=self.normalize_email(email),
            phone=normalize_phone_number(phone),
            **extra_fields,
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.full_clean()
        user.save(using=self._db)

        return user

    def create_superuser(self, username, email, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(
            username=username,
            email=email,
            phone=phone,
            password=password,
            **extra_fields,
        )


# ===========================
# USER MODEL
# ===========================
class User(AbstractBaseUser, PermissionsMixin, ImageTagMixin):
    username = models.CharField(
        _("Username"),
        max_length=150,
        unique=True,
        validators=[username_validator],
    )

    email = models.EmailField(
        _("Email"),
        unique=True,
    )

    phone = models.CharField(
        _("Phone"),
        max_length=20,
        unique=True,
        validators=[phone_validator],
    )

    image = models.ImageField(
        _("Profile Image"),
        upload_to="users/%Y/%m/%d/",
        default="media/defaults/default.jpg",
        null=True,
        blank=True,
        validators=[
            validate_file_extension,
            validate_image_size,
        ],
    )

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "phone"]

    class Meta:
        db_table = "account_users"
        verbose_name = _("01. User")
        verbose_name_plural = _("01. Users")
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["username"]),
            models.Index(fields=["email"]),
            models.Index(fields=["phone"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["is_active", "is_verified"]),
        ]

    def clean(self):
        super().clean()

        self.username = self.username.strip().casefold()
        self.email = User.objects.normalize_email(self.email)
        self.phone = normalize_phone_number(self.phone)

    def save(self, *args, **kwargs):
        validate = kwargs.pop("validate", True)

        if validate:
            self.full_clean()

        super().save(*args, **kwargs)

    @property
    def image_tag(self):
        image = getattr(self, "image", None)

        if image and hasattr(image, "url"):
            return format_html(
                '''
                <img src="{}" style="width:30px; height:30px; object-fit:cover; 
                border-radius:5px; border:1px solid #ddd;" />
                ''',
                image.url
            )

        return format_html('<span>No Image</span>')

    def __str__(self):
        return self.username

    def __repr__(self):
        return f"<User: {self.username}>"