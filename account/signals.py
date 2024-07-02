from django.db.models.signals import post_save
from django.dispatch import receiver
from user.models import User
from .models import Account


@receiver(post_save, sender=User)
def create_account(instance, created, **kwargs):
    if created:
        Account.objects.create(
            user=instance,
            account_number=instance.phone[1:]
        )
