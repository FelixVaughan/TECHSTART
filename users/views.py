from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm
from integrations.models import *
# Create your views here.
def index(request):
    """Renders the homepage"""
    spot = SpotifyApi(1)
    user_info = spot.contact_api()
    return render(request, "users/index.html", {'user_info': user_info})


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