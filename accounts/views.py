from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from . import services
from .serializers import (
    # email
    EmailVerificationSerializer,
    ResendVerificationEmailSerializer,

    # google
    GoogleAuthSerializer,

    # profile
    UserProfileUpdateSerializer,

    # admin
    AdminUserUpdateSerializer,

    # password reset
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from .permissions import IsPlatformAdmin


# ======================================================
# EMAIL VERIFICATION
# ======================================================
class EmailVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = services.verify_email_by_token(
                serializer.validated_data["token"]
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tokens = services.generate_jwt_for_user(user)

        return Response(
            {
                "success": True,
                "message": "Email muvaffaqiyatli tasdiqlandi",
                "tokens": tokens,
            },
            status=status.HTTP_200_OK,
        )


class ResendVerificationEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResendVerificationEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(email=serializer.validated_data["email"])
        services.send_email_verification(user)

        return Response(
            {
                "success": True,
                "message": "Tasdiqlash email qayta yuborildi",
            },
            status=status.HTTP_200_OK,
        )


# ======================================================
# GOOGLE AUTH
# ======================================================
class GoogleOAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = services.authenticate_with_google(
                serializer.validated_data["access_token"]
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tokens = services.generate_jwt_for_user(user)

        return Response(
            {
                "success": True,
                "tokens": tokens,
            },
            status=status.HTTP_200_OK,
        )


# ======================================================
# PROFILE (SELF)
# ======================================================
class UserProfileUpdateView(generics.UpdateAPIView):
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# ======================================================
# ADMIN - USER MANAGEMENT
# ======================================================
class AdminUserManagementView(generics.UpdateAPIView):
    """
    Platform admin uchun user update:
    role, status, is_active
    """
    queryset = User.objects.all()
    serializer_class = AdminUserUpdateSerializer
    permission_classes = [IsAuthenticated, IsPlatformAdmin]


# ======================================================
# PASSWORD RESET
# ======================================================
class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(email=serializer.validated_data["email"])
        services.send_password_reset_email(user)

        return Response(
            {
                "success": True,
                "message": "Parolni tiklash uchun email yuborildi",
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            services.reset_password(
                raw_token=serializer.validated_data["token"],
                new_password=serializer.validated_data["new_password"],
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "success": True,
                "message": "Parol muvaffaqiyatli yangilandi",
            },
            status=status.HTTP_200_OK,
        )
