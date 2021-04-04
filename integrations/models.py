from django.db import models
from requests_oauthlib import OAuth2Session
from jsonfield import JSONField
import webbrowser
import os
import django
import json
from django.contrib.auth.models import User
import requests
import tekore  # spotiy api
import praw  # reddit api
import queue
from time import sleep
from tempfile import NamedTemporaryFile
from praw.util.token_manager import FileTokenManager

# Whenever a user is redirected via an api's rauthentication process, the code repsent in the uri is stored here for the calling method to fetch
user_code_queue = queue.Queue()


# Each Entry will contain info about a user pertaining to a specific account
class User_Account_Info(models.Model):
    account_name = models.CharField(max_length=20)  # spotify, facebook, etc. Set by default in subclass implementation constructors
    account_user_name = models.CharField(max_length=30, default="")
    users = models.ForeignKey(User, on_delete=models.CASCADE, default='1')
    user_id = models.CharField(max_length=10)
    token = models.CharField(max_length=2048, default="")
    refresh_token = models.CharField(max_length=512, blank=True)
    token_type = models.CharField(max_length=10, blank=True)
    expires_in = models.CharField(max_length=60, blank=True)
    expires_at = models.CharField(max_length=100, blank=True)

    class Meta:
        abstract = True

class ApiInfo(models.Model):
    """Where the hardcoded values for accessing each API are from

    Notes
    -----
    - This class contains the HARDCODED general values for accessing each API (i.e. details for accessing redit API)
    - The API class is used for data from EACH User to access the API (i.e. details for accessing John Doe's reddit account)

    Attributes
    ----------
    api_name: models.CharField
        The colloquial name of the API

    client_id: models.CharField
        Our client ID for the specified class (i.e. our spotify client_id)

    secret: models.CharField
        Our Secret for the specified class (i.e. our spotify secret)

    base_url: models.CharField
        The base URL for the api (i.e. https://accounts.spotify.com/authorize)

    api_endpoint: models.CharField
        The URL that is used to access various aspects of the api

    token_endpoint: models.CharField
        The endpoint for the token (i.e. https://accounts.spotify.com/api/token)

    redirect_url: models.CharField
        The URL the user gets redirected to after completing authorization

    scope: JSONField
        The amount of access being provisioned

    Notes
    -----
    - while Accounts (and all its children) houses info about users, this class houses info
        on the APIs themselves
    """
    api_name = models.CharField(max_length=20, unique=True, primary_key=True)
    client_id = models.CharField(max_length=100, blank=False, default="N/A")
    secret = models.CharField(max_length=100)
    base_url = models.CharField(max_length=2083, unique=True)
    api_endpoint = models.CharField(max_length=2083, blank=False, default="N/A") #undeeded
    token_endpoint = models.CharField(max_length=2083)
    redirect_url = models.CharField(max_length=500, default="")
    scope = JSONField(max_length=1000, default="")

class Api:  
    """This class takes in user info and info about the api (from APIInfo)
    and uses it to 

    Notes
    -----
    - This class contains the info for each access to the API (i.e. details for accessing John Doe's reddit account)
    - The APIInfo class is used **hardcoded** general values for accessing each API (i.e. details for accessing redit API)
    """
    def __init__(self, user_id, api_name):
        self.user_id = user_id
        self.api_to_contact = api_name
        self.token = ""
        self.refresh_token = ""
        # TODO: Declutter. Create an object of ApiInfo.objects.get(api_name=api_name) and reuse instead of calling every time
        # should probably be changed to an inhouse url before launch
        self.redirect_uri = ApiInfo.objects.get(api_name=api_name).redirect_url
        self.client_id = ApiInfo.objects.get(api_name=api_name).client_id
        self.client_secret = ApiInfo.objects.get(api_name=api_name).secret
        self.base_url = ApiInfo.objects.get(api_name=api_name).base_url
        self.token_endpoint = ApiInfo.objects.get(
            api_name=api_name).token_endpoint
        self.scopeAsJson = ApiInfo.objects.get(api_name=api_name).scope
        if(self.scopeAsJson):  # checks if actually holds data
            self.scope = json.loads(self.scopeAsJson)
        else:
            self.scope = []

    def init_contact(self):  # for first authentication
        api = OAuth2Session(self.client_id, scope=self.scope,
                            redirect_uri=self.redirect_uri)
        auth_url, state = api.authorization_url(self.base_url)
        webbrowser.open(auth_url)
        response = input("Paste URL redirected to: ")
        token = api.fetch_token(
            self.token_endpoint, client_secret=self.client_secret, authorization_response=response)
        user = User.objects.get(user_id=self.user_id)
        # had to use with the spotify table because User_Account_Info is abstract
        user_account_table = Spotify_User_Info.objects.create(
            user_id=self.user_id)
        user_account_table.users.add(user)
        self.populate_user_table(user_account_table, token)

    # Whole method could probably be implemented in a more efficient manner with a for loop but we'd need a way to access all field attributes.
    # should take in a model that is a child of User_Account_Info
    def populate_user_table(self, user_table_ref, given_dict):
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

    def contact_api(self):  # method to be called by threadpool
        pass

    def get_new_token(self):  # uses refresh_token to get a new key
        pass


