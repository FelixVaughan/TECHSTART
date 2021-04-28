from typing import Tuple
from django.db import models
from requests_oauthlib import OAuth2Session
from jsonfield import JSONField
import webbrowser
import os
import django
import json
import urllib
from datetime import datetime, timedelta
from django.contrib.auth.models import User
import requests
import tekore  # spotiy api
import praw  # reddit api
from time import sleep
from tempfile import NamedTemporaryFile
from praw.util.token_manager import FileTokenManager
from pyOutlook import OutlookAccount
from O365 import Account
from urllib.parse import urlencode
from django.contrib.sessions.models import Session

def local_code_flow():
    waittime = 0
    code = ""
    try:
        while not os.path.isfile("./code.txt"):
            sleep(0.1)
            waittime+=1 #10 == 1sec
            if (waittime == 350): #35 seconds
                print("Session timed out. Could not authenticate. Code NOT aquired")
                return ""
        f = open("./code.txt", "r")
        code = str(f.readline())
        f.close()
    except Exception as e:
        if(len(code) == 0):
            print("Local error occured. code NOT aquired")
            print(e)
    finally:
        if os.path.exists("./code.txt"):
            os.remove("./code.txt")
    return code

class User_Account_Info(models.Model):
    account_name = models.CharField(max_length=20)  # spotify, facebook, etc. Set by default in subclass implementation constructors
    account_user_name = models.CharField(max_length=30, default="")
    # users = models.ForeignKey(User, on_delete=models.CASCADE, default='1')
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
    def __init__(self, user_id, api_name, info_class):
        self.user_id = user_id
        self.api_to_contact = api_name
        self.token = ""
        self.refresh_token = ""
        self.redirect_uri = info_class().redirect_url
        self.client_id = info_class().client_id
        self.client_secret = info_class().secret
        self.base_url = info_class().base_url
        self.token_endpoint = info_class().token_endpoint
        self.scope = info_class().scope


    def init_contact(self):  # for first authentication
        api = OAuth2Session(self.client_id, scope=self.scope, redirect_uri=self.redirect_uri)
        auth_url, state = api.authorization_url(self.base_url)
        webbrowser.open(auth_url)
        response = input("Paste URL redirected to: ")
        token = api.fetch_token(self.token_endpoint, client_secret=self.client_secret, authorization_response=response)
        user = User.objects.get(user_id=self.user_id)
        user_account_table = Spotify_User_Info.objects.create(user_id=self.user_id)
        user_account_table.users.add(user)
        self.populate_user_table(user_account_table, token)

    # Whole method could probably be implemented in a more efficient manner with a for loop but we'd need a way to access all field attributes.
    # should take in a model that is a child of User_Account_Info
    def populate_user_table(self, user_table_ref, given_dict):
        print(f"Populating {user_table_ref.account_name} table with row data: ")
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
    account_name = models.CharField(
        max_length=7, default="spotify", editable=False)
    users = models.OneToOneField(User, on_delete=models.CASCADE, default='1')

class Reddit_User_Info(User_Account_Info):
    account_name = models.CharField(
        max_length=6, default="reddit", editable=False)
    users = models.OneToOneField(User, on_delete=models.CASCADE, default='1')


class Discord_User_Info(User_Account_Info):
    account_name = models.CharField(
        max_length=7, default="discord", editable=False)

class Outlook_User_Info(User_Account_Info):
    account_name = models.CharField(
        max_length=7, default="outlook", editable=False)
    users = models.OneToOneField(User, on_delete=models.CASCADE, default='1')

class News_User_Info(User_Account_Info):
    account_name = models.CharField(
        max_length=7, default="newsapi", editable=False)
    preferences = models.CharField(max_length=100, default="")
    

