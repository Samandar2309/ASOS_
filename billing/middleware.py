# subscriptions/middleware.py
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import PermissionDenied

from billing.models import Subscription


class SubscriptionMiddleware(MiddlewareMixin):
    """Har bir so'rovda obuna limitlarini tekshirish"""

    EXCLUDED_PATHS = [
        '/admin/',
        '/api/auth/',
        '/api/subscriptions/upgrade/',
        '/api/subscriptions/start_trial/',
        '/api/subscriptions/usage/',
    ]

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Faqat markaz adminlari uchun
        if not hasattr(request.user, 'center_admin_for'):
            return None

        path = request.path
        # Excluded paths
        for excluded in self.EXCLUDED_PATHS:
            if path.startswith(excluded):
                return None

        center = request.user.center_admin_for
        subscription = center.subscription

        # Obuna aktiv emas yoki muddati tugagan bo'lsa
        subscription.deactivate_if_expired()

        # Agar trial bo'lsa, limitlarni tekshirish
        if subscription.is_trial:
            return None

        # Free plan uchun limitlarni tekshirish
        if subscription.plan == Subscription.Plan.FREE:
            # Har bir so'rovda emas, faqat POST so'rovlarida tekshirish
            if request.method == 'POST':
                # Qaysi resource qo'shilayotganini aniqlash
                if 'students' in path:
                    if not subscription.can_add_student(center.students_count()):
                        return JsonResponse(
                            {'error': 'O\'quvchilar limiti tugagan. Iltimos, rejani yangilang.'},
                            status=402  # Payment Required
                        )
                elif 'teachers' in path:
                    if not subscription.can_add_teacher(center.teachers_count()):
                        return JsonResponse(
                            {'error': 'O\'qituvchilar limiti tugagan. Iltimos, rejani yangilang.'},
                            status=402
                        )
                elif 'groups' in path:
                    if not subscription.can_add_group(center.groups_count()):
                        return JsonResponse(
                            {'error': 'Guruhlar limiti tugagan. Iltimos, rejani yangilang.'},
                            status=402
                        )

        return None