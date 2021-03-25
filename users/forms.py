from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

#create user registration form
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()  # add email field to UserCreationForm

    class Meta:
        model = User    # save form to inbuilt User model
        fields = ['username', 'email', 'password1', 'password2'] # fields in the form

