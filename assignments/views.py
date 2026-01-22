from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from .models import (
    Assignment,
    GameSession,
    AssignmentSubmission,
    StudentAnswer,
)
from .serializers import (
    AssignmentSerializer,
    GameSessionSerializer,
    AssignmentSubmissionSerializer,
    StudentAnswerSerializer,
)
from .services import finalize_submission
class AssignmentCreateView(generics.CreateAPIView):
    """
    Teacher yoki Center Admin topshiriq yaratadi
    """
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]
class AssignmentListView(generics.ListAPIView):
    """
    Guruh bo‘yicha topshiriqlarni olish
    """
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        group_id = self.request.query_params.get('group')
        qs = Assignment.objects.filter(is_active=True)

        if group_id:
            qs = qs.filter(group_id=group_id)

        return qs
class StartGameSessionView(generics.CreateAPIView):
    """
    Practice yoki Live session boshlash
    """
    serializer_class = GameSessionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(started_at=timezone.now())
class StartSubmissionView(generics.CreateAPIView):
    """
    Student quizni boshlaydi
    """
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [IsAuthenticated]
class SubmitAnswerView(generics.CreateAPIView):
    """
    Student savolga javob yuboradi
    """
    serializer_class = StudentAnswerSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        answer = serializer.save()

        submission = answer.submission
        quiz = submission.session.assignment.quiz

        # Agar barcha savollarga javob berilgan bo‘lsa → yakunlash
        if submission.answers.count() == quiz.questions.count():
            finalize_submission(submission)
class SubmissionResultView(generics.RetrieveAPIView):
    """
    Quiz yakuniy natijasini ko‘rish
    """
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [IsAuthenticated]
    queryset = AssignmentSubmission.objects.all()
class EndGameSessionView(generics.UpdateAPIView):
    """
    Live sessionni yopish
    """
    serializer_class = GameSessionSerializer
    permission_classes = [IsAuthenticated]
    queryset = GameSession.objects.all()

    def perform_update(self, serializer):
        serializer.save(
            is_active=False,
            ended_at=timezone.now()
        )
