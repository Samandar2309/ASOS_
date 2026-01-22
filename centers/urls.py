from django.urls import path
from .views import MyCenterView, UpdateCenterView

urlpatterns = [
    path('me/', MyCenterView.as_view()),
    path('me/update/', UpdateCenterView.as_view()),
]
