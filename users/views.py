from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm
from integrations.models import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

# Create your views here.
def index(request):
    """Renders the homepage"""
    return render(request, "users/index.html")

#@login_required
def ajax(request):
    user_info = {}
    if request.GET.get('social') == 'spotify_init':
        spot = SpotifyApi(request.user.id)
        spot.init_contact()
    if request.GET.get('social') == 'spotify_top':
        spot = SpotifyApi(request.user.id)
        user_info = spot.contact_api()
        return render(request, 'users/ajax.html', {'user_info':user_info})
    if request.GET.get('social') == 'spotify_play':
        spot = SpotifyApi(request.user.id)
        user_info = spot.play() #Need the right return type for the play function
    return render(request, 'users/ajax.html', {'user_info':user_info})

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
        form = UserRegistrationForm() # else use form
    return render(request, 'users/register.html', {'form':form}) # pass form as context