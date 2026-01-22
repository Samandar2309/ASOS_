import uuid
import random
import string

from django.db import models
from django.conf import settings

from centers.models import Center
def generate_invite_code():
    """
    Masalan: A9F3KQ
    """
    return ''.join(
        random.choices(string.ascii_uppercase + string.digits, k=6)
    )
class Group(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    center = models.ForeignKey(
        Center,
        on_delete=models.CASCADE,
        related_name='groups'
    )

    name = models.CharField(
        max_length=255,
        verbose_name="Guruh nomi"
    )

    subject = models.CharField(
        max_length=100,
        verbose_name="Fan nomi"
    )

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teaching_groups'
    )

    invite_code = models.CharField(
        max_length=6,
        unique=True,
        default=generate_invite_code,
        editable=False,
        verbose_name="Taklif kodi"
    )

    max_students = models.PositiveIntegerField(
        default=30,
        verbose_name="Maksimal o‘quvchilar soni"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Faol"
    )

    is_archived = models.BooleanField(
        default=False,
        verbose_name="Arxivlangan"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ('-created_at',)
        unique_together = ('center', 'name')
        verbose_name = "Guruh"
        verbose_name_plural = "Guruhlar"

    def __str__(self):
        return f"{self.name} | {self.subject} | {self.center.name}"
class GroupStudent(models.Model):
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='students'
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='group_memberships'
    )

    joined_at = models.DateTimeField(
        auto_now_add=True
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Faol a’zolik"
    )

    class Meta:
        unique_together = ('group', 'student')
        verbose_name = "Guruh o‘quvchisi"
        verbose_name_plural = "Guruh o‘quvchilari"

    def __str__(self):
        return f"{self.student} → {self.group.name}"
