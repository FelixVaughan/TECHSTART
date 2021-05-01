from django.contrib import admin
from .models import Spotify_User_Info, Reddit_User_Info, Discord_User_Info, Outlook_User_Info

# Register your models here.
admin.site.register(Spotify_User_Info)
admin.site.register(Reddit_User_Info)
admin.site.register(Discord_User_Info)
admin.site.register(Outlook_User_Info)