class SpotifyApi(Api):
    def __init__(self, user_id, api_name="spotify"):
        super().__init__(user_id, api_name, SpotifyAPIInfo)
        self.current_user = Spotify_User_Info.objects.get(user_id=user_id)
        self.token = self.current_user.token
        self.refresh_token = self.current_user.refresh_token
        self.conf = (self.client_id, self.client_secret, self.redirect_uri)
        self.spotify_auth = tekore.RefreshingCredentials(client_id=self.client_id, client_secret=self.client_secret, redirect_uri=self.redirect_uri)
        self.spotify = None
        if(self.current_user.token):
            self.spotify = tekore.Spotify(self.current_user.token)

    def init_contact(self):
        try:
            auth_url = self.spotify_auth.user_authorisation_url(scope=self.scope)
            webbrowser.open(auth_url)
        except KeyError as e:
            print("Authentication with spotify API could NOT be completed as no code was found. Access token NOT set!")
        except Exception as e:
            print(e)
    
    def obtain_token(self, code):
        try:
            access_token = self.spotify_auth.request_user_token(code)
            self.current_user.token = access_token
            self.current_user.refresh_token = access_token.refresh_token
            self.current_user.save()
            print(f"spotify token set to {token}")
        except KeyError as e:
            print("Authentication with spotify API could NOT be completed as no code was found. Access token NOT set!")
        except Exception as e:
            print(e)

    def contact_api(self, album_uri:str = "") -> dict:  # will def need parameters in the future
        """Contacts Spotify API and returns a dictionary of values

        parameters
        ----------
        album_uri (optional):
            If you want to play a specific album pass the URI as a string here to play it

        References
        ----------
        - PrivateUser docs: https://tekore.readthedocs.io/en/stable/reference/models.html?highlight=privateuser#tekore.model.PrivateUser
        - FullTrackPaging docs: https://tekore.readthedocs.io/en/stable/reference/models.html#tekore.model.FullTrackPaging
        - FullArtist docs: https://tekore.readthedocs.io/en/stable/reference/models.html?highlight=FullArtist#tekore.model.FullArtist

        Returns
        -------
        dict
            A dictionary with 3 keys:

                1. 'current_user'; a PrivateUser of the provided users account 
                2. 'top_tracks'; a FullTrackPaging of the provided users most listened to songs 
                3. 'top_artist'; a FullArtist of the provided users most listened to artist

        Throws
        ------
        tekore.NotFound:
            This error is thrown if you try to set an album to play and there's no device
            currently active on the user's account

        Examples
        --------
        ### Creating a user in django shell 
        ```
        import random
        import string
        from integrations.models import *
        from django.contrib.auth.models import User

        # Create user
        ran_name = lambda n: ''.join([random.choice(string.ascii_lowercase) for i in range(n)])
        user=User.objects.create_user(ran_name(random.randint(0, 10)), password='bar')
        user.save()
        
        # Add user to Spotify_User_Info table
        entry = Spotify_User_Info(user_id=user.id, account_name="yeet")
        entry.save()
        user.spotify_user_info_set.add(entry)
        user.save()

        # Initialize and access the spotify api
        spot = SpotifyApi(user.id)
        spot.init_contact()

        ... # need to wait to paste url and finalize initialization 

        # Contact API and get data
        data = SpotifyApi(user.id).contact_api()
        ```
        """

        user_values = {}
        try:
            spotify = tekore.Spotify(self.current_user.token)

            user_values["current_user"] = spotify.current_user()
            user_values["top_tracks"] = spotify.current_user_top_tracks(limit=10)

            if album_uri:
                spotify.playback_start_context(album_uri)

            # Set object attributes
            user_values["top_artist"] = spotify.current_user_top_artists(limit=1).items[0]
            #here
            print(user_values)
            return user_values
        except tekore.ServiceUnavailable as err:
            print("It looks like you are currently not logged into spotify...")
        except Exception as e:
            self.get_new_token(True)

    def get_new_token(self,retry): #retry is used to try a failed api contact
        spotify = tekore.RefreshingCredentials(client_id=self.client_id, client_secret=self.client_secret, redirect_uri=self.redirect_uri)
        if(self.current_user.refresh_token):
            new_access_token = spotify.refresh_user_token(self.current_user.refresh_token)
            self.current_user.token = new_access_token.access_token
            self.current_user.refresh_token = new_access_token.refresh_token
            self.current_user.save()
            if(retry):
                try:
                    self.contact_api()
                except Exception as e:
                    print(e)
        else:
            return -1  

    def change_volume(self,amount):
        self.spotify.playback_volume(amount)

    def next(self):
        self.spotify.playback_next()

    def shuffle(self):
        self.spotify.playback_shuffle()

    def prev(self):
        self.spotify.playback_previous()

    def pause(self):
        self.spotify.playback_pause()

    def play(self):
        self.spotify.playback_resume()

    
        


