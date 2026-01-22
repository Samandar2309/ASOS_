from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import StudentProgress, XPTransaction

User = get_user_model()
class StudentShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
        )
class StudentProgressSerializer(serializers.ModelSerializer):
    student = StudentShortSerializer(read_only=True)

    class Meta:
        model = StudentProgress
        fields = (
            'student',
            'xp_balance',
            'level',
            'last_activity_at',
            'created_at',
        )
        read_only_fields = fields
class XPTransactionSerializer(serializers.ModelSerializer):
    student = StudentShortSerializer(read_only=True)

    class Meta:
        model = XPTransaction
        fields = (
            'id',
            'student',
            'amount',
            'source',
            'submission',
            'created_at',
        )
        read_only_fields = fields
class LeaderboardSerializer(serializers.ModelSerializer):
    student = StudentShortSerializer(read_only=True)

    class Meta:
        model = StudentProgress
        fields = (
            'student',
            'xp_balance',
            'level',
        )
class AdminXPGrantSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)
    reason = serializers.CharField(max_length=255)

    def validate_student_id(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("Student topilmadi.")
        return value
