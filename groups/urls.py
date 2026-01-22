from django.urls import path
from .views import (
    GroupListCreateView,
    GroupDetailView,
    GroupStudentAddView,
    GroupStudentRemoveView,
)

urlpatterns = [
    path('', GroupListCreateView.as_view()),
    path('<uuid:pk>/', GroupDetailView.as_view()),
    path('<uuid:group_id>/students/add/', GroupStudentAddView.as_view()),
    path(
        '<uuid:group_id>/students/<int:student_id>/remove/',
        GroupStudentRemoveView.as_view()
    ),
]
