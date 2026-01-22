from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from .models import StudentProgress, XPTransaction
def get_or_create_progress(student):
    """
    Student uchun StudentProgress mavjud bo'lmasa — yaratadi
    """
    progress, _ = StudentProgress.objects.get_or_create(
        student=student
    )
    return progress
@transaction.atomic
def add_xp(
    *,
    student,
    amount: int,
    source: str,
    submission=None
) -> StudentProgress:
    """
    Studentga XP qo'shish:
    - transaction yoziladi
    - level avtomatik yangilanadi
    """
    if amount == 0:
        raise ValidationError("XP miqdori 0 bo‘lishi mumkin emas.")

    progress = get_or_create_progress(student)

    # XP balansini yangilash
    progress.xp_balance += amount
    progress.save(update_fields=['xp_balance'])

    # Levelni yangilash
    progress.update_level()

    # XP transaction (audit)
    XPTransaction.objects.create(
        student=student,
        amount=amount,
        source=source,
        submission=submission
    )

    return progress
@transaction.atomic
def subtract_xp(
    *,
    student,
    amount: int,
    reason: str = 'penalty'
) -> StudentProgress:
    """
    Studentdan XP ayirish (penalty)
    """
    if amount <= 0:
        raise ValidationError("Ayiriladigan XP musbat bo‘lishi kerak.")

    progress = get_or_create_progress(student)

    if progress.xp_balance < amount:
        raise ValidationError("XP balans yetarli emas.")

    progress.xp_balance -= amount
    progress.save(update_fields=['xp_balance'])

    progress.update_level()

    XPTransaction.objects.create(
        student=student,
        amount=-amount,
        source=reason
    )

    return progress
@transaction.atomic
def admin_grant_xp(
    *,
    admin_user,
    student,
    amount: int,
    reason: str
) -> StudentProgress:
    """
    Admin tomonidan XP berish
    """
    if amount <= 0:
        raise ValidationError("XP miqdori musbat bo‘lishi kerak.")

    progress = get_or_create_progress(student)

    progress.xp_balance += amount
    progress.save(update_fields=['xp_balance'])

    progress.update_level()

    XPTransaction.objects.create(
        student=student,
        amount=amount,
        source=XPTransaction.Source.ADMIN
    )

    return progress
def get_global_leaderboard(limit=50):
    """
    Global leaderboard (top XP)
    """
    return StudentProgress.objects.select_related('student') \
        .order_by('-xp_balance')[:limit]
def get_center_leaderboard(center, limit=50):
    """
    Markaz bo‘yicha leaderboard
    """
    return StudentProgress.objects.filter(
        student__memberships__center=center,
        student__memberships__role='student',
        student__memberships__is_active=True
    ).select_related('student') \
     .order_by('-xp_balance')[:limit]
def get_group_leaderboard(group, limit=50):
    """
    Guruh bo‘yicha leaderboard
    """
    return StudentProgress.objects.filter(
        student__enrolled_groups__group=group
    ).select_related('student') \
     .order_by('-xp_balance')[:limit]
