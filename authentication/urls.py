from django.conf.urls import url
from . import views

urlpatterns = [
    url('login', views.login, name='login'),
    url('logout', views.logout, name='logout'),
    url('password_change', views.password_change, name='password_change'),
    url('password_forget', views.CustomPasswordResetView.as_view(), name='password_forget')
]