class Spotify_User_Info(User_Account_Info):
    """Creates a Spotify specific User_Account_Info class to store a user's info
    into a table"""
    account_name = models.CharField(
        max_length=7, default="spotify", editable=False)


class Reddit_User_Info(User_Account_Info):
    """Creates a Reddit specific User_Account_Info class to store a user's info
    into a table"""
    account_name = models.CharField(
        max_length=6, default="reddit", editable=False)


class Discord_User_Info(User_Account_Info):
    """Creates a Discord specific User_Account_Info class to store a user's info
    into a table"""
    account_name = models.CharField(
        max_length=7, default="discord", editable=False)


class SpotifyApi(Api):
    """The specific implementation for 

    Examples
    --------
    #### Add the user with user ID of 1
    ```
    from integrations.models import *

    spot = SpotifyApi(1)
    ```
    """
    def __init__(self, user_id, api_name="spotify"):
        super().__init__(user_id, api_name)
        self.current_user = Spotify_User_Info.objects.get(user_id=user_id)
        # set to blank in parent class. Has to be set here
        self.token = self.current_user.token
        # set to blank in parent class. Has to be set here
        self.refresh_token = self.current_user.refresh_token
    

    def init_contact(self):
        try:
            conf = (self.client_id, self.client_secret, self.redirect_uri)
            scp = tekore.Scope("user-top-read","user-read-recently-played","user-read-playback-position","user-read-playback-state","user-library-read","user-modify-playback-state","user-read-currently-playing","app-remote-control","streaming");
            access_token = tekore.prompt_for_user_token(*conf, scope=scp) 
            self.current_user.token = access_token
            self.current_user.save()
        except KeyError as e:
            print("Authentication with spotify API could NOT be completed as no code was found. Access token NOT set!")
        except Exception as e:
            print("Could not authenticate fully, problem undiagnosed and token not set! ")

    def contact_api(self):  # will def need parameters in the future
        spotify = tekore.Spotify(self.current_user.token)
        tracks = spotify.current_user_top_tracks(limit=10)
        album = spotify.saved_albums(limit=1).items[0].album
        album_uri = tekore.to_uri('album', album.id)
        spotify.playback_start_context(album_uri)
        #here

    def get_new_token(self):  # token is non-expiring so there is no need
        pass


class RedditApi(Api):
    def __init__(self, user_id, api_name="reddit"):
        super().__init__(user_id, api_name)
        self.current_user = Reddit_User_Info.objects.get(user_id=user_id)
        # set to blank in parent class. Has to be set here
        self.token = self.current_user.token
        # set to blank in parent class. Has to be set here
        self.refresh_token = self.current_user.refresh_token

    def init_contact(self):
        reddit = praw.Reddit(client_id=self.client_id, client_secret=self.client_secret, redirect_uri=self.redirect_uri, user_agent="techstart");
        auth_url = reddit.auth.url(["identity"], "permanent")
        webbrowser.open(auth_url)
        waittime = 0
        while not os.path.isfile("./code.txt"):
            sleep(0.2);
            if waittime == 25:
                raise TimeoutError("Could not authenticate")
        f = open("./code.txt", "r")
        code = f.readline()
        f.close()
        os.remove("./code.txt")
        refresh_token =  reddit.auth.authorize(code)
        self.current_user.refresh_token = refresh_token
        self.current_user.save()
        print(reddit.user.me())

    
    def contact_api(self, read):
        pass
        #here


class SpotifyAPIInfo(ApiInfo):
    """The spotify specific ApiInfo subclass"""
    def __init__(self):
        self.api_name = "spotify"
        self.client_id = "eab08f62731b44c4a49010295cd3776f"
        self.secret = "5e4dcc7236ba4cc4b38ca3dbc7f03217" #TODO: make env variable
        self.base_url = "https://accounts.spotify.com/authorize"
        self.token_endpoint = "https://accounts.spotify.com/api/token"
        self.redirect_url = "https://www.spotify.com/ca-en/account/overview/"


class RedditAPIInfo(ApiInfo):
    """The reddit specific ApiInfo subclass"""
    def __init__(self):
        self.api_name = "reddit"
        self.client_id = "RouUl0Nxn9pysw"
        self.secret = "4-KNQ9Z9SsKRvpJzVMs2TGP9V2u-hA" #TODO: make env variable
        self.base_url = "https://www.reddit.com/api/v1/authorize"
        self.token_endpoint = "https://www.reddit.com/api/v1/access_token"
        self.redirect_url = "https://127.0.0.1:8000.api.redirect"
        # self.scope #TODO: Determine scope settings; possibly {'edit':True}

# class DiscordApi(Api):
#     def __init__(self, user_id, api_name="discord"):
#         super().__init__(user_id, api_name)
#         self.current_user = Discord_User_Info.objects.get(user_id=user_id)
#         self.token = self.current_user.token #set to blank in parent class. Has to be set here
#         self.refresh_token = self.current_user.refresh_token #set to blank in parent class. Has to be set here

#     def init_contact(self):
#         pass
