from requests_oauthlib import OAuth2Session
import webbrowser
from users.models import User
from integration.models import Account
#Abstract class for APIS that we will implement 
#by subclassing this class. These classes can further be modified
#by modifying, adding and overriding methods.

class Api:
    def __init__(self,user_id,api_name):
        self.user = user_id
        self.name = api_name
        self.token = Account.objects.get(user_id=user_id).token
        self.refresh_token = Account.objects.get(user_id=user_id).refresh_token
        self.redirect_uri = Account.objects.get(user_id=user_id).redirect_uri

    def init_contact():             #used when the user has never authenticated withan api before
        pass
        # basic subclass implementation should be as follows
        # redirect_url = "www.redirecturl.com"
        # client_id = "clientidissuedbyregisteringapp"
        # client_secret = "clientsecretissuedbyregisteringapp"
        # base_url = "www.authoriationpoint.com"
        # token_endpoint = "www.tokenendpoint.com"
        # scope = ["scope1","scope2"]
        # api = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_url)
        # auth_url, state = api.authorization_url(base_url)
        # webbrowser.open(auth_url)
        # response = input("please enter in the url redirected to: ")
        # token = reddit.fetch_token(token_endpoint, client_secret=client_secret, authorization_response=response)
        

    def contact_api(): #method to be called by threadpool 
        pass

    def get_new_token(): #uses refresh_token to get a new key
        pass