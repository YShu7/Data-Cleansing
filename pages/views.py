from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from .models import *
from django.core import serializers
from django.template import loader
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def index(request):
    user = request.user
    if user is not None:
        template = loader.get_template('pages/tasks.html')
        context = {
            'question_list_validating': Data.objects.all(),
            'question_list_voting': VotingData.objects.all(),
            'login_user': user,
            'title': 'Tasks'
        }
        return HttpResponse(template.render(context))
    else:
        template = loader.get_template('registration/login.html')
        context = {
            'title': 'Log In',
            'error': "Invalid Log In"
        }
        return HttpResponse(template.render(context))
    

def profile(request):
    template = loader.get_template('pages/profile.html')
    context = {
        'login_user': 'Alice',
        'title': 'Profile'
    }
    return HttpResponse(template.render(context))

def validate(request):
    return HttpResponseRedirect(request.path_info)

def vote(request, data_id):
    print("VOTE")
    print(request)
    data = get_object_or_404(VotingData, pk=data_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return HttpResponseRedirect(reverse('index', args=()))
    else:
        selected_choice.votes += 1
        selected_choice.save()

        return HttpResponseRedirect(reverse('index', args=()))