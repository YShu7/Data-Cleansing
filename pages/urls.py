from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='tasks'),
    path('tasks', views.index, name='tasks'),
    path('profile', views.profile, name='profile'),
    path('validate', views.validate, name='validate'),
    path('<int:question_id>/vote', views.vote, name='vote'),
    path('user', views.index, name='user'),
    path('add_user', views.add_user, name='add_user'),
    path('dataset', views.dataset, name='dataset'),
    path('report', views.report, name='report'),
    path('log', views.log, name='log'),
]