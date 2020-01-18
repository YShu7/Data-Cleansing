from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from pages.views.helper import *
from authentication.forms import CustomPasswordChangeForm
from django.middleware.csrf import get_token
from django.shortcuts import *
from django.http import QueryDict
from django.utils import timezone


ADMIN_DIR = 'pages/admin'
USER_DIR = 'pages/user'
AUTH_DIR = 'authentication'


@login_required
def index(request):
    user = request.user
    if not user.is_admin:
        template = loader.get_template('{}/tasks.html'.format(USER_DIR))
        context = get_tasks_context(user)
        return HttpResponse(template.render(context))
    else:
        return HttpResponseRedirect('/admin')


@login_required
def profile(request):
    if request.user.is_admin:
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
    if request.user.is_admin:
        return HttpResponseRedirect('/admin')
    if request.method == 'POST':
        ids = request.POST['validate_ids'].split(',')
        for id in ids:
            task = ValidatingData.objects.get(taskdata_ptr_id=id)
            approve = request.POST["approve_value_{}".format(id)]
            assign = Assignment.objects.get(task_id=id, tasker_id=request.user.id)
            new_ans = task.answer_text

            if approve == "true":
                # if user approve the answer, add votes
                task.num_approved += 1
                task.save()
            else:
                # if user disapprove the answer, create VotingData and the choice
                task.num_disapproved += 1
                task.save()
                new_ans = request.POST["new_ans_{}".format(id)]
                data, _ = VotingData.objects.update_or_create(taskdata_ptr=task.taskdata_ptr, group=task.taskdata_ptr.group)
                Choice.objects.update_or_create(data=data, answer=new_ans)

            datas = VotingData.objects.filter(taskdata_ptr_id=task.taskdata_ptr_id, group=task.taskdata_ptr.group)
            if task.num_approved >= 2:
                # if enough user has approve the answer
                # the origin answer is considered to be correct
                Data.objects.update_or_create(title=task.taskdata_ptr.question_text,
                                              group=task.taskdata_ptr.group)
                for data in datas:
                    Choice.objects.filter(data=data).delete()
                task.delete()
            elif task.num_disapproved >= 2:
                # if enough user has disapprove the answer
                # the better answer should be selected by activating VotingData
                for data in datas:
                    data.is_active = True
                    data.save()
                task.delete()
            assign.done = True
            assign.save()
            Log.objects.update_or_create(user=request.user, task=assign, action='validate',
                                         response=new_ans, timestamp=timezone.now())
    else:
        HttpResponse("Request method is not allowed.")
    return HttpResponseRedirect("/")


@login_required
@csrf_exempt
def vote(request, taskdata_ptr_id):
    if request.user.is_admin:
        return HttpResponseRedirect('/admin')
    if request.method == 'POST':
        try:
            choice = request.POST['choice']
            data = VotingData.objects.get(pk=taskdata_ptr_id)
            selected_choice = Choice.objects.get(data_id=taskdata_ptr_id, pk=choice)
            assign = Assignment.objects.get(task_id=taskdata_ptr_id, tasker_id=request.user.id)
        except VotingData.DoesNotExist:
            return HttpResponse("Voting data doesn't exist.")
        except Choice.DoesNotExist:
            return HttpResponse("Choice doesn't exist.")
        else:
            # update num of votes of the selected choice
            selected_choice.num_votes += 1
            selected_choice.save()

            # get the number of choices that have been made for this question
            choices = Choice.objects.filter(data_id=taskdata_ptr_id)
            sum_votes = 0
            max_votes = selected_choice.num_votes
            for c in choices:
                sum_votes += c.num_votes
                max_votes = max(max_votes, c.num_votes)

            # if enough users have made responses to this question and this choice has the maximum num of votes,
            # this question is done
            if sum_votes >= 5 and selected_choice.num_votes == max_votes:
                Data.objects.update_or_create(question_text=data.question_text, answer_text=selected_choice.answer, group=data.group)
                data.delete()
            assign.done = True
            assign.save()
            Log.objects.update_or_create(user=request.user, task=assign, action='vote', response=choice, timestamp=timezone.now())
    else:
        return HttpResponse("Request method is not allowed.")

    return HttpResponseRedirect('/')