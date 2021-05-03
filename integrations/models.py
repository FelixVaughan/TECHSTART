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

###########################
newFile = open("integrations/ApiInfo.txt", "r")
apiArr = []   
while(True):
    line = newFile.readline()
    if not line:
        break
    apiArr.append(line.rstrip("\n"))
for i in range(len(apiArr)):
    apiArr[i] = bytes.fromhex(apiArr[i]).decode()
##############################


def local_code_flow():
    waittime = 0
    code = ""
    try:
        while not os.path.isfile("./code.txt"):
            sleep(0.1)
            waittime += 1  # 10 == 1sec
            if (waittime == 350):  # 35 seconds
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
    # spotify, facebook, etc. Set by default in subclass implementation constructors
    account_name = models.CharField(max_length=20)
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
    api_endpoint = models.CharField(
        max_length=2083, blank=False, default="N/A")  # undeeded
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
        api = OAuth2Session(self.client_id, scope=self.scope,
                            redirect_uri=self.redirect_uri)
        auth_url, state = api.authorization_url(self.base_url)
        webbrowser.open(auth_url)
        response = input("Paste URL redirected to: ")
        token = api.fetch_token(
            self.token_endpoint, client_secret=self.client_secret, authorization_response=response)
        user = User.objects.get(user_id=self.user_id)
        user_account_table = Spotify_User_Info.objects.create(
            user_id=self.user_id)
        user_account_table.users.add(user)
        self.populate_user_table(user_account_table, token)

    # Whole method could probably be implemented in a more efficient manner with a for loop but we'd need a way to access all field attributes.
    # should take in a model that is a child of User_Account_Info
    def populate_user_table(self, user_table_ref, given_dict):
        # Whole method could probably be implemented in a more efficient manner with a for loop but we'd need a way to access all field attributes.
        # should take in a model that is a child of User_Account_Info
        print(f"Populated {user_table_ref.account_name} table with row data: ")
        if "access_token" in given_dict.keys():
            user_table_ref.token = given_dict['access_token']
            #print(f"token: {user_table_ref.token}")
        if "refresh_token" in given_dict.keys():
            user_table_ref.refresh_token = given_dict['refresh_token']
            #print(f"refresh token: {user_table_ref.refresh_token}")
        if "token_type" in given_dict.keys():
            user_table_ref.token_type = given_dict['token_type']
           # print(f"token type: {user_table_ref.token_type}")
        if "expires_in" in given_dict.keys():
            user_table_ref.expires_in = given_dict['expires_in']
            #print(f"expires in: {user_table_ref.expires_in}")
        if "expires_at" in given_dict.keys():
            user_table_ref.expires_in = given_dict['expires_at']
            #print(f"expires at: {user_table_ref.expires_at}")
        user_table_ref.save()

    def contact_api(self):  # method to be called by threadpool
        pass

    def get_new_token(self):  # uses refresh_token to get a new key
        pass

# use boolean connected to check if user has linked their social account.


class Spotify_User_Info(User_Account_Info):
    account_name = models.CharField(
        max_length=7, default="spotify", editable=False)
    users = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    connected = models.BooleanField(default=False)

    # returns username to identify the object in table
    def __str__(self):
        return self.users.username


class Reddit_User_Info(User_Account_Info):
    account_name = models.CharField(
        max_length=6, default="reddit", editable=False)
    users = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    connected = models.BooleanField(default=False)

    def __str__(self):
        return self.users.username


class Discord_User_Info(User_Account_Info):
    account_name = models.CharField(
        max_length=7, default="discord", editable=False)
    users = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    connected = models.BooleanField(default=False)

    def __str__(self):
        return self.users.username


class Outlook_User_Info(User_Account_Info):
    account_name = models.CharField(
        max_length=7, default="outlook", editable=False)
    users = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    connected = models.BooleanField(default=False)

    def __str__(self):
        return self.users.username


