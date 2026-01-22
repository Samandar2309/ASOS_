from django.urls import path

from .views import (
    AssignmentCreateView,
    AssignmentListView,
    StartGameSessionView,
    EndGameSessionView,
    StartSubmissionView,
    SubmitAnswerView,
    SubmissionResultView,
)
urlpatterns = [
    # Assignments
    path('assignments/', AssignmentListView.as_view(), name='assignment-list'),
    path('assignments/create/', AssignmentCreateView.as_view(), name='assignment-create'),

    # Game sessions
    path('sessions/start/', StartGameSessionView.as_view(), name='session-start'),
    path('sessions/<int:pk>/end/', EndGameSessionView.as_view(), name='session-end'),

    # Student flow
    path('submissions/start/', StartSubmissionView.as_view(), name='submission-start'),
    path('answers/submit/', SubmitAnswerView.as_view(), name='answer-submit'),
    path('submissions/<int:pk>/', SubmissionResultView.as_view(), name='submission-result'),
]
