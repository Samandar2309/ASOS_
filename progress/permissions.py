from rest_framework.permissions import BasePermission, SAFE_METHODS
from centers.models import Membership
def has_center_role(user, center, roles):
    """
    Foydalanuvchi berilgan center’da ko‘rsatilgan rollardan biriga egami?
    """
    return Membership.objects.filter(
        user=user,
        center=center,
        role__in=roles,
        is_active=True
    ).exists()
class IsStudentSelf(BasePermission):
    """
    Student faqat o'z ma'lumotlariga kira oladi
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
class IsMemberOfCenter(BasePermission):
    """
    Foydalanuvchi center a'zosi bo‘lishi shart
    """

    def has_object_permission(self, request, view, obj):
        """
        obj -> Center yoki Group
        """
        if hasattr(obj, 'center'):
            center = obj.center
        else:
            center = obj

        return Membership.objects.filter(
            user=request.user,
            center=center,
            is_active=True
        ).exists()
class IsCenterAdmin(BasePermission):
    """
    Faqat Center Admin XP bera oladi
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return Membership.objects.filter(
            user=request.user,
            role=Membership.Role.ADMIN,
            is_active=True
        ).exists()
class ReadOnlyOrCenterAdmin(BasePermission):
    """
    O‘qish hammaga, yozish faqat Center Admin
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return Membership.objects.filter(
            user=request.user,
            role=Membership.Role.ADMIN,
            is_active=True
        ).exists()