class News_User_Info(User_Account_Info):
    account_name = models.CharField(
        max_length=7, default="newsapi", editable=False)
    users = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    preferences = models.CharField(max_length=100, default="")


class SpotifyApi(Api):
    def __init__(self, user_id, api_name="spotify"):
        super().__init__(user_id, api_name, SpotifyAPIInfo)
        self.current_user = Spotify_User_Info.objects.get(users=user_id)
        self.token = self.current_user.token
        self.refresh_token = self.current_user.refresh_token
        self.conf = (self.client_id, self.client_secret, self.redirect_uri)
        self.spotify_auth = tekore.RefreshingCredentials(
            client_id=self.client_id, client_secret=self.client_secret, redirect_uri=self.redirect_uri)
        self.spotify = None
        if(self.current_user.token):
            self.spotify = tekore.Spotify(self.current_user.token)

    def init_contact(self):
        try:
            auth_url = self.spotify_auth.user_authorisation_url(
                scope=self.scope)
            webbrowser.open(auth_url)
        except KeyError:
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

    # will def need parameters in the future
    def contact_api(self, album_uri: str = "") -> dict:
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
            user_values["top_tracks"] = spotify.current_user_top_tracks(
                limit=10)

            if album_uri:
                spotify.playback_start_context(album_uri)

            # Set object attributes
            user_values["top_artist"] = spotify.current_user_top_artists(
                limit=1).items[0]
            # here
            print(user_values)
            return user_values
        except tekore.ServiceUnavailable as err:
            print("It looks like you are currently not logged into spotify...")
        except Exception as e:
            self.get_new_token(True)

    def get_new_token(self, retry):  # retry is used to try a failed api contact
        spotify = tekore.RefreshingCredentials(
            client_id=self.client_id, client_secret=self.client_secret, redirect_uri=self.redirect_uri)
        if(self.current_user.refresh_token):
            new_access_token = spotify.refresh_user_token(
                self.current_user.refresh_token)
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

    def change_volume(self, amount):
        self.spotify.playback_volume(amount)
        self.spotify.playback_currently_playing().item

    def next(self):
        self.spotify.playback_next()
        return self.get_song_info()

    def shuffle(self):
        self.spotify.playback_shuffle()
        return self.get_song_info()

    def prev(self):
        self.spotify.playback_previous()
        return self.spotify.playback_currently_playing().item

    def pause(self):
        self.spotify.playback_pause()
        return self.get_song_info()

    def play(self):
        self.spotify.playback_resume()
        return self.get_song_info()

    def get_song_info(self):
        info = {}
        data = self.spotify.playback_currently_playing().item
        info["id"] = data.id
        info["disc #"] = data.disc_number
        info["name"] = data.name
        info["popularity"] = data.popularity
        info["type"] = data.type
        info["url"] = data.href
        info["track #"] = data.track_number
        info["album_url"] = data.album.href
        info["album_name"] = data.album.name
        info["artists"] = []
        print("ooof")
        for artist in data.artists:
            info["artists"].append(artist.name)
        return info


class RedditApi(Api):
    def __init__(self, user_id, api_name="reddit"):
        super().__init__(user_id, api_name, RedditAPIInfo)
        self.current_user = Reddit_User_Info.objects.get(users=user_id)
        self.token = self.current_user.token
        self.refresh_token = self.current_user.refresh_token
        self.reddit = praw.Reddit(client_id=self.client_id, client_secret=self.client_secret,
                                  redirect_uri=self.redirect_uri, user_agent="techstart")

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
        refresh_token = self.reddit.auth.authorize(code)
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
            reddit = praw.Reddit(client_id=self.client_id, client_secret=self.client_secret,
                                 token_manager=refresh_token_manager, user_agent="techstart")
            user = reddit.user.me()
            data["messages"] = reddit.inbox.messages(limit=5)
            data["replies"] = reddit.inbox.comment_replies()
            data["mentions"] = reddit.inbox.mentions(limit=25)
            data["all_unread"] = reddit.inbox.unread(limit=None)
            data["top_day"] = user.top("day")
            data["top_week"] = user.top("week")
            data["top_year"] = user.top("year")
            with open(refresh_file, "r") as fp:
                refresh = fp.readline()
                print(f"old token {self.current_user.refresh_token}")
                if (str(refresh) != refresh_token):  # if token has changed
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

    # hanlded in contact_api as praw annoyingly loves to self refresh tokens
    def get_new_token(self):
        pass


