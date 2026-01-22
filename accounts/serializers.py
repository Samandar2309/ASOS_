from rest_framework import serializers
from .models import User


# ======================================================
# READ-ONLY USER (BOSHQA APP'LAR UCHUN)
# ======================================================
class UserProfileSerializer(serializers.ModelSerializer):
    """
    User profilini faqat o‘qish (read-only) uchun.
    Centers, groups, analytics shu serializerdan foydalanadi.
    """
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "avatar",
            "global_role",
        )
        read_only_fields = fields


# ======================================================
# EMAIL VERIFICATION
# ======================================================
class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)

    def validate_token(self, value):
        if not value:
            raise serializers.ValidationError("Token majburiy")
        if len(value) < 20:
            raise serializers.ValidationError("Token yaroqsiz")
        return value


class ResendVerificationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.only("email_verified").get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "Bu email ro'yxatdan o'tmagan"
            )

        if user.email_verified:
            raise serializers.ValidationError(
                "Email allaqachon tasdiqlangan"
            )

        return value


# ======================================================
# GOOGLE AUTH
# ======================================================
class GoogleAuthSerializer(serializers.Serializer):
    access_token = serializers.CharField(write_only=True)

    def validate_access_token(self, value):
        if not value:
            raise serializers.ValidationError("Access token majburiy")
        if len(value) < 30:
            raise serializers.ValidationError("Google token yaroqsiz")
        return value


# ======================================================
# USER PROFILE (SELF UPDATE)
# ======================================================
class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "phone_number",
            "date_of_birth",
            "avatar",
        )

    def validate_phone_number(self, value):
        if not value:
            return value

        qs = User.objects.filter(phone_number=value)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)

        if qs.exists():
            raise serializers.ValidationError(
                "Bu telefon raqami allaqachon band"
            )
        return value


# ======================================================
# ADMIN USER UPDATE
# ======================================================
class AdminUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "phone_number",
            "global_role",
            "status",
            "is_active",
        )

    def validate(self, attrs):
        request = self.context.get("request")
        if not request or not request.user.is_platform_admin():
            raise serializers.ValidationError(
                "Bu amal faqat Platform Admin uchun ruxsat etilgan"
            )
        return attrs


# ======================================================
# PASSWORD RESET
# ======================================================
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.only("is_active").get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "Bu email bilan foydalanuvchi topilmadi"
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "Account faol emas"
            )

        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )

    def validate_token(self, value):
        if not value or len(value) < 20:
            raise serializers.ValidationError("Token yaroqsiz")
        return value

    def validate_new_password(self, value):
        if value.isdigit():
            raise serializers.ValidationError(
                "Parol faqat raqamlardan iborat bo‘lishi mumkin emas"
            )
        if value.lower() == value:
            raise serializers.ValidationError(
                "Parolda kamida bitta katta harf bo‘lishi kerak"
            )
        return value
