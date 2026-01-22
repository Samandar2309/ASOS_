from rest_framework.permissions import BasePermission


class IsCenterAdmin(BasePermission):
    """
    Faqat center admin billing ma'lumotlarini ko‘ra oladi
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        center = getattr(user, "active_center", None)
        return center is not None
