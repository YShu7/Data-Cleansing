from django.contrib import messages
from django.core.paginator import Paginator
from django.http import QueryDict
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import loader
from django.views.decorators.csrf import csrf_protect

from assign.models import Assignment
from authentication.forms import CustomPasswordChangeForm
from datacleansing.settings import USER_DIR, MSG_FAIL_DATA_NONEXIST, MSG_FAIL_CHOICE, VOT, VAL, \
    MSG_SUCCESS_VAL, MSG_SUCCESS_VOTE, MSG_SUCCESS_RETRY
from datacleansing.utils import get_pre_url
from pages.decorators import user_login_required
from pages.models import ValidatingData, VotingData, FinalizedData, Choice
from pages.views.utils import get_assigned_tasks_context, log as data_log, merge_validate_context, get_ids, \
    s_format, is_true, split, clear


@user_login_required
def profile(request):
    template = loader.get_template('{}/profile.html'.format(USER_DIR))
    context = {
        'title': "Profile",
        'form_obj': CustomPasswordChangeForm(user=request.user),
        'show': False
    }
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
    template = loader.get_template('{}/validating_tasks.html'.format(USER_DIR))

    # Initiate paginator
    data, task_num = get_assigned_tasks_context(request.user, ValidatingData)
    paginator = Paginator(data, 1)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    per_task_ratio = 0
    if task_num["todo"] != 0:
        per_task_ratio = 100 / task_num["todo"]
    doing = 0
    if 'data' in request.session:
        doing = len(get_ids(request.session['data']['validate_ids']))

    context = {
        'page_obj': page_obj,
        'title': 'Validating Tasks',
        'num_done': task_num["done"],
        'num_total': task_num["total"],
        'num_doing': doing,
        'per_task_ratio': per_task_ratio,
    }

    if request.method == 'POST':
        data = {}
        if "submit" not in request.POST:
            old_data = request.session.pop('data', False)

            if old_data:
                data = merge_validate_context(request.POST, old_data)
            else:
                data = request.POST
            request.session['data'] = data
            return HttpResponse(template.render(request=request, context=context))
        else:
            data = request.session.pop('data', False)

        # merge session and post
        request.POST = merge_validate_context(new_data=request.POST, old_data=data)

        validate_ids = set(request.POST['validate_ids'])
        for validate_id in validate_ids:
            try:
                task = ValidatingData.objects.get(pk=validate_id)
            except ValidatingData.DoesNotExist:
                messages.add_message(request, level=messages.ERROR,
                                     message=MSG_FAIL_DATA_NONEXIST.format(validate_id),
                                     extra_tags="danger")
                continue
            except ValueError:
                continue

            approve = request.POST["approve_value_{}".format(validate_id)]
            new_ans = task.answer_text

            # User has done this assignment
            try:
                assign = Assignment.objects.get(task_id=validate_id, tasker_id=request.user.id)
                assign.is_done()
            except Assignment.DoesNotExist:
                pass

            if approve == "true":
                # if user approve the answer, add votes
                task.approve()
            elif approve == "false":
                # if user disapprove the answer, create VotingData and the choice
                task.disapprove(new_ans=request.POST["new_ans_{}".format(validate_id)])

            task.validate()
            data_log(request.user, task.data_ptr, VAL, new_ans)
        messages.success(request, MSG_SUCCESS_VAL)
        return HttpResponseRedirect(request.path)

    return HttpResponse(template.render(request=request, context=context))


@user_login_required
@csrf_protect
def vote(request, vote_id=None):
    if request.method == 'POST':
        try:
            choice = request.POST['choice']
            data = VotingData.objects.get(pk=vote_id)
            selected_choice = Choice.objects.get(data_id=vote_id, pk=choice)
        except VotingData.DoesNotExist:
            messages.add_message(request, level=messages.ERROR,
                                 message=MSG_FAIL_DATA_NONEXIST, extra_tags="danger")
            return HttpResponseRedirect(get_pre_url(request))
        except Choice.DoesNotExist:
            messages.add_message(request, level=messages.ERROR,
                                 message=MSG_FAIL_CHOICE, extra_tags="danger")
            return HttpResponseRedirect(get_pre_url(request))

        try:
            assign = Assignment.objects.get(task_id=vote_id, tasker_id=request.user.id)
            assign.is_done()
        except Assignment.DoesNotExist:
            pass

        data.vote(selected_choice)
        messages.success(request, MSG_SUCCESS_VOTE)
        data_log(request.user, data, VOT, choice)
    else:
        template = loader.get_template('{}/voting_tasks.html'.format(USER_DIR))

        # Initiate paginator
        data, task_num = get_assigned_tasks_context(request.user, VotingData, condition=(lambda x: x.is_active))
        for d in data:
            d.answers = d.choice_set.all()
        paginator = Paginator(data, 1)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        per_task_ratio = 0
        if task_num["todo"] != 0:
            per_task_ratio = 100 / task_num["todo"]
        context = {
            'page_obj': page_obj,
            'num_done': task_num["done"],
            'num_total': task_num["total"],
            'num_doing': 0,
            'title': 'Voting Tasks',
        }
        return HttpResponse(template.render(request=request, context=context))
    return HttpResponseRedirect(get_pre_url(request))


@user_login_required
@csrf_protect
def keywords(request, data_id=None):
    if request.method == "POST":
        try:
            qns_keywords = request.POST["qns_keywords"]
            ans_keywords = request.POST["ans_keywords"]
            data = FinalizedData.objects.get(pk=data_id)
        except FinalizedData.DoesNotExist:
            messages.add_message(request, level=messages.ERROR,
                                 message=MSG_FAIL_DATA_NONEXIST, extra_tags="danger")
            return HttpResponseRedirect(get_pre_url(request))

        try:
            assign = Assignment.objects.get(task_id=data_id, tasker_id=request.user.id)
            assign.is_done()
        except Assignment.DoesNotExist:
            pass

        data.update_keywords(qns_keywords, ans_keywords)
        messages.success(request, MSG_SUCCESS_VOTE)
        #data_log(request.user, data)
    else:
        template = loader.get_template('{}/keywords_tasks.html'.format(USER_DIR))

        # Initiate paginator
        data, task_num = get_assigned_tasks_context(request.user, FinalizedData)
        paginator = Paginator(data, 1)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        per_task_ratio = 0
        if task_num["todo"] != 0:
            per_task_ratio = 100 / task_num["todo"]
        doing = 0
        if 'data' in request.session:
            doing = len(get_ids(request.session['data']['validate_ids']))

        context = {
            'page_obj': page_obj,
            'title': 'Keyword Selection Tasks',
            'num_done': task_num["done"],
            'num_total': task_num["total"],
            'num_doing': doing,
            'per_task_ratio': per_task_ratio,
        }
        return HttpResponse(template.render(request=request, context=context))
    return HttpResponseRedirect(get_pre_url(request))


def retry_sign_up(request):
    request.user.approve(None)
    messages.success(request, MSG_SUCCESS_RETRY)
    return HttpResponseRedirect('/')
