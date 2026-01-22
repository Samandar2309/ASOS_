from django.db import models
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model

User = get_user_model()


class Center(models.Model):
    """O'quv markazi modeli"""

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Faol'
        INACTIVE = 'INACTIVE', 'Nofaol'
        SUSPENDED = 'SUSPENDED', 'To‘xtatilgan'

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Contact information
    email = models.EmailField(null=True, blank=True, default=None)
    phone = models.CharField(max_length=20, blank=True, default='')
    address = models.TextField(null=True, blank=True, default='')
    website = models.URLField(blank=True, null=True, default=None)

    # Center settings
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )

    # Subscription info
    subscription_plan = models.CharField(
        max_length=50,
        choices=[
            ('FREE', 'Free'),
            ('PRO', 'Pro'),
            ('ENTERPRISE', 'Enterprise')
        ],
        default='FREE'
    )
    subscription_end_date = models.DateField(null=True, blank=True)
    max_students = models.IntegerField(default=10)
    max_teachers = models.IntegerField(default=2)

    # Invite system
    invite_code = models.CharField(max_length=20, unique=True, blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_centers'
    )

    class Meta:
        db_table = 'centers'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = get_random_string(8).upper()
        super().save(*args, **kwargs)

    # Helper methods
    def is_active(self):
        return self.status == self.Status.ACTIVE

    def can_add_student(self):
        current_students = self.memberships.filter(
            role=Membership.Role.STUDENT,
            status=Membership.Status.ACTIVE
        ).count()
        return current_students < self.max_students

    def can_add_teacher(self):
        current_teachers = self.memberships.filter(
            role=Membership.Role.TEACHER,
            status=Membership.Status.ACTIVE
        ).count()
        return current_teachers < self.max_teachers

    def groups_count(self):
        """
        Returns the count of groups associated with this center.
        """
        return self.groups.count()


class Membership(models.Model):
    """Foydalanuvchi va markaz o'rtasidagi bog'lanish"""

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Faol'
        INACTIVE = 'INACTIVE', 'Nofaol'
        PENDING = 'PENDING', 'Kutilmoqda'

    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Student'
        TEACHER = 'TEACHER', 'Teacher'
        CENTER_ADMIN = 'CENTER_ADMIN', 'Center Admin'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='memberships'
    )

    center = models.ForeignKey(
        Center,
        on_delete=models.CASCADE,
        related_name='memberships'
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )

    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Additional info
    is_default = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'memberships'
        unique_together = ['user', 'center']
        ordering = ['-joined_at']

    def __str__(self):
        return f"{self.user} - {self.center} ({self.role})"

    def save(self, *args, **kwargs):
        # Agar bu foydalanuvchining birinchi active a'zoligi bo'lsa, uni default qilish
        if self.status == Membership.Status.ACTIVE and not self.user.memberships.filter(is_default=True).exists():
            self.is_default = True
        super().save(*args, **kwargs)
