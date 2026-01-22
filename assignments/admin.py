from django.contrib import admin
from .models import (
    Assignment,
    Quiz,
    Question,
    AnswerOption,
    GameSession,
    AssignmentSubmission,
    StudentAnswer
)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'type', 'xp_reward', 'is_active', 'created_at')
    list_filter = ('type', 'group', 'is_active')
    search_fields = ('title',)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'time_per_question')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'order', 'text')
    ordering = ('quiz', 'order')


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ('question', 'text', 'is_correct')


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'group', 'mode', 'session_code', 'is_active')


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'session', 'score', 'is_completed')


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('submission', 'question', 'selected_option', 'is_correct')
