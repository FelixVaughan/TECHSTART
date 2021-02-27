from django.db import models
from users.models import User

class Account(Models.model):
    account_name = models.charField(max_length=20) #note: not the same as user_name in Users model
    user = models.ForeignKey(User)
    user_id = models.CharField(max_length=10, default=user.user_id, primary_key=True)
    token = models.CharField(max_length=2048)
    refresh_token = models.CharField(max_length=512, blank=True)
    redirect_uri = models.CharField(max_length=500)
