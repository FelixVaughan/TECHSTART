from praw.reddit import Reddit
from integrations.views import authenticate_spotify
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm
from integrations.models import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.http import *
# Create your views here.


@login_required
def index(request):
    """Renders the homepage"""
    news = NewsApi(request.user.id)
    prefs = news.get_prefs()
    return render(request, "users/index.html", {'prefs': prefs})


def ajax(request):
    user_info = {}
    if request.GET.get('social') == 'spotify_init':
        spot = SpotifyApi(request.user.id)
        spot.init_contact()
    if request.GET.get('social') == 'spotify_top':
        spot = SpotifyApi(request.user.id)
        user_info = spot.contact_api()
        return render(request, 'users/ajax.html', {'user_info': user_info})
    return HttpResponse('')

def reddit_data(request):
    print("OOOOOOPH")
    if request.GET.get('state') != 'redditData':
        red = RedditApi(request.user.id)
        red.init_contact()
        user_data = red.contact_api()
        messages = [[message.body_html, message.subject, message.author] for message in user_data["messages"]]
        top_year = [
            [post.body_html, post.subject, post.author] for post in user_data["top_year"]]
        unread = [
            [message.body_html, message.subject, message.author] for message in user_data["all_unread"]]
        return render(request, "users/reddit_data.html", {'messages': messages,'top_year': top_year, 'unread':unread })
    return HttpResponse('')

def song(request):
    user_info = {}
    if request.GET.get('state') == 'spotify_play':
        spot = SpotifyApi(request.user.id)
        user_info = spot.play()
        return render(request, 'users/song.html', {'user_info': user_info})
    if request.GET.get('state') == 'spotify_pause':
        spot = SpotifyApi(request.user.id)
        user_info = spot.pause()
        return render(request, 'users/song.html', {'user_info': user_info})
    if request.GET.get('state') == 'spotify_shuffle':
        spot = SpotifyApi(request.user.id)
        user_info = spot.shuffle()
        return render(request, 'users/song.html', {'user_info': user_info})
    if request.GET.get('state') == 'spotify_next':
        spot = SpotifyApi(request.user.id)
        user_info = spot.next()
        return render(request, 'users/song.html', {'user_info': user_info})
    if request.GET.get('state') == 'spotify_prev':
        spot = SpotifyApi(request.user.id)
        user_info = spot.prev()
        return render(request, 'users/song.html', {'user_info': user_info})
    if request.GET.get('volume') :
        volume = int(request.GET.get('volume'))  # ?state=spotify_volume&volume=
        print("volume is ", volume)
        spot = SpotifyApi(request.user.id)
        spot.change_volume(volume)
        return render(request, 'users/song.html')
    return HttpResponse('')
# renders articles page


def article_overview(request):
    user_info = {}
    if request.method == "POST":
        searched = request.POST['searched']
        news = NewsApi(request.user.id)
        if searched not in news.get_prefs():
            news.add_prefs(searched)
        user_info = news.contact_api()
        print(news.get_prefs())
        if(searched not in user_info):
            print(news.get_prefs())
            return HttpResponse('Error: no results found.')
        else:
            articles = user_info[searched]
            return render(request, 'users/article.html', {'searched':searched,'articles': articles})
    else:
        return render(request, 'users/article.html', {})

# renders register page


def register(request):
    if request.method == "POST":    # if form is submitted
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Sign Up successful for {username}')
            return redirect('login')
    else:
        form = UserRegistrationForm()  # else use form
    # pass form as context
    return render(request, 'users/register.html', {'form': form})
