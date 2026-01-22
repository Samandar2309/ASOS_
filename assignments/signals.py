from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import AssignmentSubmission
from progress.models import StudentProgress, XPTransaction
@receiver(post_save, sender=AssignmentSubmission)
def award_xp_on_submission_complete(sender, instance, created, **kwargs):
    """
    AssignmentSubmission yakunlanganda:
    - studentga XP beriladi
    - faqat 1 marta
    """

    # Faqat yakunlangan submission
    if not instance.is_completed:
        return

    # Takroran XP berilishining oldini olish
    if XPTransaction.objects.filter(submission=instance).exists():
        return

    student = instance.student
    assignment = instance.session.assignment
    xp_amount = assignment.xp_reward

    # Student progress
    progress, _ = StudentProgress.objects.get_or_create(
        student=student
    )

    progress.xp_balance += xp_amount
    progress.save(update_fields=['xp_balance'])

    # XP log (audit / analytics uchun juda muhim)
    XPTransaction.objects.create(
        student=student,
        amount=xp_amount,
        source='assignment',
        submission=instance
    )
