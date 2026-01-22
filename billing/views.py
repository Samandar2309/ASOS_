# subscriptions/api/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.timezone import now
from datetime import timedelta
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.views.generic import DetailView, TemplateView
from .models import Subscription, SubscriptionPlanLimit
from .serializers import (
    SubscriptionSerializer,
    SubscriptionPlanLimitSerializer,
    UpgradeSubscriptionSerializer
)


class RequestUpgradeView(View):
    def get(self, request, *args, **kwargs):
        # Logic for displaying the upgrade request form or info
        return HttpResponse("Upgrade request page")

    def post(self, request, *args, **kwargs):
        # Logic for processing the upgrade
        return HttpResponse("Upgrade processed")


class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Admin barcha obunalarni ko'radi
        if self.request.user.is_staff:
            return Subscription.objects.all()

        # Center admin faqat o'z markazi obunasini ko'radi
        center = getattr(self.request.user, 'center_admin_for', None)
        if center:
            return Subscription.objects.filter(center=center)

        return Subscription.objects.none()

    @action(detail=False, methods=['get'])
    def my_subscription(self, request):
        """Joriy foydalanuvchi markazining obunasi"""
        center = getattr(request.user, 'center_admin_for', None)
        if not center:
            return Response(
                {'error': 'Siz markaz admini emassiz'},
                status=status.HTTP_403_FORBIDDEN
            )

        subscription, created = Subscription.objects.get_or_create(center=center)
        serializer = self.get_serializer(subscription)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def usage(self, request):
        """Foydalanish statistikasi"""
        center = getattr(request.user, 'center_admin_for', None)
        if not center:
            return Response(
                {'error': 'Siz markaz admini emassiz'},
                status=status.HTTP_403_FORBIDDEN
            )

        subscription = center.subscription
        stats = subscription.get_usage_stats()

        return Response({
            'subscription': SubscriptionSerializer(subscription).data,
            'usage': stats,
            'limits': {
                'students': subscription.plan_limit.max_students if subscription.plan_limit else 0,
                'teachers': subscription.plan_limit.max_teachers if subscription.plan_limit else 0,
                'groups': subscription.plan_limit.max_groups if subscription.plan_limit else 0,
            },
            'features': subscription.features
        })

    @action(detail=False, methods=['post'])
    def upgrade(self, request):
        """Plan yangilash"""
        center = getattr(request.user, 'center_admin_for', None)
        if not center:
            return Response(
                {'error': 'Siz markaz admini emassiz'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = UpgradeSubscriptionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        subscription = center.subscription
        new_plan = serializer.validated_data['plan']
        billing_cycle = serializer.validated_data.get('billing_cycle', 'monthly')

        # Limitlarni tekshirish
        new_limit = SubscriptionPlanLimit.objects.filter(plan=new_plan).first()
        if not new_limit:
            return Response(
                {'error': f'{new_plan} rejasi topilmadi'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Yangi plan uchun limitlarni tekshirish
        current_stats = subscription.get_usage_stats()

        for resource in ['students', 'teachers', 'groups']:
            if current_stats[resource]['current'] > getattr(new_limit, f'max_{resource}'):
                return Response({
                    'error': f'{resource} limitidan oshib ketgan. '
                             f'Hozir: {current_stats[resource]["current"]}, '
                             f'Yangida: {getattr(new_limit, f"max_{resource}")}'
                }, status=status.HTTP_400_BAD_REQUEST)

        # Plan yangilash
        subscription.plan = new_plan
        subscription.billing_cycle = billing_cycle
        subscription.activate()

        return Response({
            'success': True,
            'message': f'Plan {subscription.get_plan_display()} ga yangilandi',
            'subscription': SubscriptionSerializer(subscription).data
        })

    @action(detail=False, methods=['post'])
    def start_trial(self, request):
        """Trial boshlash"""
        center = getattr(request.user, 'center_admin_for', None)
        if not center:
            return Response(
                {'error': 'Siz markaz admini emassiz'},
                status=status.HTTP_403_FORBIDDEN
            )

        subscription = center.subscription

        # Agar allaqachon trial yoki to'lov qilingan bo'lsa
        if subscription.is_active and subscription.plan != Subscription.Plan.FREE:
            return Response({
                'error': 'Sizda allaqachon faol obuna mavjud'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Trial boshlash
        subscription.activate_trial()

        return Response({
            'success': True,
            'message': '14 kunlik trial muvaffaqiyatli boshlandi',
            'trial_ends_at': subscription.trial_ends_at,
            'days_remaining': subscription.trial_days_remaining
        })


class SubscriptionPlansView(TemplateView):
    template_name = "billing/plans.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add your logic for plans here
        return context


class SubscriptionPlanLimitViewSet(viewsets.ReadOnlyModelViewSet):
    """Plan limitlarini ko'rish uchun API"""
    queryset = SubscriptionPlanLimit.objects.all()
    serializer_class = SubscriptionPlanLimitSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def all_plans(self, request):
        """Barcha rejalar va ularning xususiyatlari"""
        plans = SubscriptionPlanLimit.objects.all()

        # Agar DB'da planlar yo'q bo'lsa, defaultlarni qo'shamiz
        if not plans.exists():
            defaults = SubscriptionPlanLimit.get_default_limits()
            for plan_key, plan_data in defaults.items():
                SubscriptionPlanLimit.objects.create(
                    plan=plan_key,
                    **{k: v for k, v in plan_data.items() if k != 'description'}
                )
            plans = SubscriptionPlanLimit.objects.all()

        serializer = self.get_serializer(plans, many=True)

        return Response({
            'plans': serializer.data,
            'current_prices': {
                'pro_monthly': 99000,
                'pro_yearly': 990000,
                'enterprise_monthly': 299000,
                'enterprise_yearly': 2990000,
            }
        })


class SubscriptionDetailView(DetailView):
    model = Subscription
    template_name = 'billing/subscription_detail.html'
    context_object_name = 'subscription'