class RedditApi(Api):
    def __init__(self, user_id, api_name="reddit"):
        super().__init__(user_id, api_name, RedditAPIInfo)
        self.current_user = Reddit_User_Info.objects.get(user_id=user_id)
        self.token = self.current_user.token
        self.refresh_token = self.current_user.refresh_token
        self.reddit = praw.Reddit(client_id=self.client_id, client_secret=self.client_secret, redirect_uri=self.redirect_uri, user_agent="techstart")
        
    def init_contact(self):
        """Initializes contact with the API

        Examples
        --------
        ### Creating a user in django shell and initializing API
        ```
        import random
        import string
        from integrations.models import *
        from django.contrib.auth.models import User

        # Create user
        ran_name = lambda n: ''.join([random.choice(string.ascii_lowercase) for i in range(n)])
        user=User.objects.create_user(ran_name(random.randint(0, 10)), password='bar')
        user.save()

        # Add user to Reddit_User_Info table
        entry = Reddit_User_Info(user_id=user.id, account_name="yeet")
        entry.save()
        user.reddit_user_info_set.add(entry)
        user.save()

        # Initialize and access the reddit api
        red = RedditApi(user.id)
        reddit, reddit_user = red.init_contact()
        """
        auth_url = self.reddit.auth.url(["*"], "permanent")
        webbrowser.open(auth_url)
        
    def obtain_token(self, code):
        refresh_token =  self.reddit.auth.authorize(code)
        self.current_user.refresh_token = refresh_token
        self.current_user.save()
        print(f"reddit Token set: {refresh_token}")
    
    def contact_api(self):
        """Contacts the API and gets the user data

        References
        ----------
        - 

        Returns
        -------
        dict
            A dictionary with 7 keys:
                1. 'all_unread'; a ListingGenerator that has unread mentions, replies and messages
                2. 'mentions'; a ListingGenerator that has unread mentions
                3. 'messages'; a ListingGenerator that has unread messages
                4. 'replies'; a ListingGenerator that has unread replies
                5. 'top_day'; a ListingGenerator that has top posts of the last day
                6. 'top_week'; a ListingGenerator that has top posts of the last week
                7. 'top_year'; a ListingGenerator that has top posts of the last year

        Examples
        --------
        ### Creating a user in django shell and initializing API
        ```
        import random
        import string
        from integrations.models import *
        from django.contrib.auth.models import User

        # Create user
        ran_name = lambda n: ''.join([random.choice(string.ascii_lowercase) for i in range(n)])
        user=User.objects.create_user(ran_name(random.randint(0, 10)), password='bar')
        user.save()

        # Add user to Reddit_User_Info table
        entry = Reddit_User_Info(user_id=user.id, account_name="yeet")
        entry.save()
        user.reddit_user_info_set.add(entry)
        user.save()

        # Initialize and access the reddit api
        red = RedditApi(user.id)
        reddit, reddit_user = red.init_contact()
        ... # need to wait to paste url and finalize initialization 
        
        # Contact API to get data
        user_data = red.contact_api(reddit, reddit_user)

        """
        data = {}
        refresh_file = "./reddit_refresh.txt"
        try:
            refresh_token = self.current_user.refresh_token
            with open(refresh_file, "w") as fp:
                fp.write(refresh_token)
            refresh_token_manager = FileTokenManager(refresh_file)
            reddit = praw.Reddit(client_id=self.client_id, client_secret=self.client_secret, token_manager=refresh_token_manager, user_agent="techstart")  
            user = reddit.user.me()
            data["messages"] = reddit.inbox.messages(limit=5)
            data["replies"] = reddit.inbox.comment_replies()
            data["mentions"] = reddit.inbox.mentions(limit=25)
            data["all_unread"] = reddit.inbox.unread(limit=None)
            data["top_day"] =user.top("day")
            data["top_week"] =user.top("week")
            data["top_year"] =user.top("year")
            with open(refresh_file, "r") as fp:
                refresh = fp.readline()
                print(f"old token {self.current_user.refresh_token}")
                if (str(refresh) != refresh_token): #if token has changed 
                    self.current_user.refresh_token = refresh
                    self.current_user.save()
                print(f"new token {self.current_user.refresh_token}")

        except Exception as e:
            print(e)
            pass
        finally:
            if os.path.isfile(refresh_file):
                os.remove(refresh_file)
        return data


    def get_new_token(self): #hanlded in contact_api as praw annoyingly loves to self refresh tokens
        pass 


