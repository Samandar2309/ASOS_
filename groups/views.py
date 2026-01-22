from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Group, GroupStudent
from .serializers import GroupSerializer, GroupStudentAddSerializer
from .permissions import IsGroupAdminOrTeacher
from centers.models import Membership


class GroupListCreateView(generics.ListCreateAPIView):
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Center admin → barcha guruhlar
        admin_centers = Membership.objects.filter(
            user=user,
            role=Membership.Role.ADMIN,
            is_active=True
        ).values_list('center_id', flat=True)

        if admin_centers.exists():
            return Group.objects.filter(center_id__in=admin_centers)

        # Teacher → faqat o'z guruhlari
        return Group.objects.filter(teacher=user)

    def perform_create(self, serializer):
        membership = Membership.objects.filter(
            user=self.request.user,
            role=Membership.Role.ADMIN,
            is_active=True
        ).first()

        serializer.save(center=membership.center)


class GroupDetailView(generics.RetrieveUpdateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, IsGroupAdminOrTeacher]


class GroupStudentAddView(generics.CreateAPIView):
    serializer_class = GroupStudentAddSerializer
    permission_classes = [IsAuthenticated, IsGroupAdminOrTeacher]

    def get_group(self):
        return Group.objects.get(pk=self.kwargs['group_id'])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['group'] = self.get_group()
        return context

    def perform_create(self, serializer):
        group = self.get_group()
        serializer.save(group=group)


class GroupStudentRemoveView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsGroupAdminOrTeacher]

    def get_object(self):
        return GroupStudent.objects.get(
            group_id=self.kwargs['group_id'],
            student_id=self.kwargs['student_id']
        )
