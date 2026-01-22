# billing/models.py
from datetime import timedelta
from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from centers.models import Center


class SubscriptionPlanLimit(models.Model):
    """
    Har bir plan uchun resurs cheklovlari.
    Limitlar DB'da saqlanadi — kodga tegmasdan o'zgartirish mumkin.
    """
    plan = models.CharField(
        max_length=20,
        choices=[("free", "Free"), ("pro", "Pro"), ("enterprise", "Enterprise")],
        unique=True
    )
    max_students = models.PositiveIntegerField(
        help_text="Maksimal o'quvchilar soni",
        default=0
    )
    max_teachers = models.PositiveIntegerField(
        help_text="Maksimal o'qituvchilar soni",
        default=0
    )
    max_groups = models.PositiveIntegerField(
        help_text="Maksimal guruhlar soni",
        default=0
    )
    # FEATURE FLAGS
    has_analytics = models.BooleanField(default=False)
    has_live_games = models.BooleanField(default=False)
    has_custom_branding = models.BooleanField(default=False)
    # NARX MA'LUMOTLARI
    price_monthly = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        help_text="Oylik narx (so'mda)"
    )
    price_yearly = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        help_text="Yillik narx (so'mda)"
    )
    description = models.TextField(blank=True, help_text="Plan tavsifi")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Plan Limit"
        verbose_name_plural = "Plan Limitlari"

    def __str__(self):
        return f"{self.get_plan_display()} Plan Limitlari"

    @classmethod
    def get_default_limits(cls):
        """Default plan limitlarini qaytaradi"""
        return {
            "free": {
                "max_students": 50,
                "max_teachers": 5,
                "max_groups": 10,
                "has_analytics": False,
                "has_live_games": False,
                "has_custom_branding": False,
                "price_monthly": 0,
                "price_yearly": 0,
                "description": "Bepul boshlang'ich reja"
            },
            "pro": {
                "max_students": 200,
                "max_teachers": 20,
                "max_groups": 50,
                "has_analytics": True,
                "has_live_games": True,
                "has_custom_branding": False,
                "price_monthly": 99000,
                "price_yearly": 990000,
                "description": "Professional reja - barcha asosiy funksiyalar"
            },
            "enterprise": {
                "max_students": 1000,
                "max_teachers": 100,
                "max_groups": 200,
                "has_analytics": True,
                "has_live_games": True,
                "has_custom_branding": True,
                "price_monthly": 299000,
                "price_yearly": 2990000,
                "description": "Korporativ reja - maksimal imkoniyatlar"
            }
        }


