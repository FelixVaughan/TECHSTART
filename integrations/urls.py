from django.urls import path, include
import integrations.views

from . import views
urlpatterns = [
    path('redirect/', views.redirect, name='api-redirect'),
    path("index/", views.index, name='api-index'),
    path("test", views.authenticate_spotify, name="test")
]