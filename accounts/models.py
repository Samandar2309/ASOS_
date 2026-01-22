import uuid
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.utils import timezone
from django.core.validators import RegexValidator
from django.apps import apps


# =========================
# USER MANAGER
# =========================
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email majburiy")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        # system username (internal)
        if not user.username:
            user.username = email.split("@")[0]

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("status", User.Status.ACTIVE)
        extra_fields.setdefault("global_role", User.GlobalRole.PLATFORM_ADMIN)
        extra_fields.setdefault("email_verified", True)
        extra_fields.setdefault("email_verified_at", timezone.now())

        return self.create_user(email, password, **extra_fields)


# =========================
# USER MODEL
# =========================
class User(AbstractBaseUser, PermissionsMixin):

    # ---------- ENUMS ----------
    class Status(models.TextChoices):
        ACTIVE = "active", "Faol"
        SUSPENDED = "suspended", "Bloklangan"
        DELETED = "deleted", "O‘chirilgan"
        PENDING = "pending", "Tasdiqlanmagan"

    class GlobalRole(models.TextChoices):
        PLATFORM_ADMIN = "platform_admin", "Platform Admin"
        CENTER_ADMIN = "center_admin", "Center Admin"
        TEACHER = "teacher", "Teacher"
        STUDENT = "student", "Student"

    class AuthProvider(models.TextChoices):
        EMAIL = "email", "Email"
        GOOGLE = "google", "Google"

    # ---------- IDENTITY ----------
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    email = models.EmailField(unique=True, db_index=True)

    username = models.CharField(
        max_length=150,
        unique=True,
        editable=False,
        null=True,
        blank=True,
    )

    # ---------- PERSONAL ----------
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    phone_regex = RegexValidator(
        regex=r"^\+998\d{9}$",
        message="Telefon raqami +998XXXXXXXXX formatida bo‘lishi kerak",
    )
    phone_number = models.CharField(
        max_length=13,
        validators=[phone_regex],
        null=True,
        blank=True,
        db_index=True,
    )

    date_of_birth = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/%Y/%m/%d/", null=True, blank=True)

    # ---------- ROLE & STATUS ----------
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    global_role = models.CharField(
        max_length=20,
        choices=GlobalRole.choices,
        default=GlobalRole.STUDENT,
        db_index=True,
    )

    auth_provider = models.CharField(
        max_length=20,
        choices=AuthProvider.choices,
        default=AuthProvider.EMAIL,
    )

    # ---------- EMAIL VERIFICATION ----------
    email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    email_verification_token = models.CharField(max_length=255, null=True, blank=True)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)

    # ---------- PASSWORD RESET ----------
    password_reset_token = models.CharField(max_length=255, null=True, blank=True)
    password_reset_sent_at = models.DateTimeField(null=True, blank=True)

    # ---------- SECURITY ----------
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_login_device = models.CharField(max_length=255, null=True, blank=True)
    last_active_at = models.DateTimeField(null=True, blank=True)

    # ---------- ONBOARDING ----------
    is_onboarding_completed = models.BooleanField(default=False)
    onboarding_step = models.PositiveSmallIntegerField(default=1)
    onboarding_data = models.JSONField(default=dict, blank=True)

    # ---------- OAUTH ----------
    google_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
        db_index=True,
    )

    # ---------- SYSTEM ----------
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # ---------- AUTH CONFIG ----------
    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["status"]),
            models.Index(fields=["global_role"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["last_active_at"]),
        ]

    def __str__(self):
        return f"{self.email} ({self.global_role})"

    # =========================
    # BUSINESS METHODS
    # =========================
    def mark_email_verified(self):
        self.email_verified = True
        self.email_verified_at = timezone.now()
        self.status = self.Status.ACTIVE
        self.save(update_fields=["email_verified", "email_verified_at", "status"])

    def suspend(self):
        self.status = self.Status.SUSPENDED
        self.is_active = False
        self.save(update_fields=["status", "is_active"])

    def activate(self):
        self.status = self.Status.ACTIVE
        self.is_active = True
        self.save(update_fields=["status", "is_active"])

    def soft_delete(self):
        self.status = self.Status.DELETED
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(update_fields=["status", "deleted_at", "is_active"])

    # ---------- ROLE CHECKS ----------
    def is_platform_admin(self):
        return self.global_role == self.GlobalRole.PLATFORM_ADMIN

    def is_center_admin(self):
        return self.global_role == self.GlobalRole.CENTER_ADMIN

    def is_teacher(self):
        return self.global_role == self.GlobalRole.TEACHER

    def is_student(self):
        return self.global_role == self.GlobalRole.STUDENT

    # ---------- CENTER HELPER ----------
    def has_center_access(self, center_id):
        Membership = apps.get_model("centers", "Membership")
        return Membership.objects.filter(
            user=self,
            center_id=center_id,
            status=Membership.Status.ACTIVE,
        ).exists()
