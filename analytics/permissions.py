from rest_framework.permissions import BasePermission
from centers.models import Membership


class IsCenterAdmin(BasePermission):
    """
    Allows access only to users who are:
    - authenticated
    - have an active_center selected
    - are center_admin of that active_center

    This permission is designed for multi-tenant SaaS analytics access.
    """

    message = "You do not have permission to access this analytics data."

    def has_permission(self, request, view):
        user = request.user

        # 1. Authentication check
        if not user or not user.is_authenticated:
            return False

        # 2. Active center must be selected
        center = getattr(user, "active_center", None)
        if center is None:
            return False

        # 3. Membership-based role validation (SaaS-safe)
        return Membership.objects.filter(
            user=user,
            center=center,
            role=Membership.Role.CENTER_ADMIN
            if hasattr(Membership, "Role")
            else "center_admin"
        ).exists()
