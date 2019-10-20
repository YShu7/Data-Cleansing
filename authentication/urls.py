from django.urls import path

from . import views
from django.views.generic.base import TemplateView
from django.contrib.auth import views as v

urlpatterns = [
    path('login', views.login, name='login'),
    path('logout', views.login, name='logout')
]