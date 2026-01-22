from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from analytics.permissions import IsCenterAdmin
from analytics.services.time_series import get_center_growth


class CenterGrowthAnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsCenterAdmin]

    def get(self, request):
        center = request.user.active_center
        days = int(request.query_params.get("days", 7))

        if days not in (7, 30):
            days = 7

        data = get_center_growth(center=center, days=days)
        return Response(data)
