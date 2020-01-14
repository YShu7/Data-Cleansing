from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('signup', views.signup, name='signup'),
    path('add_user', views.add_user, name='add_user'),
    path('password_change', views.password_change, name='password_change'),
    path('password_forget', views.CustomPasswordResetView.as_view(), name='password_forget'),
]