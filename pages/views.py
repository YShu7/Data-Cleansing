from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from .models import Data
# Create your views here.

class IndexView(generic.ListView):
    template_name = 'pages/index.html'
    context_object_name = 'question_list'

    def get_queryset(self):
        return Data.objects.all()
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['login_user'] = 'Alice'
        context['title'] = 'Tasks'
        return context

class TasksView(generic.ListView):
    template_name = 'pages/tasks.html'
    context_object_name = 'question_list'

    def get_queryset(self):
        return Data.objects.all()