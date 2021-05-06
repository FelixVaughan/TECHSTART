from django.urls import path
from django.conf.urls import url
# import auth.views for login and logout
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    url(r"^$", views.index, name="index"),  # site hompage
    path('ajax/', views.ajax, name='ajax'),
    path('reddit/', views.reddit_data, name="reddit"),
    path('song/', views.song, name='song'),
    path('article/', views.article_overview, name='article'),
    path('register/', views.register, name='register'),   # register page path
    path('contact/', views.contact_page, name='contact'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'),
         name='login'),  # login page
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'),
         name='logout'),  # logout page
]
