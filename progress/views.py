from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model

from centers.models import Center
from groups.models import Group
from .models import XPTransaction
from .serializers import (
    StudentProgressSerializer,
    XPTransactionSerializer,
    LeaderboardSerializer,
    AdminXPGrantSerializer,
)
from .services import (
    get_or_create_progress,
    get_global_leaderboard,
    get_center_leaderboard,
    get_group_leaderboard,
    admin_grant_xp,
)

User = get_user_model()
class LimitMixin:
    def get_limit(self, default=50, max_limit=100):
        try:
            limit = int(self.request.query_params.get('limit', default))
        except (TypeError, ValueError):
            limit = default
        return min(limit, max_limit)
class MyProgressView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StudentProgressSerializer

    def get_object(self):
        return get_or_create_progress(self.request.user)
class MyXPTransactionsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = XPTransactionSerializer

    def get_queryset(self):
        return XPTransaction.objects.filter(
            student=self.request.user
        ).order_by('-created_at')
class GlobalLeaderboardView(LimitMixin, generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LeaderboardSerializer

    def get_queryset(self):
        return get_global_leaderboard(
            limit=self.get_limit()
        )
class CenterLeaderboardView(LimitMixin, generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LeaderboardSerializer

    def get_queryset(self):
        center = get_object_or_404(Center, id=self.kwargs.get('center_id'))
        return get_center_leaderboard(
            center=center,
            limit=self.get_limit()
        )
class GroupLeaderboardView(LimitMixin, generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LeaderboardSerializer

    def get_queryset(self):
        group = get_object_or_404(Group, id=self.kwargs.get('group_id'))
        return get_group_leaderboard(
            group=group,
            limit=self.get_limit()
        )
class AdminXPGrantView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    serializer_class = AdminXPGrantSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        student = get_object_or_404(
            User,
            id=serializer.validated_data['student_id']
        )

        progress = admin_grant_xp(
            admin_user=request.user,
            student=student,
            amount=serializer.validated_data['amount'],
            reason=serializer.validated_data['reason']
        )

        return Response(
            StudentProgressSerializer(progress).data,
            status=status.HTTP_200_OK
        )
