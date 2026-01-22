from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from billing.models import Subscription, SubscriptionPlanLimit
from billing.services import SubscriptionService


# ======================================================
# SUBSCRIPTION PLAN LIMITS
# ======================================================
@admin.register(SubscriptionPlanLimit)
class SubscriptionPlanLimitAdmin(admin.ModelAdmin):
    list_display = (
        "plan",
        "max_students",
        "max_teachers",
        "max_groups",
        "has_analytics",
        "has_live_games",
        "has_custom_branding",
    )

    list_editable = (
        "max_students",
        "max_teachers",
        "max_groups",
        "has_analytics",
        "has_live_games",
        "has_custom_branding",
    )

    list_filter = ("plan",)
    ordering = ("plan",)


# ======================================================
# SUBSCRIPTIONS
# ======================================================
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "center_link",
        "plan_badge",
        "status_badge",
        "days_remaining",
        "expires_at",
        "payment_gateway",
    )

    list_filter = (
        "plan",
        "is_active",
        "payment_gateway",
    )

    search_fields = (
        "center__name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "days_remaining",
    )

    fieldsets = (
        ("Basic information", {
            "fields": (
                "center",
                "plan",
                "is_active",
            )
        }),
        ("Subscription period", {
            "fields": (
                "starts_at",
                "expires_at",
                "auto_renew",
            )
        }),
        ("Payment", {
            "fields": (
                "payment_gateway",
                "gateway_subscription_id",
            )
        }),
        ("Audit", {
            "fields": (
                "created_at",
                "updated_at",
            ),
            "classes": ("collapse",),
        }),
    )

    actions = (
        "activate_30_days",
        "deactivate_subscription",
    )

    # ==================================================
    # DISPLAY HELPERS
    # ==================================================

    def center_link(self, obj):
        """
        Center sahifasiga link
        """
        url = reverse("admin:centers_center_change", args=[obj.center_id])
        return format_html('<a href="{}"><b>{}</b></a>', url, obj.center.name)

    center_link.short_description = "Center"
    center_link.admin_order_field = "center__name"

    def plan_badge(self, obj):
        """
        Plan rangli badge
        """
        colors = {
            Subscription.Plan.FREE: "#6b7280",        # gray
            Subscription.Plan.PRO: "#2563eb",         # blue
            Subscription.Plan.ENTERPRISE: "#7c3aed",  # purple
        }
        return format_html(
            "<span style='color:{}; font-weight:600'>{}</span>",
            colors.get(obj.plan, "#6b7280"),
            obj.get_plan_display(),
        )

    plan_badge.short_description = "Plan"

    def status_badge(self, obj):
        """
        Aktiv / Aktiv emas holati
        """
        if obj.is_active:
            return format_html(
                "<span style='color:{}; font-weight:600'>ACTIVE</span>",
                "green",
            )
        return format_html(
            "<span style='color:{}; font-weight:600'>INACTIVE</span>",
            "red",
        )

    status_badge.short_description = "Status"

    # ==================================================
    # ADMIN ACTIONS
    # ==================================================

    def activate_30_days(self, request, queryset):
        """
        Subscription'ni 30 kunga faollashtirish (manual billing)
        """
        for subscription in queryset:
            SubscriptionService.activate(
                subscription=subscription,
                plan=subscription.plan,
                days=30,
                gateway="manual",
            )

        self.message_user(
            request,
            f"{queryset.count()} ta subscription 30 kunga faollashtirildi."
        )

    activate_30_days.short_description = "Activate for 30 days (manual)"

    def deactivate_subscription(self, request, queryset):
        """
        Subscription'ni o‘chirish (expire qilish)
        """
        for subscription in queryset:
            SubscriptionService.expire_if_needed(subscription)

        self.message_user(
            request,
            f"{queryset.count()} ta subscription deaktivatsiya qilindi."
        )

    deactivate_subscription.short_description = "Deactivate (expire)"