class DiscordApi(Api):
    def __init__(self, user_id, api_name="discord"):
        super().__init__(user_id, api_name, DiscordAPIInfo)
        self.current_user = Discord_User_Info.objects.get(user_id=user_id)
        self.token = self.current_user.token #set to blank in parent class. Has to be set here
        self.refresh_token = self.current_user.refresh_token #set to blank in parent class. Has to be set here

    def init_contact(self):
        auth_url = self.base_url
        webbrowser.open(auth_url)
        # code = local_code_flow()
        # token_json = self.obtain_token(code) 
        # self.token = token_json["access_token"]
        # self.refresh_token = token_json["refresh_token"]
        # self.current_user.token = token_json["access_token"]
        # self.current_user.refresh_token = token_json["refresh_token"]
        # self.current_user.save()

    def obtain_token(self,code):
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'scope': self.scope
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.post(self.token_endpoint, data=data, headers=headers)
        r.raise_for_status()
        print(json.dumps(r.json()))
        return r.json()

    def contact_api():
        pass
        #Kieran

    def get_new_token(self):
        data = {
        'client_id': self.client_id,
        'client_secret': self.client_secret,
        'grant_type': 'refresh_token',
        'refresh_token': self.refresh_token
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.post(self.token_endpoint, data=data, headers=headers)
        r.raise_for_status()
        response = r.json()
        self.current_user.token = response['access_token']
        self.current_user.refresh_token = response['refresh_token']
        self.current_user.save()

        

class OutlookApi(Api):
    def __init__(self, user_id, api_name="outlook"):
        super().__init__(user_id, api_name, OutlookAPIInfo)
        try:
            self.current_user = Outlook_User_Info.objects.get(user_id=user_id)
            self.token = self.current_user.token #set to blank in parent class. Has to be set here
            self.refresh_token = self.current_user.refresh_token #set to blank in parent class. Has to be set here
        except Exception as e:
            print("Exception: {e}")
    
    def init_contact(self):
        auth_url = self.base_url
        webbrowser.open(auth_url)
            
    def obtain_token(self, code):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        payload = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "scope": self.scope,
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_secret": self.client_secret  
        }
        r = requests.post(self.token_endpoint, headers=headers, data=payload)
        token_response  =  r.json()
        print(r.json())
        self.current_user.token = token_response['access_token']
        self.current_user.refresh_token = token_response['refresh_token']
        self.current_user.save()
        self.token = token_response['access_token']
        print(f"outlook oken set: {self.token}")

    def contact_api(self):
        """Contacts the API and gets the user data

        References
        ----------
        - Message objects: https://pyoutlook.readthedocs.io/en/latest/pyOutlook.html#message

        Returns
        -------
        dict
            A dictionary with 1 key:
                1. 'inbox'; a list of Message objects

        Examples
        --------
        ### Creating a user in django shell and initializing API
        ```
        import random
        import string
        from integrations.models import *
        from django.contrib.auth.models import User

        # Create user
        ran_name = lambda n: ''.join([random.choice(string.ascii_lowercase) for i in range(n)])
        user=User.objects.create_user(ran_name(random.randint(0, 10)), password='bar')
        user.save()

        # Add user to Outlook_User_Info table
        entry = Outlook_User_Info(user_id=user.id, account_name="yeet")
        entry.save()
        user.outlook_user_info_set.add(entry)
        user.save()

        # Initialize and access the reddit api
        outlook_User = OutlookApi(user.id)
        outlook_User.init_contact()
        ... # need to wait to paste url and finalize initialization 
        
        # Contact API to get data
        user_data = outlook_User.contact_api()

        """
        data = {}
        acc = OutlookAccount(self.token)
        data["inbox"] = acc.inbox()
        print(data)
        return data

    def get_new_token(self, retry):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "scope": self.scope,
            "refresh_token": self.refresh_token,
            "redirect_uri": self.redirect_uri,
            "client_secret": self.client_secret  
        }
        r = requests.post(self.token_endpoint, headers=headers, data=payload)
        response = r.json()
        if ('access_token' in response):
            self.current_user.token = response['access_token']
            self.current_user.refresh_token = response['refresh_token']
            self.current_user.save()
        else:
            print("could not retrieve new token")
    
        if(retry):
            self.contact_api()


