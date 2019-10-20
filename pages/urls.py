from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='tasks'),
    path('tasks', views.index, name='tasks'),
    path('profile', views.profile, name='profile'),
    path('validate', views.validate, name='validate'),
    path('<int:question_id>/vote', views.vote, name='vote'),
]