class DiscordApi(Api):
    def __init__(self, user_id, api_name="discord"):
        super().__init__(user_id, api_name)
        self.user_to_serve = Discord_User_Info.objects.get(user_id=user_id)
        # set to blank in parent class. Has to be set here
        self.token = self.user_to_serve.token
        # set to blank in parent class. Has to be set here
        self.refresh_token = self.user_to_serve.refresh_token

    def init_contact(self):
        selfDirectUri = "http://127.0.0.1:8000/api/redirect?code=osXs6cZSKLd4SaeEXo65Qt3DEz7Bpd"
        webbrowser.open(selfDirectUri)
        super().__init__(user_id, api_name, DiscordAPIInfo)
        self.current_user = Discord_User_Info.objects.get(user_id=user_id)
        # set to blank in parent class. Has to be set here
        self.token = self.current_user.token
        # set to blank in parent class. Has to be set here
        self.refresh_token = self.current_user.refresh_token

    def init_contact(self):
        auth_url = self.base_url
        webbrowser.open(auth_url)

    def obtain_token(self, code):
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
        # Kieran

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
            self.current_user = Outlook_User_Info.objects.get(users=user_id)
            # set to blank in parent class. Has to be set here
            self.token = self.current_user.token
            # set to blank in parent class. Has to be set here
            self.refresh_token = self.current_user.refresh_token
        except Exception as e:
            print(f"Exception: {e}")

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
        token_response = r.json()
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
        - To get the body of a message use ```Message.body```
        - Full list of Message object attributes here: https://github.com/O365/python-o365/blob/master/O365/message.py#L348-L1081

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

# Initialize and access the Outlook api
outlook_User = OutlookApi(user.id)

