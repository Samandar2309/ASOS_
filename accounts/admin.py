# accounts/admin.py

from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "global_role",
        "status",
        "email_verified",
        "is_active",
        "created_at",
    )

    list_filter = (
        "global_role",
        "status",
        "email_verified",
        "is_active",
    )

    search_fields = (
        "email",
        "first_name",
        "last_name",
        "phone_number",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "id",
        "uuid",
        "created_at",
        "updated_at",
        "last_active_at",
        "email_verified_at",
        "password_reset_sent_at",
    )

    fieldsets = (
        ("Auth", {
            "fields": (
                "email",
                "password",
                "auth_provider",
                "google_id",
            )
        }),
        ("Personal info", {
            "fields": (
                "first_name",
                "last_name",
                "phone_number",
                "date_of_birth",
                "avatar",
            )
        }),
        ("Roles & Status", {
            "fields": (
                "global_role",
                "status",
                "is_active",
                "is_staff",
                "is_superuser",
            )
        }),
        ("Verification", {
            "fields": (
                "email_verified",
                "email_verified_at",
            )
        }),
        ("Security", {
            "fields": (
                "last_login",
                "last_active_at",
                "last_login_ip",
                "last_login_device",
            )
        }),
        ("System", {
            "fields": (
                "uuid",
                "created_at",
                "updated_at",
            )
        }),
    )

    def has_delete_permission(self, request, obj=None):
        # Hard delete yo‘q — faqat soft delete
        return False
