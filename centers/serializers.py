from rest_framework import serializers
from .models import Center, Membership
from accounts.serializers import UserProfileSerializer


class CenterSerializer(serializers.ModelSerializer):
    """Markaz serializeri"""

    member_count = serializers.SerializerMethodField()
    can_join = serializers.SerializerMethodField()

    class Meta:
        model = Center
        fields = [
            'id',
            'name',
            'description',
            'email',
            'phone',
            'address',
            'status',
            'invite_code',
            'member_count',
            'can_join',
            'created_at'
        ]
        read_only_fields = ['id', 'invite_code', 'created_at']

    def get_member_count(self, obj):
        return obj.memberships.filter(status='ACTIVE').count()

    def get_can_join(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return not obj.memberships.filter(user=request.user, status='ACTIVE').exists()
        return False


class MembershipSerializer(serializers.ModelSerializer):
    """A'zolik serializeri"""

    user = UserProfileSerializer(read_only=True)
    center = CenterSerializer(read_only=True)

    class Meta:
        model = Membership
        fields = [
            'id',
            'user',
            'center',
            'role',
            'status',
            'joined_at',
            'is_default'
        ]
        read_only_fields = ['id', 'joined_at']


class CreateCenterSerializer(serializers.ModelSerializer):
    """Markaz yaratish serializeri"""

    class Meta:
        model = Center
        fields = ['name', 'description', 'email', 'phone', 'address', 'website']

    def create(self, validated_data):
        request = self.context.get('request')
        center = Center.objects.create(
            **validated_data,
            created_by=request.user
        )

        # Yaratgan foydalanuvchini Center Admin qilish
        Membership.objects.create(
            user=request.user,
            center=center,
            role='CENTER_ADMIN',
            status='ACTIVE',
            is_default=True
        )

        return center