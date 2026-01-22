from rest_framework import serializers
from .models import Group, GroupStudent
from centers.models import Membership


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = (
            'id',
            'name',
            'subject',
            'teacher',
            'invite_code',
            'is_active',
            'created_at',
        )
        read_only_fields = ('id', 'invite_code', 'created_at')


class GroupStudentAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupStudent
        fields = ('student',)

    def validate(self, attrs):
        group = self.context['group']
        student = attrs['student']

        # Student shu centerga tegishli bo'lishi shart
        if not Membership.objects.filter(
            user=student,
            center=group.center,
            role=Membership.Role.STUDENT,
            is_active=True
        ).exists():
            raise serializers.ValidationError(
                "Bu foydalanuvchi ushbu markazga tegishli emas."
            )

        return attrs
