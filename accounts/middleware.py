# accounts/middleware.py

from django.utils import timezone
from datetime import timedelta


class UpdateLastActiveMiddleware:
    """
    Authenticated user'ning last_active_at maydonini yangilaydi.
    DB'ni har request'da urmaslik uchun throttle qo‘llanadi.
    """

    UPDATE_INTERVAL = timedelta(minutes=5)

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return response

        now = timezone.now()

        if (
            not user.last_active_at
            or now - user.last_active_at >= self.UPDATE_INTERVAL
        ):
            user.last_active_at = now
            user.save(update_fields=["last_active_at"])

        return response