class NewsApi(Api):
    news_endpoint = "https://newsapi.org/v2/everything"
    apiKey = "cce67af05ae04866ad9820f0edbdf363"
    def __init__(self, user_id, api_name="newsapi"):
        super().__init__(user_id, api_name, NewsApiInfo)
        self.current_user = News_User_Info.objects.get(user_id=user_id)

    def get_user_articles(self,article):
        now = datetime.now()
        day_past = now - timedelta(hours = 24)
        now = now.isoformat()
        day_past = day_past.isoformat()
        params = {
            'q': article,
            'from': str(day_past),
            'to': str(now),
            'sortBy': 'popularity',
            'apiKey': self.apiKey 
        }

        r = requests.get(self.news_endpoint, params=params)
        result = r.json()
        if (result['status'] == 'ok'):
            return result
        else:
            return ""

    def contact_api(self):
        preferences = self.current_user.preferences.split("  ")
        urls = {}
        for pref in preferences:
            result = self.get_user_articles(pref)
            articles = result.get('articles')
            for article in articles:
                if pref in urls:
                    urls[pref].append(article['url'])
                else:
                     urls[pref] = [article['url']]
        print(urls)
        return urls #returns dict of form {preference: url}

    def search_news(self, keywords, sources):
        now = datetime.now()
        day_past = now - timedelta(hours = 24)
        params = {
            'q': urllib.parse.urlencode(keywords),
            'from': now,
            'to': day_past,
            'sortBy': 'popularity',
            'apiKey': self.apiKey,
            'sources': sources, #comma separated
        }
        r = requests.get(self.news_endpoint, params=params)
        result = r.json()
        if result['status'] == 'ok':
            return result
        else:
            return "search couldn't be performed as specified"

        


    def add_prefs(self,str): #this should be moved to a form
        if (self.current_user.preferences):
            self.current_user.preferences = self.current_user.preferences + "  " + str.strip()
        else:
             self.current_user.preferences = str.strip()
        self.current_user.save()


class SpotifyAPIInfo(ApiInfo):
    """The spotify specific ApiInfo subclass"""
    def __init__(self):
        self.api_name = "spotify"
        self.client_id = "eab08f62731b44c4a49010295cd3776f"
        self.secret = "5e4dcc7236ba4cc4b38ca3dbc7f03217" #TODO: make env variable
        self.base_url = "https://accounts.spotify.com/authorize"
        self.token_endpoint = "https://login.microsoftonline.com/consumer/oauth2/v2.0/token"
        self.redirect_url = "http://127.0.0.1:8000/api/redirect"
        self.scope = "user-top-read user-read-recently-played user-read-playback-position user-read-playback-state user-library-read user-modify-playback-state user-read-currently-playing app-remote-control streaming"


class RedditAPIInfo(ApiInfo):
    """The reddit specific ApiInfo subclass"""
    def __init__(self):
        self.api_name = "reddit"
        self.client_id = "RouUl0Nxn9pysw"
        self.secret = "4-KNQ9Z9SsKRvpJzVMs2TGP9V2u-hA" #TODO: make env variable
        self.base_url = "https://www.reddit.com/api/v1/authorize"
        self.token_endpoint = "https://www.reddit.com/api/v1/access_token"
        self.redirect_url = "http://127.0.0.1:8000/api/redirect"
        self.scope = {} #TODO: 
        # self.scope 

        
class DiscordAPIInfo(ApiInfo):
    """The discord specific ApiInfo subclass"""
    def __init__(self):
        self.api_name = "discord"
        self.client_id = '829140725307932733'
        self.secret = "FNAo1rbbdhLD9pda2SyaIdRl2wC2_ATn" #TODO: 
        self.base_url = 'https://discord.com/api/oauth2/authorize?client_id=829140725307932733&redirect_uri=http%3A%2F%2F127.0.0.1%3A8000%2Fapi%2Fredirect&response_type=code&scope=email%20connections%20rpc%20rpc.notifications.read%20rpc.activities.write%20messages.read'
        self.token_endpoint = 'https://discord.com/api/oauth2/token'
        self.redirect_url = 'http://127.0.0.1:8000/api/redirect'
        self.scope = 'email connections rpc rpc.notifications.read rpc.activities.write messages.read'
        # self.scope 

class OutlookAPIInfo(ApiInfo):
    """The outlook specific ApiInfo subclass"""
    def __init__(self):
        self.api_name = "outlook"
        self.client_id = "9bb0ebfa-b59b-4717-af05-506e0188c0bb"
        self.secret = "w.0ywb5.VL3VxQ~cCkEs~G6p-c8i_~-Q9~" 
        self.base_url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize?client_id=9bb0ebfa-b59b-4717-af05-506e0188c0bb&response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fapi%2Fredirect&response_mode=query&scope=https://graph.microsoft.com/.default"
        self.token_endpoint = 'https://login.microsoftonline.com/consumers/oauth2/v2.0/token'
        self.redirect_url = 'http://localhost:8000/api/redirect' 
        self.scope = "https://outlook.office.com/mail.send https://outlook.office.com/mail.readwrite offline_access"
        # self.scope 

class NewsApiInfo(ApiInfo):
    def __init___(self):
        self.api_name = "newsapi"
        self.secret = "N/A"
        self.client_id = "N/A"
        self.base_url = "N/A"
        self.token_endpoint = "N/A""N/A"
        self.redirect_url = "N/A"
        self.scope = "N/A"
        # self.scope 