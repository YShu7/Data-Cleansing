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
        ids = request.POST['validate_ids'].split(',');
        for id in ids:
            approve = request.POST["approve_value_{}".format(id)]
            new_ans = request.POST["new_ans_{}".format(id)]
    return render(request, 'pages/tasks.html')


@login_required
def vote(request, data_id):
    print("VOTE")
    print(request)
    data = get_object_or_404(VotingData, pk=data_id)
    try:
        selected_choice = data.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return HttpResponseRedirect(reverse('index', args=()))
    else:
        selected_choice.votes += 1
        selected_choice.save()

        return HttpResponseRedirect(reverse('index', args=()))