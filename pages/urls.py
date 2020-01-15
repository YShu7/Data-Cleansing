from django.urls import path

from pages.views import views, admin

urlpatterns = [
    path('', views.index, name='tasks'),
    path('tasks', views.index, name='tasks'),
    path('profile', views.profile, name='profile'),
    path('validate', views.validate, name='validate'),
    path('<int:question_id>/vote', views.vote, name='vote'),
    path('admin', admin.index, name='admin'),
    path('modify_users', admin.modify_users, name='modify_users'),
    path('dataset', admin.dataset, name='dataset'),
    path('download_dataset', admin.download_dataset, name='download_dataset'),
    path('download_report', admin.download_report, name='download_report'),
    path('<int:question_id>/update', admin.update, name='update'),
    path('report', admin.report, name='report'),
    path('log', admin.log, name='log'),
    path('assign_tasks', admin.assign_tasks, name='assign_tasks'),
    path('summarize', admin.summarize, name='summarize'),
]