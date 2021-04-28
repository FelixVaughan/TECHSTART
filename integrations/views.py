from django.shortcuts import render
from django.contrib.sessions.models import Session
from django.http import *
from tempfile import NamedTemporaryFile
from integrations.models import *
import errno
import os
import tekore
import praw  
import traceback
import requests

def obtain_url_code(url):
    print(f"code request {url}")
    try:
        index = url.index("code=") 
        amp_separator = url.find("&", index) 
        code = ""
        if (amp_separator != -1):
            code = url[index+5:amp_separator]
        else:
            code = url[index+5:len(url)-3]
        return code
    except Exception as e:
        print(f"could not find code in string {str(url)}")
        return -1


######################################################################
#Authenication Methods used for applications that reqire user consent# 
######################################################################
def authenticate_spotify(request):
    request.session['api'] = 'spotify'
    spot = SpotifyApi(request.user.id)
    spot.init_contact()
    return HttpResponse('')

def authenticate_reddit(request):
    request.session['api'] = 'reddit'
    reddit = RedditApi(request.user.id)
    reddit.init_contact()
    return HttpResponse('')

def authenticate_outlook(request):
    request.session['api'] = 'outlook'
    outlook = OutlookApi(request.user.id)
    outlook.init_contact()
    return HttpResponse('')

######################################################################
#                                End                                 # 
######################################################################


######################################################################
#          Methods used for apis that reqire user output             # 
######################################################################
def play_spotify(request):
    data = None 
    if request.method == 'POST':
        form = UserForm(request.POST or None)
        if form.is_valid():
            data =  form.cleaned_data.get("data")
            data = str(data)
    if (data):
        pass
    return HttpResponse('')

def change_spotify_volume(request):
    #FRONT END : 30 IS JUST A PLACE HOLDER. EXTRACT VALUE FROM FORM AND USE IT AS INPUT PARAMTER FOR CHANGE_VOLUME
    spotify = SpotifyApi(request.user.id)
    spotify.change_volume(30)
    return HttpResponse('')



######################################################################
#                                End                                 # 
######################################################################


def redirect(request):
    try:
        url = str(request.build_absolute_uri)
        code = obtain_url_code(url)
        token_recv = False
        user = request.user
        oauth_session = request.session['api']
        if(code is -1):
            msg = "Code not found in redirect Url. Probably malformed..."
        if oauth_session == 'reddit':
            red = RedditApi(user.id)
            red.obtain_token(code)
            token_recv = True
        elif oauth_session == 'spotify':
            spotify = SpotifyApi(user.id)
            spotify.obtain_token(code)
            token_recv = True
        elif oauth_session == 'outlook':
            outlook = OutlookApi(user.id)
            outlook.obtain_token(code)
            token_recv = True

        if(token_recv):
            print(f"Token Obtained for {request.session['api']} api under user {user}!")
        else:
             print(f"Expected response from {request.session['api']} token set: {token_recv}")
        # url = str(request.build_absolute_uri)
        # code = obtain_url_code(url)
        # if(code is -1):
        #     msg = "Code not set as it was not found in redirect. Url probably malformed..."
        #     print(msg)
        #     return(msg)
        # if os.path.exists("code.txt"):
        #     os.remove("code.txt")
        # if (request.session['api'] == 'discord'):
        #     print(f"CODE IS: {code}")
        # f = open("code.txt","w")
        # f.write(code)
        # f.close()
    except Exception as e:
        print(e) 
    finally:
        return render(request, 'users/redirect.html')

def index(request):
    userinfo = {'current_user': 'bingo',
                'top_tracks': 'Some Music',
                'top_artists': 'Celine Dion'}
    return render(request, 'integrations/index.html', {'userinfo':userinfo})
