from django.conf import settings
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('login', views.CustomLoginView.as_view(), name='login'),
    path('logout', auth_views.LogoutView.as_view(), {'next_page': settings.LOGOUT_REDIRECT_URL}, name='logout'),
    path('signup', views.signup, name='signup'),
    path('password_change', views.password_change, name='password_change'),
    path('password_reset', views.CustomPasswordResetView.as_view(),
         name='password_reset'),
    path('password_reset_done', auth_views.PasswordResetDoneView.as_view(
        template_name="authentication/password_reset_done.html"
    ), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password_reset_complete', auth_views.PasswordResetCompleteView.as_view(
        template_name="authentication/password_reset_complete.html"
    ), name='password_reset_complete'),
]
