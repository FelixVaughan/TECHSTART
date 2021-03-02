from django.db import models
from users.models import User
from requests_oauthlib import OAuth2Session
from jsonfield import JSONField
import webbrowser
import os
import django
import json
from users.models import User 

#Each Entry will house info about a user
class Account(models.Model):
    account_name = models.CharField(max_length=20) #note: not the same as user_name in Users model
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=2048,default="")
    refresh_token = models.CharField(max_length=512, blank=True)

    # class Meta:
    #     abstract = True


#Each api gives client id and secret after app registration. These are stored here.
#Note: while Accounts (and all its children) houses info about users, this class
#houses info on the APIs themselves 
class ApiInfo(models.Model): 
    api_name = models.CharField(max_length=20, unique=True, primary_key=True) 
    client_id = models.CharField(max_length=100)
    secret = models.CharField(max_length=100)
    base_url = models.CharField(max_length=2083, unique=True)
    token_endpoint = models.CharField(max_length=2083)
    redirect_u = models.CharField(max_length=500, default="")
    scope = JSONField(max_length=1000, default="")


#Abstract class for APIS that we will implement 
#by subclassing this class. These classes can further be modified
#by modifying, adding and overriding methods.
class Api:
    def __init__(self,user_id,api_name):
        self.user_id = user_id
        self.api_to_contact = api_name
        self.token = Account.objects.get(user_id=self.user_id).token
        self.refresh_token = Account.objects.get(user_id=self.user_id).refresh_token
        self.redirect_uri = ApiInfo.objects.get(api_name=self.api_to_contact).redirect_u
        self.client_id = ApiInfo.objects.get(api_name=api_name).client_id
        self.client_secret = ApiInfo.objects.get(api_name=api_name).secret
        self.base_url = ApiInfo.objects.get(api_name=api_name).base_url
        self.token_endpoint = ApiInfo.objects.get(api_name=api_name).token_endpoint
        self.scopeAsJson = ApiInfo.objects.get(api_name=api_name).scope 
        if(self.scopeAsJson): #checks if actually holds data
            self.scope  = json.loads(self.scopeAsJson)
        else:
            self.scope = []

    def init_contact(self): #for first authentication
        api = OAuth2Session(self.client_id, scope=self.scope, redirect_uri=self.redirect_uri)
        auth_url, state = api.authorization_url(self.base_url)
        webbrowser.open(auth_url)
        response = input("Paste URL redirected to: ")
        token = api.fetch_token(self.token_endpoint, client_secret=self.client_secret, authorization_response=response)
        print(token)

    def contact_api(self): #method to be called by threadpool 
        pass

    def get_new_token(self): #uses refresh_token to get a new key
        pass

