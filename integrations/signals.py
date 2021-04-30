from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Spotify_User_Info, Reddit_User_Info, Discord_User_Info, Outlook_User_Info


@receiver(post_save, sender=User)
def create_socials(sender, instance, created, **kwargs):
    if created:
        Spotify_User_Info.objects.create(users=instance)
        Reddit_User_Info.objects.create(users=instance)
        Discord_User_Info.objects.create(users=instance)
        Outlook_User_Info.objects.create(users=instance)


@receiver(post_save, sender=User)
def save_socials(sender, instance, created, **kwargs):
    instance.spotify_user_info.save()
    instance.reddit_user_info.save()
    instance.discord_user_info.save()
    instance.outlook_user_info.save()
