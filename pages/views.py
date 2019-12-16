from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import *
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


@login_required
def index(request):
    user = request.user
    if user is not None:
        template = loader.get_template('pages/tasks.html')
        voting_data = VotingData.objects.all()
        for data in voting_data:
            data.answers = Choice.objects.filter(data_id=data.id)
        context = {
            'question_list_validating': Data.objects.all(),
            'question_list_voting': voting_data,
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


@login_required
def profile(request):
    template = loader.get_template('pages/profile.html')
    context = {
        'login_user': 'Alice',
        'title': 'Profile'
    }
    return HttpResponse(template.render(context))


@login_required
@csrf_exempt
def validate(request):
    if request.method == 'POST':
        ids = request.POST['validate_ids'].split(',')
        for id in ids:
            approve = request.POST["approve_value_{}".format(id)]
            new_ans = request.POST["new_ans_{}".format(id)]
    else:
        HttpResponse("Request method is not allowed.")
    return render(request, 'pages/tasks.html')


@login_required
@csrf_exempt
def vote(request, question_id):
    if request.method == 'POST':
        try:
            choice = request.POST["choice"]
            data = VotingData.objects.get(pk=question_id)
            selected_choice = Choice.objects.get(data_id=question_id, pk=request.POST['choice'])
        except VotingData.DoesNotExist:
            return HttpResponse("Voting data doesn't exist.")
        except Choice.DoesNotExist:
            return HttpResponse("Choice doesn't exist.")
        else:
            selected_choice.num_votes += 1
            selected_choice.save()
    else:
        return HttpResponse("Request method is not allowed.")
    return render(request, 'pages/tasks.html')