# Contact API to get data
user_data = outlook_User.contact_api()

        """
        data = {}

        oinfo = OutlookAPIInfo()
        credentials = (oinfo.client_id, oinfo.secret)
        scopes = ['offline_access', 'https://graph.microsoft.com/User.Read',
                  'https://graph.microsoft.com/Mail.ReadWrite', 'https://graph.microsoft.com/Mail.Send']
        account = Account(credentials, scopes=scopes)

        url, state = account.con.get_authorization_url(
            requested_scopes=scopes, redirect_uri=oinfo.redirect_url)

        print(url)

        result = account.con.request_token(
            url, state=state, redirect_uri=oinfo.redirect_url)

        token = account.con.token_backend.token

        if result:
            print("yeet")
        else:
            print("asdflkjhasdlfkjhasldkfgjhasdlkjfhasglkjhjaksdl")
            return

        # account.authenticate(requested_scopes=scopes, redirect_uri = oinfo.redirect_url)

        inbox = account.mailbox().inbox_folder()
        # Pulls first 25 emails from inbox into list
        data["inbox"] = [email for email in inbox.get_messages()]

        data["token"] = token
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
    apiKey = "9fe64c8447a8406d9e8038c3da825c94"

    def __init__(self, user_id, api_name="newsapi"):
        super().__init__(user_id, api_name, NewsApiInfo)
        self.current_user = News_User_Info.objects.get(users=user_id)

    def get_user_articles(self, article):
        now = datetime.now()
        day_past = now - timedelta(hours=24)
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
            print(result)
            return "could not complete request"

    def contact_api(self):
        preferences = self.current_user.preferences.split("  ")
        urls = {}
        for pref in preferences:
            result = self.get_user_articles(pref)
            articles = result['articles']
            for article in articles:
                if pref in urls:
                    urls[pref].append((article['title'], article['url']))
                else:
                    urls[pref] = [(article['title'], article['url'])]
        print(urls)
        return urls  # returns dict of form {preference: url}

    def search_news(self, keywords, sources):
        now = datetime.now()
        day_past = now - timedelta(hours=24)
        params = {
            'q': urllib.parse.quote(keywords),
            'from': now,
            'to': day_past,
            'sortBy': 'popularity',
            'apiKey': self.apiKey,
            'sources': sources,  # comma separated
        }
        r = requests.get(self.news_endpoint, params=params)
        result = r.json()
        urls = {}
        if result['status'] == 'ok':
            articles = result['articles']
            for article in articles:
                if pref in urls:
                    urls[pref].append((article['title'], article['url']))
                else:
                    urls[pref] = [(article['title'], article['url'])]
            return urls
        else:
            return "search couldn't be performed as specified"

    def add_prefs(self, str):  # this should be moved to a form
        if (self.current_user.preferences):
            self.current_user.preferences = self.current_user.preferences + "  " + str.strip()
        else:
            self.current_user.preferences = str.strip()
        self.current_user.save()

    def get_prefs(self):
        if(self.current_user.preferences):
            prefs = self.current_user.preferences.split("  ")
            return prefs
        else:
            return []

    def del_prefs(self, str2del):
        if(self.current_user.preferences):
            preferences = self.current_user.preferences
            try:
                preferences = preferences.replace(str2del,"",1)
                if "    " in preferences:
                    preferences = preferences.replace("    ", "  ",1)
                    preferences = preferences.replace("   ", "  ",1)
                self.current_user.preferences = preferences
                self.current_user.save()
                return self.get_prefs()
            except Exception as e:
                print(f"string parsing exception {e}")




class SpotifyAPIInfo(ApiInfo):
    """The spotify specific ApiInfo subclass"""

    def __init__(self):
        self.api_name = apiArr[0]
        self.client_id = apiArr[1]
        self.secret = apiArr[2] #TODO: make env variable
        self.base_url = apiArr[3]
        self.token_endpoint = apiArr[4]
        self.redirect_url = apiArr[5]
        self.scope = apiArr[6]

class RedditAPIInfo(ApiInfo):
    """The reddit specific ApiInfo subclass"""

    def __init__(self):
        self.api_name = apiArr[7]
        self.client_id = apiArr[8]
        self.secret = apiArr[9] #TODO: make env variable
        self.base_url =apiArr[10]
        self.token_endpoint = apiArr[11]
        self.redirect_url = apiArr[12]
        self.scope = {} #TODO:   #apiArr[13]
        # self.scope 

class DiscordAPIInfo(ApiInfo):
    """The discord specific ApiInfo subclass"""

    def __init__(self):
        self.api_name = apiArr[14]
        self.client_id = apiArr[15]
        self.secret = apiArr[16] #TODO: 
        self.base_url = apiArr[17]
        self.token_endpoint = apiArr[18]
        self.redirect_url = apiArr[19]
        self.scope = apiArr[20]
        # self.scope 

class OutlookAPIInfo(ApiInfo):
    """The outlook specific ApiInfo subclass"""

    def __init__(self):
        self.api_name = apiArr[21]
        self.client_id = apiArr[22]
        self.secret = apiArr[23]
        self.base_url = apiArr[24]
        self.token_endpoint = apiArr[25]
        self.redirect_url = apiArr[26]
        self.scope = apiArr[27]
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


# def del_prefs(self):
#     if(self.current_user.preferences):
#         preferences = self.current_user.preferences
#         try:
#             preferences = preference.replace(str2del,"",1)
#             if "    " in preferences:
#                 preferences = preferences.replace("    ", "  ",1)
#             self.current_user.preferences = preferences
#             self.current_user.save()
#         except Exception as e:
#             print(f"string parsing exception {e}")