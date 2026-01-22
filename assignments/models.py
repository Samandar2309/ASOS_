import uuid
import random
import string
from django.db import models
from django.conf import settings
from django.utils import timezone
from groups.models import Group
class Assignment(models.Model):
    class Type(models.TextChoices):
        QUIZ = 'quiz', 'Quiz'
        PRACTICE = 'practice', 'Practice'
        CHALLENGE = 'challenge', 'Challenge'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='assignments'
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_assignments'
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='assignments/tasks/', null=True, blank=True)

    type = models.CharField(max_length=20, choices=Type.choices)

    xp_reward = models.PositiveIntegerField(
        default=10,
        help_text="Topshiriq yakunlanganda beriladigan XP"
    )

    visible_from = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        unique_together = ('group', 'title')

    def __str__(self):
        return self.title
class Quiz(models.Model):
    assignment = models.OneToOneField(
        Assignment,
        on_delete=models.CASCADE,
        related_name='quiz'
    )
    time_per_question = models.PositiveIntegerField(default=30)
class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    text = models.TextField()
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ('order',)
        unique_together = ('quiz', 'order')
def generate_session_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
class GameSession(models.Model):
    class Mode(models.TextChoices):
        PRACTICE = 'practice', 'Practice'
        LIVE = 'live', 'Live Game'

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    mode = models.CharField(max_length=10, choices=Mode.choices)

    session_code = models.CharField(
        max_length=6,
        unique=True,
        default=generate_session_code
    )

    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
class AssignmentSubmission(models.Model):
    session = models.ForeignKey(
        GameSession,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    score = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('session', 'student')
class AnswerOption(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='options'
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class StudentAnswer(models.Model):
    submission = models.ForeignKey(
        AssignmentSubmission,
        on_delete=models.CASCADE,
        related_name='answers'
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )

    selected_option = models.ForeignKey(
        AnswerOption,
        on_delete=models.CASCADE
    )

    is_correct = models.BooleanField()
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('submission', 'question')
