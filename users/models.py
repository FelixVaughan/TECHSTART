from django.db import models
import django


class User(models.Model):
    user_name = models.CharField(max_length = 30, unique=True)
    date_joined = models.DateTimeField(auto_now=True)
    password = models.CharField(max_length = 40)
    user_id = models.CharField(max_length = 10, primary_key = True)
    user_email = models.EmailField(max_length = 40)


