from django.db import models, transaction
from django.db.models import F
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin, 
    BaseUserManager
)
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from validation.validators import (
    phone_validator, 
    username_validator, 
    validate_image_size,
    validate_file_extension
)
from mixins.mixing import ImageTagMixin

from account.utils import normalize_phone_number



# ==================== USER MANAGER ====================
class UserManager(BaseUserManager):
    def create_user(self, username, email, phone, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        if not email:
            raise ValueError("Email is required")
        if not phone:
            raise ValueError("Phone is required")

        user = self.model(
            username=username.strip().lower(),
            email=email.strip().lower(),
            phone=normalize_phone_number(phone),
            **extra_fields
        )

        user.set_password(password) if password else user.set_unusable_password()
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

        return self.create_user(username, email, phone, password, **extra_fields)

# ==================== USER MODEL ====================
class User(AbstractBaseUser, PermissionsMixin, ImageTagMixin):
    # ---------- BASIC ----------
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        validators=[username_validator],
    )
    email = models.EmailField(
        _("email"),
        max_length=255,
        unique=True
    )
    phone = models.CharField(
        _("phone"),
        max_length=20,
        unique=True,
        validators=[phone_validator],
    )
    
    image = models.ImageField(
        _("image"),
        upload_to="users/%Y/%m/%d/",
        default="defaults/default.jpg",
        validators=[validate_file_extension, validate_image_size]
    )
    
    
    # ---------- STATUS ----------
    is_active = models.BooleanField(_("is_active"), default=False)
    is_staff = models.BooleanField(_("is_staff"), default=False)
    is_verified = models.BooleanField(_("is_verified"), default=False)
    
    # ---------- SYSTEM ----------
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated_at"), auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "phone"]

    class Meta:
        db_table = "account_users"
        verbose_name = "01. User"
        verbose_name_plural = "01. Users"
        ordering = ["id"]
        indexes = [
            models.Index(fields=["username"]),
            models.Index(fields=["email"]),
            models.Index(fields=["phone"]),
            models.Index(fields=["is_active", "is_verified"]),
        ]

    # ==================== NORMALIZE ====================
    def normalize_fields(self):
        self.username = self.username.strip().lower()
        self.email = self.email.strip().lower()
        self.phone = normalize_phone_number(self.phone)

    def save(self, *args, **kwargs):
        validate = kwargs.pop("validate", True)

        self.normalize_fields()

        if validate:
            self.full_clean()

        super().save(*args, **kwargs)
