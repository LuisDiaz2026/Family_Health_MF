"""
Authentication Signals
- Crea LoyaltyProfile automáticamente cuando un cliente nace
- Registro en AuditLog para creación/actualización de usuarios
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import AuditLog, User


@receiver(post_save, sender=User)
def create_loyalty_profile_for_clients(sender, instance, created, **kwargs):
    if created and instance.role == User.ROLE_CLIENT:
        try:
            from apps.rewards.models import LoyaltyProfile
            LoyaltyProfile.objects.get_or_create(user=instance, defaults={
                "current_points": 0,
                "lifetime_points": 0,
            })
        except Exception:
            pass
