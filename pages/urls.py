from django.urls import path

from pages.views import views, user, admin

urlpatterns = [
    path('', views.index, name='index'),
    path('help', views.help, name='help'),

    path('tasks/validate', user.validate, name='user'),
    path('tasks/validate', user.validate, name='tasks/validate'),
    path('tasks/vote', user.vote, name='tasks/vote'),
    path('tasks/keywords', user.keywords, name='tasks/keywords'),
    path('tasks/image', user.image, name='tasks/image'),
    path('profile', user.profile, name='profile'),
    path('validate', user.validate, name='validate'),
    path('<int:data_id>/keywords', user.keywords, name='keywords'),
    path('<int:vote_id>/vote', user.vote, name='vote'),
    path('<int:img_id>/image', user.image, name='image'),
    path('retry_sign_up', user.retry_sign_up, name='retry_sign_up'),

    path('modify_users', admin.modify_users, name='admin'),
    path('modify_users', admin.modify_users, name='modify_users'),
    path('dataset', admin.dataset, name='dataset'),
    path('dataset/', admin.dataset, name='dataset'),
    path('dataset/<str:group_name>', admin.dataset, name='dataset'),
    path('download_dataset/<str:group_name>', admin.download_dataset, name='download_dataset'),
    path('download_dataset/', admin.download_dataset, name='download_dataset'),
    path('update', admin.update, name='update'),
    path('<int:data_ptr_id>/update', admin.update, name='update'),
    path('report', admin.report, name='report'),
    path('report/<str:from_date>/<str:to_date>', admin.report, name='report'),
    path('download_report', admin.download_report, name='download_report'),
    path('download_report/<str:from_date>/<str:to_date>', admin.download_report, name='download_report'),
    path('log', admin.log, name='log'),
    path('assign_tasks', admin.assign_tasks, name='assign_tasks'),
    path('summarize', admin.summarize, name='summarize'),
    path('import_dataset', admin.import_dataset, name='import_dataset'),
    path('group', admin.group, name='group'),
    path('delete_group', admin.delete_group, name='delete_group'),
    path('create_group', admin.create_group, name='create_group'),
]