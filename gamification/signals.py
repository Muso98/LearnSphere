from django.db.models.signals import post_save
from django.dispatch import receiver
from journal.models import Grade
from .models import PointTransaction

@receiver(post_save, sender=Grade)
def award_points_for_grade(sender, instance, created, **kwargs):
    if created:
        points = 0
        if instance.value == 5:
            points = 10
        elif instance.value == 4:
            points = 5
            
        if points > 0:
            PointTransaction.objects.create(
                user=instance.student,
                amount=points,
                transaction_type='grade',
                description=f"{instance.subject.name} fanidan {instance.value} baho uchun"
            )
