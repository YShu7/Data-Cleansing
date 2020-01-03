from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from pages.views.helper import *
from authentication.forms import CustomPasswordChangeForm
from django.middleware.csrf import get_token
from django.shortcuts import *
from django.contrib import messages
from django.http import QueryDict


ADMIN_DIR = 'pages/admin'
USER_DIR = 'pages/user'
AUTH_DIR = 'authentication'


@login_required
def index(request):
    user = request.user
    if user is not None:
        if not user.is_superuser:
            template = loader.get_template('{}/tasks.html'.format(USER_DIR))
            context = get_tasks_context(user)
            return HttpResponse(template.render(context))
        else:
            return HttpResponseRedirect('/admin')
    else:
        template = loader.get_template('{}/login.html'.format(AUTH_DIR))
        context = {
            'title': 'Log In',
            'error': "Invalid Log In"
        }
        return HttpResponse(template.render(context))


@login_required
def profile(request):
    if request.user.is_superuser:
        return HttpResponseRedirect('/admin')
    template = loader.get_template('{}/profile.html'.format(USER_DIR))
    context = get_profile_context(request.user)
    context['token'] = get_token(request)
    context['next'] = '{}/profile.html'.format(USER_DIR)
    context['form_obj'] = CustomPasswordChangeForm(user=request.user)
    context['show'] = False
    success = request.session.pop('success', False)
    data = request.session.pop('data', False)
    if not success and data:
        context['show'] = True
        qdict = QueryDict('', mutable=True)
        qdict.update(data)
        context['form_obj'] = CustomPasswordChangeForm(data=qdict, user=request.user)

    return HttpResponse(template.render(context, request))


@login_required
@csrf_exempt
def validate(request):
    if request.user.is_superuser:
        return HttpResponseRedirect('/admin')
    if request.method == 'POST':
        ids = request.POST['validate_ids'].split(',')
        for id in ids:
            task = ValidatingData.objects.get(id=id)
            approve = request.POST["approve_value_{}".format(id)]
            assign = AssignmentValidate.objects.get(task_id=id)
            if approve == "true":
                task.num_approved += 1
                task.save()
            else:
                task.num_disapproved += 1
                task.save()
                new_ans = request.POST["new_ans_{}".format(id)]
                data, _ = VotingData.objects.update_or_create(question_text=task.question_text, type=task.type)
                Choice.objects.update_or_create(data=data, answer=new_ans)

            datas = VotingData.objects.filter(question_text=task.question_text, type=task.type)
            if task.num_approved >= 2:
                Data.objects.update_or_create(question_text=task.question_text, answer_text=task.answer_text,
                                              type=task.type)
                for data in datas:
                    Choice.objects.filter(data=data).delete()
                task.delete()
            elif task.num_disapproved >= 2:
                for data in datas:
                    data.activate = True
                    data.save()
                task.delete()
            assign.done = True
            assign.save()
    else:
        HttpResponse("Request method is not allowed.")
    return HttpResponseRedirect("/")


@login_required
@csrf_exempt
def vote(request, question_id):
    if request.user.is_superuser:
        return HttpResponseRedirect('/admin')
    if request.method == 'POST':
        try:
            choice = request.POST['choice']
            data = VotingData.objects.get(pk=question_id)
            selected_choice = Choice.objects.get(data_id=question_id, pk=choice)
            assign = AssignmentVote.objects.get(task_id=question_id)
        except VotingData.DoesNotExist:
            return HttpResponse("Voting data doesn't exist.")
        except Choice.DoesNotExist:
            return HttpResponse("Choice doesn't exist.")
        else:
            selected_choice.num_votes += 1
            selected_choice.save()

            choices = Choice.objects.filter(data_id=question_id)
            sum_votes = 0
            max_votes = selected_choice.num_votes
            for c in choices:
                sum_votes += c.num_votes
                max_votes = max(max_votes, c.num_votes)
            if sum_votes >= 5 and selected_choice.num_votes == max_votes:
                Data.objects.update_or_create(question_text=data.question_text, answer_text=selected_choice.answer, type=data.type)
                data.delete()
            assign.done = True
            assign.save()
    else:
        return HttpResponse("Request method is not allowed.")

    return HttpResponseRedirect('/')