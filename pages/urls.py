from django.urls import path

from pages.views import views, user, admin

urlpatterns = [
    path('', views.index, name='tasks'),

    path('user', user.task_list, name='user'),
    path('tasks', user.task_list, name='tasks'),
    path('profile', user.profile, name='profile'),
    path('validate', user.validate, name='validate'),
    path('<int:id>/vote', user.vote, name='vote'),

    path('admin', admin.modify_users, name='admin'),
    path('modify_users', admin.modify_users, name='modify_users'),
    path('dataset', admin.dataset, name='dataset'),
    path('dataset/', admin.dataset, name='dataset'),
    path('dataset/<str:group_name>', admin.dataset, name='dataset'),
    path('download_dataset/<str:group_name>', admin.download_dataset, name='download_dataset'),
    path('download_dataset/', admin.download_dataset, name='download_dataset'),
    path('download_report', admin.download_report, name='download_report'),
    path('<int:taskdata_ptr_id>/update', admin.update, name='update'),
    path('report', admin.report, name='report'),
    path('log', admin.log, name='log'),
    path('assign_tasks', admin.assign_tasks, name='assign_tasks'),
    path('summarize', admin.summarize, name='summarize'),
]