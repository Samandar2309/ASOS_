from rest_framework import serializers
from django.utils import timezone

from .models import (
    Assignment,
    AssignmentSubmission,
    GameSession,
    StudentAnswer,
    Question,
    AnswerOption,
)
from centers.models import Membership
class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = (
            'id',
            'group',
            'title',
            'description',
            'file',
            'type',
            'xp_reward',
            'visible_from',
            'due_date',
            'is_active',
            'is_archived',
            'created_at',
        )
        read_only_fields = ('id', 'created_at')

    def validate(self, attrs):
        user = self.context['request'].user
        group = attrs.get('group')

        if not (
            group.teacher == user or
            Membership.objects.filter(
                user=user,
                center=group.center,
                role=Membership.Role.ADMIN,
                is_active=True
            ).exists()
        ):
            raise serializers.ValidationError(
                "Siz bu guruh uchun topshiriq yarata olmaysiz."
            )

        return attrs
class GameSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameSession
        fields = (
            'id',
            'assignment',
            'group',
            'mode',
            'session_code',
            'is_active',
            'started_at',
            'ended_at',
        )
        read_only_fields = (
            'id',
            'session_code',
            'started_at',
            'ended_at',
        )

    def create(self, validated_data):
        validated_data['started_at'] = timezone.now()
        return super().create(validated_data)
class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmission
        fields = (
            'id',
            'session',
            'score',
            'is_completed',
            'started_at',
            'finished_at',
        )
        read_only_fields = (
            'id',
            'started_at',
            'finished_at',
        )

    def validate(self, attrs):
        user = self.context['request'].user
        session = attrs['session']
        assignment = session.assignment

        if not Membership.objects.filter(
            user=user,
            center=assignment.group.center,
            role=Membership.Role.STUDENT,
            is_active=True
        ).exists():
            raise serializers.ValidationError(
                "Siz bu topshiriqni bajarish huquqiga ega emassiz."
            )

        return attrs
class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = (
            'id',
            'submission',
            'question',
            'selected_option',
            'is_correct',
            'answered_at',
        )
        read_only_fields = (
            'id',
            'is_correct',
            'answered_at',
        )

    def validate(self, attrs):
        option = attrs['selected_option']
        attrs['is_correct'] = option.is_correct
        return attrs
