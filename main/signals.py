from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment, Debt

@receiver(post_save, sender=Payment)
def remove_debt_if_payment_is_paid(sender, instance, **kwargs):
    if instance.is_paid:
        try:
            debt = instance.debt
            debt.delete()
        except Debt.DoesNotExist:
            pass

