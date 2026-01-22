from rest_framework.permissions import BasePermission
from centers.models import Membership
from .models import Group


class IsCenterAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        return Membership.objects.filter(
            user=request.user,
            role=Membership.Role.ADMIN,
            is_active=True
        ).exists()


class IsGroupTeacher(BasePermission):
    def has_object_permission(self, request, view, obj: Group):
        return obj.teacher == request.user


class IsGroupAdminOrTeacher(BasePermission):
    def has_object_permission(self, request, view, obj: Group):
        # Teacher o'z guruhi
        if obj.teacher == request.user:
            return True

        # Center admin
        return Membership.objects.filter(
            user=request.user,
            center=obj.center,
            role=Membership.Role.ADMIN,
            is_active=True
        ).exists()
