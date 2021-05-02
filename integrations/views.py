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
from django.views.decorators.cache import cache_page


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
    spotify = SpotifyApi(request.user.id)
    spotify.play()
    return HttpResponse('')

def change_spotify_volume(request):
    #FRONT END : 30 IS JUST A PLACE HOLDER. EXTRACT VALUE FROM FORM AND USE IT AS INPUT PARAMTER FOR CHANGE_VOLUME
    spotify = SpotifyApi(request.user.id)
    spotify.change_volume(30)
    return HttpResponse('')

def shuffle(request):
    spotify = SpotifyApi(request.user.id)
    spotify.shuffle()
    return HttpResponse('')
    
def play_next(request):
    spotify = SpotifyApi(request.user.id)
    spotify.next()
    return HttpResponse('')

def play_prev(request):
    spotify = SpotifyApi(request.user.id)
    spotify.prev()
    return HttpResponse('')

def pause_play(request):
    spotify = SpotifyApi(request.user.id)
    spotify.pause()
    return HttpResponse('')

def play_album(request):
    temp = SpotifyApi(request.user.id)
    spotify = tekore.Spotify(temp.current_user.token)
    albums = spotify.saved_albums(limit=15).items
    a = 0
    print("your albums are:")
    for album in albums:
        print("{a}. {album.album.name}")

    ########implement front end choice to choose which album#########

    alb = tekore.to_uri('album', albums[0].album.id) #is zero rn but should be changed to index chosen by user
    spotify.playback_start_context(alb)



######################################################################
#                                End                                 # 
######################################################################

    # headers = {
    #     'Authorization': f'Bearer {self.token}',
    #     'Accept': 'application/json',
    #     'Content-Type': 'application/json'
    # }
    # dir = "next"
    # if(prev):
    #     dir = "previous"
    # requests.post("https://api.spotify.com/v1/me/player/{dir}", headers=headers, params=params)

def pause(request):
    spotify = SpotifyApi(request.user.id)
    spotify.pause()
    return HttpResponse('')

    # headers = {
    #     'Authorization': f'Bearer {self.token}',
    #     'Accept': 'application/json',
    #     'Content-Type': 'application/json'
    # }
    # requests.put("https://api.spotify.com/v1/me/player/pause")

def play(request):
    spotify = SpotifyApi(request.user.id)
    spotify.play()
    return HttpResponse('')
    # headers = {
    #     'Authorization': f'Bearer {self.token}',
    #     'Accept': 'application/json',
    #     'Content-Type': 'application/json'
    # }
    # requests.put("https://api.spotify.com/v1/me/player/play")



######################################################################
#                                End                                 # 
######################################################################

def test(request):
    print("API IS: {request.session['api']}")
    
def redirect(request):
    print(f"AUTHENTICATION IN PROGRESS FOR {request.session['api']}")
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
        elif oauth_session == 'outlook':
            outlook = OutlookApi(user.id)
            outlook.obtain_token(code)
            token_recv = True
        elif oauth_session == 'spotify':
            spotify = SpotifyApi(user.id)
            spotify.obtain_token(code)
            token_recv = True
        

        if(token_recv):
            print(f"Token Obtained for {request.session['api']} api under user {user}!")
        else:
             print(f"Expected response from {request.session['api']} token set: {token_recv}")
    except Exception as e:
        print(e) 
    finally:
        return render(request, 'users/redirect.html')

def index(request):
    userinfo = {'current_user': 'bingo',
                'top_tracks': 'Some Music',
                'top_artists': 'Celine Dion'}
    return render(request, 'integrations/index.html', {'userinfo':userinfo})
