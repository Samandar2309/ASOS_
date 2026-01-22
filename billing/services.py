from datetime import timedelta
from django.utils.timezone import now
from django.core.exceptions import ValidationError

from billing.models import Subscription, SubscriptionPlanLimit


class SubscriptionService:
    """
    ENTERPRISE Subscription Service (MODELGA MOS)

    - Activate
    - Expire
    - Limits
    - Features
    """

    # =========================
    # ACTIVATION
    # =========================

    @staticmethod
    def activate(
        subscription: Subscription,
        plan: str,
        days: int = 30,
        gateway: str = "manual",
    ):
        """
        Subscription'ni faollashtirish (manual billing).
        """

        subscription.plan = plan
        subscription.starts_at = now()
        subscription.expires_at = now() + timedelta(days=days)
        subscription.is_active = True
        subscription.payment_gateway = gateway

        subscription.full_clean()
        subscription.save()

    # =========================
    # EXPIRY
    # =========================

    @staticmethod
    def expire_if_needed(subscription: Subscription):
        """
        Muddati tugagan bo‘lsa Free plan’ga tushiradi.
        """

        if subscription.expires_at and subscription.expires_at < now():
            subscription.plan = Subscription.Plan.FREE
            subscription.is_active = False
            subscription.starts_at = None
            subscription.expires_at = None
            subscription.payment_gateway = ""
            subscription.save()

    # =========================
    # LIMITS
    # =========================

    @staticmethod
    def get_plan_limit(subscription: Subscription) -> SubscriptionPlanLimit | None:
        """
        Joriy plan uchun limitlarni olish.
        """
        return SubscriptionPlanLimit.objects.filter(
            plan=subscription.plan
        ).first()

    @staticmethod
    def can_create(subscription: Subscription, resource: str) -> bool:
        """
        students / teachers / groups limitini tekshiradi.
        """

        limit = SubscriptionService.get_plan_limit(subscription)
        if not limit:
            return True

        counters = {
            "students": subscription.center.students_count,
            "teachers": subscription.center.teachers_count,
            "groups": subscription.center.groups_count,
        }

        limits = {
            "students": limit.max_students,
            "teachers": limit.max_teachers,
            "groups": limit.max_groups,
        }

        if resource not in counters:
            return True

        return counters[resource]() < limits[resource]

    # =========================
    # FEATURES
    # =========================

    @staticmethod
    def has_feature(subscription: Subscription, feature: str) -> bool:
        """
        analytics / live_games / custom_branding
        """
        limit = SubscriptionService.get_plan_limit(subscription)
        if not limit:
            return False

        return bool(getattr(limit, f"has_{feature}", False))
