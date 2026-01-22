from django.urls import path
from billing.views import (
    SubscriptionDetailView,
    SubscriptionPlansView,
    RequestUpgradeView,
)

urlpatterns = [
    path("subscription/", SubscriptionDetailView.as_view()),
    path("plans/", SubscriptionPlansView.as_view()),
    path("request-upgrade/", RequestUpgradeView.as_view()),
]
