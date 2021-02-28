from django.db import models
from users.models import User

class Account(models.Model):
    account_name = models.CharField(max_length=20) #note: not the same as user_name in Users model
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=2048)
    refresh_token = models.CharField(max_length=512, blank=True)
    redirect_uri = models.CharField(max_length=500)


class Secrets(models.Model):
    API = models.CharField(max_length=20)
    secret = models.CharField(max_length=60)
    #Each application that we sign our app up with will give us a personal client secret
    #the mappings of which will be stored here.