# subscriptions/api/serializers.py
from rest_framework import serializers
from .models import Subscription, SubscriptionPlanLimit
from centers.models import Center


class SubscriptionPlanLimitSerializer(serializers.ModelSerializer):
    plan_display = serializers.CharField(source='get_plan_display', read_only=True)

    class Meta:
        model = SubscriptionPlanLimit
        fields = [
            'id', 'plan', 'plan_display', 'max_students', 'max_teachers',
            'max_groups', 'has_analytics', 'has_live_games',
            'has_custom_branding', 'price_monthly', 'price_yearly', 'description'
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    center_name = serializers.CharField(source='center.name', read_only=True)
    plan_display = serializers.CharField(source='get_plan_display', read_only=True)
    billing_cycle_display = serializers.CharField(source='get_billing_cycle_display', read_only=True)
    plan_limit = SubscriptionPlanLimitSerializer(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    trial_days_remaining = serializers.IntegerField(read_only=True)
    current_price = serializers.FloatField(read_only=True)
    features = serializers.DictField(read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id', 'center', 'center_name', 'plan', 'plan_display',
            'billing_cycle', 'billing_cycle_display', 'is_active',
            'starts_at', 'expires_at', 'trial_ends_at',
            'payment_gateway', 'auto_renew', 'days_remaining',
            'trial_days_remaining', 'current_price', 'features',
            'plan_limit', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'days_remaining',
            'trial_days_remaining', 'current_price', 'features'
        ]


class UpgradeSubscriptionSerializer(serializers.Serializer):
    plan = serializers.ChoiceField(choices=Subscription.Plan.choices)
    billing_cycle = serializers.ChoiceField(
        choices=Subscription.BillingCycle.choices,
        default='monthly',
        required=False
    )

    def validate(self, data):
        center = self.context['request'].user.center_admin_for
        if not center:
            raise serializers.ValidationError("Siz markaz admini emassiz")

        # Yangi plan joriy plandan yuqori bo'lishi kerak
        current_plan = center.subscription.plan
        plan_hierarchy = {
            Subscription.Plan.FREE: 0,
            Subscription.Plan.PRO: 1,
            Subscription.Plan.ENTERPRISE: 2
        }

        if plan_hierarchy[data['plan']] <= plan_hierarchy[current_plan]:
            raise serializers.ValidationError(
                "Yangilash uchun yuqoriroq rejani tanlang"
            )

        return data