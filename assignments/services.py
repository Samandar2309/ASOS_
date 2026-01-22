from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import (
    GameSession,
    AssignmentSubmission,
    StudentAnswer,
)
@transaction.atomic
def finalize_submission(submission: AssignmentSubmission) -> AssignmentSubmission:
    """
    Student barcha savollarga javob bergach:
    - avtomatik baholaydi
    - score hisoblaydi
    - submission’ni yopadi
    """
    if submission.is_completed:
        return submission

    quiz = submission.session.assignment.quiz
    total_questions = quiz.questions.count()

    if total_questions == 0:
        raise ValidationError("Quizda savollar yo‘q.")

    correct_answers = submission.answers.filter(is_correct=True).count()

    score = int((correct_answers / total_questions) * 100)

    submission.score = score
    submission.is_completed = True
    submission.finished_at = timezone.now()
    submission.save(
        update_fields=['score', 'is_completed', 'finished_at']
    )

    return submission
@transaction.atomic
def submit_answer(
    submission: AssignmentSubmission,
    question,
    selected_option
) -> StudentAnswer:
    """
    Bitta savolga javob berish:
    - duplicate yo‘q
    - to‘g‘riligini aniqlash
    """
    if submission.is_completed:
        raise ValidationError("Bu submission allaqachon yopilgan.")

    if StudentAnswer.objects.filter(
        submission=submission,
        question=question
    ).exists():
        raise ValidationError("Bu savolga allaqachon javob berilgan.")

    answer = StudentAnswer.objects.create(
        submission=submission,
        question=question,
        selected_option=selected_option,
        is_correct=selected_option.is_correct
    )

    return answer
@transaction.atomic
def start_game_session(session: GameSession) -> GameSession:
    """
    Session’ni ishga tushirish
    """
    if session.started_at:
        raise ValidationError("Session allaqachon boshlangan.")

    session.started_at = timezone.now()
    session.is_active = True
    session.save(update_fields=['started_at', 'is_active'])

    return session
@transaction.atomic
def end_game_session(session: GameSession) -> GameSession:
    """
    Live session’ni yopish
    """
    if not session.is_active:
        return session

    session.is_active = False
    session.ended_at = timezone.now()
    session.save(update_fields=['is_active', 'ended_at'])

    return session
def is_submission_finished(submission: AssignmentSubmission) -> bool:
    """
    Barcha savollarga javob berilganmi?
    """
    quiz = submission.session.assignment.quiz
    total_questions = quiz.questions.count()
    answered = submission.answers.count()

    return answered >= total_questions
def is_session_active(session: GameSession) -> bool:
    """
    Session hozir faolmi?
    """
    if not session.is_active:
        return False

    if session.ended_at:
        return False

    return True
