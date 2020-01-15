from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from . import views

urlpatterns = [
    path('login', views.CustomLoginView.as_view(), name='login'),
    path('logout', auth_views.LogoutView.as_view(), {'next_page': settings.LOGOUT_REDIRECT_URL}, name='logout'),
    path('signup', views.signup, name='signup'),
    path('add_user', views.add_user, name='add_user'),
    path('password_change', views.password_change, name='password_change'),
    path('password_forget', views.CustomPasswordResetView.as_view(), name='password_forget'),
]