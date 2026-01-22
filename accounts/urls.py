# accounts/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # ======================================================
    # AUTH
    # ======================================================
    path(
        "auth/email/verify/",
        views.EmailVerificationView.as_view(),
        name="email-verify",
    ),
    path(
        "auth/email/resend/",
        views.ResendVerificationEmailView.as_view(),
        name="email-resend",
    ),
    path(
        "auth/google/",
        views.GoogleOAuthView.as_view(),
        name="google-auth",
    ),

    # ----------------------
    # PASSWORD RESET
    # ----------------------
    path(
        "auth/password/reset/",
        views.PasswordResetRequestView.as_view(),
        name="password-reset",
    ),
    path(
        "auth/password/reset/confirm/",
        views.PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),

    # ======================================================
    # PROFILE
    # ======================================================
    path(
        "me/profile/",
        views.UserProfileUpdateView.as_view(),
        name="profile-update",
    ),

    # ======================================================
    # ADMIN (PLATFORM)
    # ======================================================
    path(
        "admin/users/",
        views.AdminUserManagementView.as_view(),
        name="admin-user-list",
    ),
    path(
        "admin/users/<int:pk>/",
        views.AdminUserManagementView.as_view(),
        name="admin-user-update",
    ),
]
