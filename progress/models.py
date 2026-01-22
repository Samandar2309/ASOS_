from django.db import models
from django.conf import settings
from django.utils import timezone
class StudentProgress(models.Model):
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='progress'
    )

    xp_balance = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)

    last_activity_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Student Progress"
        verbose_name_plural = "Students Progress"

    def __str__(self):
        return f"{self.student} | XP: {self.xp_balance} | Level: {self.level}"
    def calculate_level(self) -> int:
        """
        Progressive level calculation:
        1-level:   0 – 99 XP
        2-level: 100 – 249 XP
        3-level: 250 – 499 XP
        4-level: 500 – 899 XP
        keyin geometrik o‘sadi
        """
        xp = self.xp_balance

        if xp < 100:
            return 1
        elif xp < 250:
            return 2
        elif xp < 500:
            return 3
        elif xp < 900:
            return 4

        # 5-leveldan keyin dinamik formula
        return int((xp / 500) ** 0.5) + 4
    def update_level(self):
        new_level = self.calculate_level()
        if new_level != self.level:
            self.level = new_level
            self.save(update_fields=['level'])
class XPTransaction(models.Model):
    class Source(models.TextChoices):
        ASSIGNMENT = 'assignment', 'Assignment'
        CHALLENGE = 'challenge', 'Challenge'
        BONUS = 'bonus', 'Bonus'
        ADMIN = 'admin', 'Admin grant'

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='xp_transactions'
    )

    amount = models.IntegerField(help_text="XP miqdori (+ yoki - bo‘lishi mumkin)")
    source = models.CharField(max_length=20, choices=Source.choices)

    # Qayerdan kelganini aniqlash uchun
    submission = models.ForeignKey(
        'assignments.AssignmentSubmission',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "XP Transaction"
        verbose_name_plural = "XP Transactions"

    def __str__(self):
        return f"{self.student} | {self.amount} XP | {self.source}"
