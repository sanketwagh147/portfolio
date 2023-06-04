from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import User, userProfile


# post_save.connect(post_create_profile_receiver, sender=User)
@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    if created:
        userProfile.objects.create(user=instance)
        print("create the user profile")

    else:
        try:
            profile = userProfile.objects.get(user=instance)
            profile.save()
            print("user is updated")
        except Exception:
            userProfile.objects.create(user=instance)
            print("profile did not exists but we created one")


@receiver(pre_save, sender=User)
def pre_save_profile_receiver(sender, instance, **kwargs):
    print(instance.username, "this user in being saved")
