from django.contrib import messages
from django.http import QueryDict
from django.shortcuts import *
from django.views.decorators.csrf import csrf_protect

from authentication.forms import CustomPasswordChangeForm
from datacleansing.settings import *
from datacleansing.utils import get_pre_url
from pages.decorators import user_login_required
from pages.views.utils import *


@user_login_required
def task_list(request):
    template = loader.get_template('{}/tasks.html'.format(USER_DIR))
    context = get_assigned_tasks_context(request.user)
    return HttpResponse(template.render(request=request, context=context))


@user_login_required
def profile(request):
    template = loader.get_template('{}/profile.html'.format(USER_DIR))
    context = get_profile_context(request.user)
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


@user_login_required
@csrf_protect
def validate(request):
    if request.method == 'POST':
        validate_ids = request.POST['validate_ids'].split(',')
        for validate_id in validate_ids:
            try:
                task = ValidatingData.objects.get(pk=validate_id)
            except ValidatingData.DoesNotExist:
                messages.add_message(request, level=messages.ERROR, message=MSG_FAIL_DATA_NONEXIST.format(validate_id),
                                     extra_tags="danger")
                continue

            approve = request.POST["approve_value_{}".format(validate_id)]
            new_ans = task.answer_text

            # User has done this assignment
            try:
                assign = Assignment.objects.get(task_id=validate_id, tasker_id=request.user.id)
                assign.done()
            except Assignment.DoesNotExist:
                pass

            if approve == "true":
                # if user approve the answer, add votes
                task.approve()
            else:
                # if user disapprove the answer, create VotingData and the choice
                task.disapprove(new_ans=request.POST["new_ans_{}".format(validate_id)])

            task.validate()
            log(request.user, task, VAL, new_ans)
    return HttpResponseRedirect(get_pre_url(request))


@user_login_required
@csrf_protect
def vote(request, id):
    if request.method == 'POST':
        try:
            choice = request.POST['choice']
            data = VotingData.objects.get(pk=id)
            selected_choice = Choice.objects.get(data_id=id, pk=choice)
        except VotingData.DoesNotExist:
            messages.add_message(request, level=messages.ERROR, message=MSG_FAIL_DATA_NONEXIST, extra_tags="danger")
            return HttpResponseRedirect(get_pre_url(request))
        except Choice.DoesNotExist:
            messages.add_message(request, level=messages.ERROR, message=MSG_FAIL_CHOICE, extra_tags="danger")
            return HttpResponseRedirect(get_pre_url(request))

        try:
            assign = Assignment.objects.get(task_id=id, tasker_id=request.user.id)
            assign.done()
        except Assignment.DoesNotExist:
            pass

        data.vote(selected_choice)
        log(request.user, data, VOT, choice)
    return HttpResponseRedirect(get_pre_url(request))
