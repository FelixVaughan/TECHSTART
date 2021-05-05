from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Spotify_User_Info, Reddit_User_Info, Discord_User_Info, Outlook_User_Info


@receiver(post_save, sender=User)
def create_socials(sender, instance, created, **kwargs):
    spot = Spotify_User_Info.objects.get_or_create(users=instance)
    reddit = Reddit_User_Info.objects.get_or_create(users=instance)
    discord = Discord_User_Info.objects.get_or_create(users=instance)
    outlook = Outlook_User_Info.objects.get_or_create(users=instance)
    spot.save()
    reddit.save()
    discord.save()
    outlook.save()


# @receiver(post_save, sender=User)
# def save_socials(sender, instance, created, **kwargs):
#     instance.spotify_user_info.save()
#     instance.reddit_user_info.save()
#     instance.discord_user_info.save()
#     instance.outlook_user_info.save()
