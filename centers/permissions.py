from rest_framework.permissions import BasePermission
from .models import Membership


class IsCenterAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        return Membership.objects.filter(
            user=request.user,
            role=Membership.Role.ADMIN,
            is_active=True
        ).exists()


class IsCenterMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        return Membership.objects.filter(
            user=request.user,
            center=obj,
            is_active=True
        ).exists()
