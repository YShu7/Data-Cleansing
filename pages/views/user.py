from django.contrib import messages
from django.db import models
from django.http import QueryDict
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import loader
from django.views.decorators.csrf import csrf_protect

from authentication.forms import CustomPasswordChangeForm
from datacleansing.settings import USER_DIR, MSG_FAIL_DATA_NONEXIST, MSG_FAIL_CHOICE, VOT, VAL, \
    MSG_SUCCESS_VAL, MSG_SUCCESS_VOTE, MSG_SUCCESS_RETRY, MSG_FAIL_LABEL_NONEXIST
from datacleansing.utils import get_pre_url
from pages.decorators import user_login_required
from pages.models.models import FinalizedData
from pages.models.validate import ValidatingData
from pages.models.vote import VotingData, Choice
from pages.models.image import ImageData, ImageLabel
from pages.views.utils import get_assigned_tasks_context, done_assignment, \
    log as data_log, merge_validate_context, get_ids, compute_progress, compute_paginator


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
    page_obj, task_num = compute_paginator(request, data)
    doing, per_task_ratio = compute_progress(request, task_num)

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
            done_assignment(validate_id, request.user.id)

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

        done_assignment(vote_id, request.user.id)

        data.vote(selected_choice)
        messages.success(request, MSG_SUCCESS_VOTE)
        data_log(request.user, data, VOT, choice)
    else:
        template = loader.get_template('{}/voting_tasks.html'.format(USER_DIR))

        # Initiate paginator
        data, task_num = get_assigned_tasks_context(request.user, VotingData, condition=(lambda x: x.is_active))
        page_obj, task_num = compute_paginator(request, data)

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

        done_assignment(data_id, request.user.id)

        data.update_keywords(qns_keywords, ans_keywords)
        messages.success(request, MSG_SUCCESS_VOTE)
        # data_log(request.user, data)
    else:
        template = loader.get_template('{}/keywords_tasks.html'.format(USER_DIR))

        # Initiate paginator
        data, task_num = get_assigned_tasks_context(request.user, FinalizedData)
        page_obj, task_num = compute_paginator(request, data)
        doing, per_task_ratio = compute_progress(request, task_num)

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


@user_login_required
@csrf_protect
def image(request, img_id=None):
    if request.method == "POST":
        try:
            data = ImageData.objects.all().get(pk=img_id)
            label_id = request.POST["label"]
            label = ImageLabel.objects.all().get(id=label_id)
        except ImageData.DoesNotExist:
            messages.add_message(request, level=messages.ERROR,
                                 message=MSG_FAIL_DATA_NONEXIST, extra_tags="danger")
            return HttpResponseRedirect(get_pre_url(request))
        except ImageLabel.DoesNotExist:
            messages.add_message(request, level=messages.ERROR,
                                 message=MSG_FAIL_LABEL_NONEXIST, extra_tags="danger")
            return HttpResponseRedirect(get_pre_url(request))

        done_assignment(img_id, request.user.id)

        data.vote(label)
        messages.success(request, MSG_SUCCESS_VOTE)
        data_log(request.user, data, VOT, label)
        return HttpResponseRedirect(request.path)

    if request.method == "GET":
        template = loader.get_template('{}/image_tasks.html'.format(USER_DIR))
        data, task_num = get_assigned_tasks_context(request.user, ImageData, parent=models.Model)
        page_obj, task_num = compute_paginator(request, data)
        doing, per_task_ratio = compute_progress(request, task_num)

        context = {
            'page_obj': page_obj,
            'title': 'Image Label Validation Tasks',
            'num_done': task_num["done"],
            'num_total': task_num["total"],
            'num_doing': doing,
            'per_task_ratio': per_task_ratio,
        }
        return HttpResponse(template.render(request=request, context=context))


def retry_sign_up(request):
    request.user.approve(None)
    messages.success(request, MSG_SUCCESS_RETRY)
    return HttpResponseRedirect('/')
