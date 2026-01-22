# billing/signals.py
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from centers.models import Membership
from groups.models import Group
from .models import Subscription


@receiver(pre_save, sender=Membership)
def check_student_limit_before_save(sender, instance, **kwargs):
    """
    O'quvchi qo'shilishidan oldin limitni tekshirish
    """
    if instance.role == Membership.Role.STUDENT:
        subscription = instance.center.subscription

        # Agar subscription bo'lmasa, yaratish
        if not hasattr(instance.center, 'subscription'):
            subscription = Subscription.objects.create(
                center=instance.center,
                plan=Subscription.Plan.FREE
            )

        # Limitni tekshirish
        if not subscription.can_add_student(instance.center.students_count()):
            raise ValidationError(
                f"O'quvchilar limiti tugagan. "
                f"Hozir: {instance.center.students_count()}, "
                f"Limit: {subscription.plan_limit.max_students if subscription.plan_limit else 50}"
            )


@receiver(pre_save, sender=Group)
def check_group_limit_before_save(sender, instance, **kwargs):
    # Retrieve the subscription related to the group's center
    # Assuming the Group model has a 'center' field and Center has a subscription relationship
    subscription = instance.center.subscription 
    
    if not subscription.can_add_group(instance.center.groups_count()):
        raise ValidationError("Group limit reached for this subscription.")


@receiver(post_save, sender=Subscription)
def handle_subscription_change(sender, instance, created, **kwargs):
    """
    Obuna o'zgarganda, markaz limitlarini yangilash
    """
    if not created:
        # Obuna plan o'zgarganda eski resurslarni tekshirish
        instance.deactivate_if_expired()

        # Agar limitdan oshib ketgan bo'lsa, log yozish
        usage = instance.get_usage_stats()

        for resource, stats in usage.items():
            if stats.get('percentage', 0) > 100:
                print(f"⚠️ DIQQAT: {instance.center.name} markazi {resource} limitidan oshib ketdi!")
                # Keyinchalik bu yerda email yoki notification yuborish mumkin