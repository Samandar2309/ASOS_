from rest_framework.permissions import BasePermission
from accounts.models import User
from django.apps import apps


# ======================================================
# PLATFORM ADMIN
# ======================================================
class IsPlatformAdmin(BasePermission):
    """
    Faqat platform adminlar uchun
    """
    message = "Bu amal faqat Platform Admin uchun ruxsat etilgan"
    code = "platform_admin_required"

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.global_role == User.GlobalRole.PLATFORM_ADMIN


# ======================================================
# ONBOARDING
# ======================================================
class IsOnboarded(BasePermission):
    """
    Foydalanuvchi onboarding tugatgan bo‘lishi shart
    """
    message = "Iltimos, avval onboarding jarayonini tugating"
    code = "onboarding_required"

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.is_onboarding_completed


# ======================================================
# CENTER ACCESS (ESLATMA: accounts uchun shart emas)
# ======================================================
class HasCenterAccess(BasePermission):
    """
    User center’ga kirish huquqiga ega bo‘lishi shart
    """
    message = "Sizda ushbu o‘quv markazga kirish huquqi yo‘q"
    code = "center_access_denied"

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.global_role == User.GlobalRole.PLATFORM_ADMIN:
            return True

        center_id = (
            view.kwargs.get("center_id")
            or request.query_params.get("center_id")
            or request.data.get("center_id")
        )

        Membership = apps.get_model("centers", "Membership")

        if not center_id:
            return Membership.objects.filter(
                user=user,
                status=Membership.Status.ACTIVE
            ).exists()

        return Membership.objects.filter(
            user=user,
            center_id=center_id,
            status=Membership.Status.ACTIVE
        ).exists()


# ======================================================
# ROLE-BASED
# ======================================================
class IsTeacherOrHigher(BasePermission):
    message = "Bu amal faqat teacher yoki undan yuqori foydalanuvchilar uchun"
    code = "teacher_required"

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        return user.global_role in {
            User.GlobalRole.TEACHER,
            User.GlobalRole.CENTER_ADMIN,
            User.GlobalRole.PLATFORM_ADMIN,
        }


class IsCenterAdminOrHigher(BasePermission):
    message = "Bu amal faqat center admin yoki platform admin uchun"
    code = "center_admin_required"

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        return user.global_role in {
            User.GlobalRole.CENTER_ADMIN,
            User.GlobalRole.PLATFORM_ADMIN,
        }
