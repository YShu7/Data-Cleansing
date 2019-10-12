from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from .models import *
from django.core import serializers
from django.template import loader

# Create your views here.

def index(request):
    template = loader.get_template('pages/tasks.html')
    context = {
        'question_list_validating': Data.objects.all(),
        'question_list_voting': VotingData.objects.all(),
        'login_user': 'Alice',
        'title': 'Tasks'
    }
    return HttpResponse(template.render(context))

def profile(request):
    template = loader.get_template('pages/profile.html')
    context = {
        'title': 'Profile'
    }
    return HttpResponse(template.render(context))

def validate():
    return HttpResponseRedirect(reverse('index'))