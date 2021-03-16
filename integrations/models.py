from django.db import models
from requests_oauthlib import OAuth2Session
from jsonfield import JSONField
import webbrowser
import os
import django
import json
from users.models import User 
import requests
import tekore #spotiy api
import praw #reddit api
import queue
from time import sleep

user_code_queue = queue.Queue() #Whenever a user is redirected via an api's rauthentication process, the code repsent in the uri is stored here for the calling method to fetch



#Each Entry will contain info about a user pertaining to a specific account
class User_Account_Info(models.Model):
    account_name = models.CharField(max_length=20) #spotify, facebook, etc
    account_user_name = models.CharField(max_length=30, default="")
    users = models.ManyToManyField(User)
    user_id = models.CharField(max_length=10)
    token = models.CharField(max_length=2048, default="")
    refresh_token = models.CharField(max_length=512, blank=True)
    token_type = models.CharField(max_length=10, blank=True)
    expires_in = models.CharField(max_length=60, blank=True)
    expires_at = models.CharField(max_length=100, blank=True)

    class Meta:
        abstract = True

#Each api gives client id and secret after app registration. These are stored here.
#Note: while Accounts (and all its children) houses info about users, this class
#houses info on the APIs themselves 
class ApiInfo(models.Model): 
    api_name = models.CharField(max_length=20, unique=True, primary_key=True) 
    client_id = models.CharField(max_length=100, blank=False, default="N/A")
    secret = models.CharField(max_length=100)
    base_url = models.CharField(max_length=2083, unique=True)
    api_endpoint = models.CharField(max_length=2083, blank=False, default="N/A")
    token_endpoint = models.CharField(max_length=2083)
    redirect_url = models.CharField(max_length=500, default="")
    scope = JSONField(max_length=1000, default="")


#Abstract class for APIS that we will implement 
#by subclassing this class. These classes can further be modified
#by modifying, adding and overriding methods.
class Api:
    def __init__(self,user_id,api_name):
        self.user_id = user_id
        self.api_to_contact = api_name
        self.token = "" 
        self.refresh_token = "" 
        #TODO: Declutter. Create an object of ApiInfo.objects.get(api_name=api_name) and reuse instead of calling every time
        self.redirect_uri = ApiInfo.objects.get(api_name=api_name).redirect_url #should probably be changed to an inhouse url before launch
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
        user = User.objects.get(user_id=self.user_id) 
        user_account_table = Spotify_User_Info.objects.create(user_id=self.user_id) #had to use with the spotify table because User_Account_Info is abstract
        user_account_table.users.add(user)
        self.populate_user_table(user_account_table, token)

    #Whole method could probably be implemented in a more efficient manner with a for loop but we'd need a way to access all field attributes.
    def populate_user_table(self, user_table_ref, given_dict): #should take in a model that is a child of User_Account_Info
        print(f"Populated {user_table_ref.account_name} table with row data: ")
        if "access_token" in given_dict.keys():
            user_table_ref.token = given_dict['access_token']
            print(f"token: {user_table_ref.token}")
        if "refresh_token" in given_dict.keys():
            user_table_ref.refresh_token = given_dict['refresh_token']
            print(f"refresh token: {user_table_ref.refresh_token}")
        if "token_type" in given_dict.keys():
            user_table_ref.token_type = given_dict['token_type']
            print(f"token type: {user_table_ref.token_type}")
        if "expires_in" in given_dict.keys():
            user_table_ref.expires_in = given_dict['expires_in']
            print(f"expires in: {user_table_ref.expires_in}")
        if "expires_at" in given_dict.keys():
            user_table_ref.expires_in = given_dict['expires_at']
            print(f"expires at: {user_table_ref.expires_at}")
        user_table_ref.save()

    def contact_api(self): #method to be called by threadpool 
        pass

    def get_new_token(self): #uses refresh_token to get a new key
        pass

class Spotify_User_Info(User_Account_Info):
    account_name = models.CharField(max_length=7, default="spotify", editable=False)

class Reddit_User_Info(User_Account_Info):
    account_name = models.CharField(max_length=6, default="reddit", editable=False)

class SpotifyApi(Api):
    def __init__(self, user_id, api_name="spotify"):
        super().__init__(user_id, api_name)
        self.user_to_serve = Spotify_User_Info.objects.get(user_id=user_id) 
        self.token = self.user_to_serve.token #set to blank in parent class. Has to be set here
        self.refresh_token = self.user_to_serve.refresh_token #set to blank in parent class. Has to be set here


    def init_contact(self):
        try:
            conf = (self.client_id, self.client_secret, self.redirect_uri)
            access_token = tekore.prompt_for_user_token(*conf, scope=tekore.scope.every)
            self.user_to_serve.token = access_token
            self.user_to_serve.save()

        except Exception as e:
            print("Authentication with spotify API could NOT be completed. access token NOT set!")
        

    def contact_api(self): #will def need parameters in the future
        spotify = tekore.Spotify(self.user_to_serve.token)
        

    def get_new_token(self): #token is non-expiring so there is no need 
        pass 

class RedditApi(Api):
    def __init__(self, user_id, api_name="reddit"):
        super().__init__(user_id, api_name)
        self.user_to_serve = Reddit_User_Info.objects.get(user_id=user_id) 
        self.token = self.user_to_serve.token #set to blank in parent class. Has to be set here
        self.refresh_token = self.user_to_serve.refresh_token #set to blank in parent class. Has to be set here
    

    def init_contact(self):
        reddit = praw.Reddit("platform:zJA0hcGv_sx5AA:V1(by /u/techstartucalgary)") #TODO: change to actual details
        reddit.set_oauth_app_info(client_id=self.client_id, client_secret=self.client_secret, redirect_uri=self.redirect_uri)
        auth_url = reddit.get_authorize_url('read','submit',True)
        while(os.path.isfile("transfer.txt") is False):
            pass
        read_code_from_file = file("transfer.txt","r")
        url_code = read_code_from_file.readline()
        read_code_from_file.close()
        print(url_code)
        access_info = reddit.get_access_information(code) #contains token
        print(access_info)





