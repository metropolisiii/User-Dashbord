from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from dashboard.models import Profile
from dashboard.utils import getUserType

@receiver(post_save, sender=User)
def handle_user_save(sender, instance, created, **kwargs):
  if created:
    type = getUserType(request.user.username)
    Profile.objects.create(user=instance, type=type)
