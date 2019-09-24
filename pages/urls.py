from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('tasks', views.TasksView.as_view(), name='tasks'),
]