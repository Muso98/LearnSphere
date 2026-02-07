from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Grade
from core.models import Notification

@receiver(post_save, sender=Grade)
def create_grade_notification(sender, instance, created, **kwargs):
    """
    Yangi baho qo'yilganda o'quvchi va uning ota-onasiga bildirishnoma yuborish.
    """
    if created:
        # 1. O'quvchiga xabar
        student_msg = f"Sizga {instance.subject.name} fanidan yangi baho qo'yildi: {instance.value}."
        if instance.comment:
            student_msg += f" Izoh: {instance.comment}"
        
        Notification.objects.create(
            user=instance.student,
            message=student_msg
        )
        
        # 2. Ota-onalarga xabar
        # accounts.User modelida children M2M maydoni related_name='parents' deb belgilangan
        if hasattr(instance.student, 'parents'):
            parents = instance.student.parents.all()
            for parent in parents:
                student_name = instance.student.get_full_name() or instance.student.username
                parent_msg = f"Farzandingiz {student_name}ga {instance.subject.name} fanidan yangi baho qo'yildi: {instance.value}."
                if instance.comment:
                    parent_msg += f" Izoh: {instance.comment}"
                
                Notification.objects.create(
                    user=parent,
                    message=parent_msg
                )
