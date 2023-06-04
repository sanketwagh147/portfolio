from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import User, userProfile


# post_save.connect(post_create_profile_receiver, sender=User)
@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    if created:
        userProfile.objects.create(user=instance)

    else:
        try:
            profile = userProfile.objects.get(user=instance)
            profile.save()
        except Exception:
            userProfile.objects.create(user=instance)


@receiver(pre_save, sender=User)
def pre_save_profile_receiver(sender, instance, **kwargs):
    ...
