from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Center, Membership
from .serializers import CenterSerializer
from .permissions import IsCenterAdmin


class MyCenterView(generics.RetrieveAPIView):
    serializer_class = CenterSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        membership = Membership.objects.get(
            user=self.request.user,
            is_active=True
        )
        return membership.center


class UpdateCenterView(generics.UpdateAPIView):
    serializer_class = CenterSerializer
    permission_classes = [IsAuthenticated, IsCenterAdmin]

    def get_object(self):
        return Center.objects.get(
            memberships__user=self.request.user,
            memberships__role=Membership.Role.ADMIN,
            memberships__is_active=True
        )
