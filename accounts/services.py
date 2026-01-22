# accounts/services.py

import secrets
import hashlib
import requests

from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


# ======================================================
# INTERNAL HELPERS
# ======================================================
def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _is_expired(sent_at, timeout_seconds: int) -> bool:
    if not sent_at:
        return True
    return (timezone.now() - sent_at).total_seconds() > timeout_seconds


# ======================================================
# JWT
# ======================================================
def generate_jwt_for_user(user: User) -> dict:
    """
    Access + Refresh token yaratadi.
    """
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


# ======================================================
# REGISTRATION (EMAIL)
# ======================================================
def register_user(
    *,
    email: str,
    password: str,
    first_name: str = "",
    last_name: str = "",
) -> User:
    """
    Email + password orqali ro'yxatdan o'tkazadi.
    """
    if User.objects.filter(email=email).exists():
        raise ValueError("Bu email allaqachon ro'yxatdan o'tgan")

    user = User.objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        status=User.Status.PENDING,
        auth_provider=User.AuthProvider.EMAIL,
    )

    send_email_verification(user)
    return user


# ======================================================
# LOGIN (EMAIL)
# ======================================================
def authenticate_user(*, email: str, password: str) -> User:
    """
    Email + password login.
    """
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise ValueError("Login yoki parol noto‘g‘ri")

    if not user.check_password(password):
        raise ValueError("Login yoki parol noto‘g‘ri")

    if user.status == User.Status.SUSPENDED:
        raise ValueError("Account bloklangan")

    if user.status == User.Status.DELETED:
        raise ValueError("Account mavjud emas")

    if not user.email_verified:
        raise ValueError("Email tasdiqlanmagan")

    user.last_login = timezone.now()
    user.save(update_fields=["last_login"])
    return user


# ======================================================
# EMAIL VERIFICATION
# ======================================================
def generate_email_verification_token(user: User) -> str:
    raw_token = secrets.token_urlsafe(32)
    user.email_verification_token = _hash_token(raw_token)
    user.email_verification_sent_at = timezone.now()
    user.save(update_fields=[
        "email_verification_token",
        "email_verification_sent_at",
    ])
    return raw_token


def verify_email_by_token(raw_token: str) -> User:
    token_hash = _hash_token(raw_token)

    try:
        user = User.objects.get(email_verification_token=token_hash)
    except User.DoesNotExist:
        raise ValueError("Token yaroqsiz")

    if _is_expired(
        user.email_verification_sent_at,
        settings.EMAIL_VERIFICATION_TIMEOUT,
    ):
        raise ValueError("Token muddati o'tgan")

    user.mark_email_verified()
    user.email_verification_token = None
    user.email_verification_sent_at = None
    user.save(update_fields=[
        "email_verified",
        "email_verified_at",
        "status",
        "email_verification_token",
        "email_verification_sent_at",
    ])
    return user


def send_email_verification(user: User) -> None:
    raw_token = generate_email_verification_token(user)

    verification_url = (
        f"{settings.FRONTEND_URL}/verify-email?token={raw_token}"
    )

    html_message = render_to_string(
        "accounts/email_verification.html",
        {
            "user": user,
            "verification_url": verification_url,
            "expiry_hours": settings.EMAIL_VERIFICATION_TIMEOUT // 3600,
        },
    )

    send_mail(
        subject="ASOS - Emailni tasdiqlash",
        message="",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )


# ======================================================
# PASSWORD RESET
# ======================================================
def generate_password_reset_token(user: User) -> str:
    raw_token = secrets.token_urlsafe(32)
    user.password_reset_token = _hash_token(raw_token)
    user.password_reset_sent_at = timezone.now()
    user.save(update_fields=[
        "password_reset_token",
        "password_reset_sent_at",
    ])
    return raw_token


def verify_password_reset_token(raw_token: str) -> User:
    token_hash = _hash_token(raw_token)

    try:
        user = User.objects.get(password_reset_token=token_hash)
    except User.DoesNotExist:
        raise ValueError("Token yaroqsiz")

    if _is_expired(
        user.password_reset_sent_at,
        settings.PASSWORD_RESET_TIMEOUT,
    ):
        raise ValueError("Token muddati o'tgan")

    return user


def reset_password(*, raw_token: str, new_password: str) -> None:
    user = verify_password_reset_token(raw_token)
    user.set_password(new_password)
    user.password_reset_token = None
    user.password_reset_sent_at = None
    user.save(update_fields=[
        "password",
        "password_reset_token",
        "password_reset_sent_at",
    ])


def send_password_reset_email(user: User) -> None:
    raw_token = generate_password_reset_token(user)

    reset_url = (
        f"{settings.FRONTEND_URL}/reset-password?token={raw_token}"
    )

    html_message = render_to_string(
        "accounts/password_reset.html",
        {
            "user": user,
            "reset_url": reset_url,
            "expiry_hours": settings.PASSWORD_RESET_TIMEOUT // 3600,
        },
    )

    send_mail(
        subject="ASOS - Parolni tiklash",
        message="",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )


# ======================================================
# GOOGLE OAUTH
# ======================================================
def authenticate_with_google(access_token: str) -> User:
    response = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=5,
    )

    if response.status_code != 200:
        raise ValueError("Google token yaroqsiz")

    data = response.json()
    email = data.get("email")
    google_id = data.get("sub")

    if not email or not google_id:
        raise ValueError("Google ma'lumotlari to‘liq emas")

    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            "first_name": data.get("given_name", ""),
            "last_name": data.get("family_name", ""),
            "auth_provider": User.AuthProvider.GOOGLE,
            "google_id": google_id,
            "email_verified": True,
            "status": User.Status.ACTIVE,
        },
    )

    if not created:
        updated = False
        if user.auth_provider != User.AuthProvider.GOOGLE:
            user.auth_provider = User.AuthProvider.GOOGLE
            updated = True
        if not user.google_id:
            user.google_id = google_id
            updated = True
        if not user.email_verified:
            user.email_verified = True
            user.status = User.Status.ACTIVE
            updated = True
        if updated:
            user.save()

    return user
