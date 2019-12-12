from django.urls import path
from django.conf.urls import url

from . import views
from django.views.generic.base import TemplateView
from django.contrib.auth import views as v

urlpatterns = [
    url(r'login', views.login, name='login'),
    url(r'logout', views.logout, name='logout'),
    url(r'password_reset', views.password_reset, name='password_reset')
]