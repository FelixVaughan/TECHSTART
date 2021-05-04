from integrations.views import authenticate_spotify
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm
from integrations.models import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.http import *
# Create your views here.


def index(request):
    """Renders the homepage"""
    return render(request, "users/index.html")

# @login_required


def ajax(request):
    user_info = {}
    if request.GET.get('social') == 'spotify_init':
        spot = SpotifyApi(request.user.id)
    if request.GET.get('social') == 'spotify_top':
        spot = SpotifyApi(request.user.id)
        return render(request, 'users/ajax.html', {'user_info': user_info})
    if request.GET.get('social') == 'spotify_play':
        spot = SpotifyApi(request.user.id)
        x = spot.play()
        print(x)
    if request.GET.get('social') == 'spotify_pause':
        spot = SpotifyApi(request.user.id)
        spot.pause()
    if request.GET.get('social') == 'spotify_shuffle':
        spot = SpotifyApi(request.user.id)
        spot.shuffle()
    if request.GET.get('social') == 'spotify_next':
        spot = SpotifyApi(request.user.id)
        spot.next()
    if request.GET.get('social') == 'spotify_prev':
        spot = SpotifyApi(request.user.id)
        spot.prev()

    if request.GET.get("social") == 'redditData':
        red = RedditApi(request.user.id)
        red.init_contact()
        user_data = red.contact_api()

        
        user_data["messages"] = [message.body for message in user_data["message"]]
        user_data["top_year"] = [
            message.body for message in user_data["top_year"]]
        user_data["all_unread"] = [
            message.body for message in user_data["all_unread"]]
        return render(request, "users/reddit_data.html", {'user_data': user_data})
    return HttpResponse('')

# renders articles page

def article_overview(request):
    user_info = {}
    if request.method == "POST":
        searched = request.POST['searched']
        news = NewsApi(request.user.id)
        if searched in news.get_prefs():
            user_info = news.contact_api()
            print(news.get_prefs())
        else:
            news.add_prefs(searched)
            user_info = news.contact_api()
            print(news.get_prefs())
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
