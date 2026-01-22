from rest_framework.permissions import BasePermission


class IsCenterAdmin(BasePermission):
    """
    Faqat center_admin bo‘lgan foydalanuvchi analytics ko‘ra oladi
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # role tekshiruvi
        if user.role != "center_admin":
            return False

        # active_center borligini tekshiramiz
        if not getattr(user, "active_center", None):
            return False

        return True
