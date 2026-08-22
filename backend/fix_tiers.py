"""Actualiza los tiers de los LoyaltyProfile existentes (Bronce para 0 pts)."""
import os, sys, django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.rewards.models import LoyaltyProfile

count = 0
for profile in LoyaltyProfile.objects.all():
    old_tier = profile.tier_id
    profile._update_tier()
    new_tier = profile.tier_id
    if old_tier != new_tier:
        profile.save(update_fields=["tier", "updated_at"])
        count += 1
        print(f"Actualizado {profile.user.username}: {old_tier} -> {profile.tier.name if profile.tier else 'Ninguno'}")

print(f"Perfiles actualizados: {count}")
print(f"Total LoyaltyProfile: {LoyaltyProfile.objects.count()}")
