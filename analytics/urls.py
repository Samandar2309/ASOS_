from django.urls import path
from analytics.views import CenterAnalyticsSummaryView
from analytics.growth import CenterGrowthAnalyticsView

urlpatterns = [
    path(
        "center/summary/",
        CenterAnalyticsSummaryView.as_view(),
        name="center-analytics-summary",
    ),
    path("center/growth/",
         CenterGrowthAnalyticsView.as_view(),
         name="center-growth-analytics", )
]