class Subscription(models.Model):
    """
    Subscription model:
    - Center uchun aktiv reja (plan) holatini saqlaydi
    - Manual billing va kelajakdagi payment gateway'lar uchun tayyor
    """

    class Plan(models.TextChoices):
        FREE = "free", "Free"
        PRO = "pro", "Pro"
        ENTERPRISE = "enterprise", "Enterprise"

    class BillingCycle(models.TextChoices):
        MONTHLY = "monthly", "Oylik"
        YEARLY = "yearly", "Yillik"

    # === ASOSIY ALOQA ===
    center = models.OneToOneField(
        Center,
        on_delete=models.CASCADE,
        related_name="subscription"
    )

    plan = models.CharField(
        max_length=20,
        choices=Plan.choices,
        default=Plan.FREE
    )

    billing_cycle = models.CharField(
        max_length=10,
        choices=BillingCycle.choices,
        default=BillingCycle.MONTHLY
    )

    # === OBUNA DAVRI ===
    starts_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Subscription boshlangan vaqt"
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Subscription tugash vaqti"
    )

    is_active = models.BooleanField(
        default=False,
        help_text="Subscription hozir aktivmi"
    )

    trial_ends_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Trial muddati tugash vaqti"
    )

    # === PAYMENT (FUTURE-PROOF) ===
    payment_gateway = models.CharField(
        max_length=50,
        blank=True,
        help_text="To'lov gateway nomi (payme, click, stripe, manual)"
    )

    gateway_subscription_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Gateway ichidagi subscription ID"
    )

    auto_renew = models.BooleanField(
        default=True,
        help_text="Avtomatik yangilanish"
    )

    # === AUDIT ===
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Obuna"
        verbose_name_plural = "Obunalar"
        indexes = [
            models.Index(fields=['center', 'is_active']),
            models.Index(fields=['expires_at']),
        ]

    # =====================================================
    # BUSINESS METHODS
    # =====================================================

    def clean(self):
        """Validatsiya"""
        if self.expires_at and self.starts_at and self.expires_at <= self.starts_at:
            raise ValidationError("Tugash vaqti boshlanish vaqtidan keyin bo'lishi kerak")

        # Plan limitlarini tekshirish
        if not self.plan_limit and self.plan != self.Plan.FREE:
            raise ValidationError(f"{self.get_plan_display()} rejasi uchun limitlar sozlangan emas")

    def save(self, *args, **kwargs):
        """Saqlashdan oldin to'lov muddatini hisoblash"""
        if not self.pk and self.is_active and self.starts_at and not self.expires_at:
            # Yangi obuna - muddatni hisoblash
            days = 365 if self.billing_cycle == self.BillingCycle.YEARLY else 30
            self.expires_at = self.starts_at + timedelta(days=days)

        self.full_clean()
        super().save(*args, **kwargs)

    def activate(self, days: int = None, gateway: str = "manual"):
        """
        Subscription'ni faollashtirish (manual yoki avtomatik).
        """
        self.plan = self.plan or self.Plan.FREE
        self.starts_at = now()

        # Agar kun berilmasa, billing cycle ga qarab hisoblash
        if days is None:
            days = 365 if self.billing_cycle == self.BillingCycle.YEARLY else 30

        self.expires_at = now() + timedelta(days=days)
        self.is_active = True
        self.payment_gateway = gateway

        self.save()

    def activate_trial(self, trial_days: int = 14):
        """
        Trial rejimini faollashtirish
        """
        self.plan = self.Plan.PRO  # Trial davrida PRO funksiyalardan foydalanish
        self.starts_at = now()
        self.trial_ends_at = now() + timedelta(days=trial_days)
        self.is_active = True
        self.payment_gateway = "trial"
        self.save()

    def deactivate_if_expired(self):
        """
        Agar subscription muddati tugagan bo'lsa — avtomatik o'chadi
        va Free plan'ga tushadi.
        """
        if self.expires_at and self.expires_at < now():
            self.plan = self.Plan.FREE
            self.is_active = False
            self.starts_at = None
            self.expires_at = None
            self.trial_ends_at = None
            self.save()

    def can_add_student(self, current_count: int) -> bool:
        """Yangi o'quvchi qo'shish mumkinmi?"""
        limit = self.plan_limit
        if not limit:
            return True
        return current_count < limit.max_students

    def can_add_teacher(self, current_count: int) -> bool:
        """Yangi o'qituvchi qo'shish mumkinmi?"""
        limit = self.plan_limit
        if not limit:
            return True
        return current_count < limit.max_teachers

    def can_add_group(self, current_count: int) -> bool:
        """Yangi guruh qo'shish mumkinmi?"""
        limit = self.plan_limit
        if not limit:
            return True
        return current_count < limit.max_groups

    def check_limit(self, resource_type: str, current_count: int) -> bool:
        """Har qanday resurs uchun limitni tekshirish"""
        limit_map = {
            'students': ('max_students', self.center.students_count),
            'teachers': ('max_teachers', self.center.teachers_count),
            'groups': ('max_groups', self.center.groups_count),
        }

        if resource_type not in limit_map:
            return True

        limit_field, count = limit_map[resource_type]
        limit = self.plan_limit
        if not limit:
            return True

        max_allowed = getattr(limit, limit_field, 0)
        return count() < max_allowed

    def get_usage_stats(self) -> dict:
        """Foydalanish statistikasi"""
        limit = self.plan_limit
        if not limit:
            return {}

        return {
            'students': {
                'current': self.center.students_count(),
                'max': limit.max_students,
                'percentage': (self.center.students_count() / limit.max_students * 100) if limit.max_students > 0 else 0
            },
            'teachers': {
                'current': self.center.teachers_count(),
                'max': limit.max_teachers,
                'percentage': (self.center.teachers_count() / limit.max_teachers * 100) if limit.max_teachers > 0 else 0
            },
            'groups': {
                'current': self.center.groups_count(),
                'max': limit.max_groups,
                'percentage': (self.center.groups_count() / limit.max_groups * 100) if limit.max_groups > 0 else 0
            }
        }

    # =====================================================
    # PROPERTIES
    # =====================================================

    @property
    def plan_limit(self):
        """Plan limitlarini qaytaradi"""
        try:
            return SubscriptionPlanLimit.objects.get(plan=self.plan)
        except SubscriptionPlanLimit.DoesNotExist:
            # Default limitlarni qaytarish
            default_limits = SubscriptionPlanLimit.get_default_limits()
            if self.plan in default_limits:
                # Agar DB'da yo'q bo'lsa ham, default limitlarni ko'rsatish
                class MockLimit:
                    def __init__(self, data):
                        for key, value in data.items():
                            setattr(self, key, value)

                return MockLimit(default_limits[self.plan])
            return None

    @property
    def days_remaining(self) -> int:
        """Subscription tugashiga qolgan kunlar soni"""
        if self.expires_at and self.is_active:
            remaining = self.expires_at - now()
            return max(remaining.days, 0)
        return 0

    @property
    def is_expired(self) -> bool:
        """Subscription muddati tugaganmi"""
        return bool(self.expires_at and self.expires_at < now())

    @property
    def is_trial(self) -> bool:
        """Trial rejimidami?"""
        return bool(self.trial_ends_at and self.trial_ends_at > now())

    @property
    def trial_days_remaining(self) -> int:
        """Trial qolgan kunlari"""
        if self.trial_ends_at:
            remaining = self.trial_ends_at - now()
            return max(remaining.days, 0)
        return 0

    @property
    def current_price(self) -> float:
        """Joriy narx"""
        limit = self.plan_limit
        if not limit:
            return 0.0

        if self.billing_cycle == self.BillingCycle.YEARLY:
            return float(limit.price_yearly)
        return float(limit.price_monthly)

    @property
    def features(self) -> dict:
        """Planning imkoniyatlari"""
        limit = self.plan_limit
        if not limit:
            return {}

        return {
            'analytics': limit.has_analytics,
            'live_games': limit.has_live_games,
            'custom_branding': limit.has_custom_branding,
        }

    def __str__(self):
        return f"{self.center.name} — {self.get_plan_display()}"