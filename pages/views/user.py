from django.contrib import messages
from django.http import QueryDict
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import loader
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect

from authentication.forms import CustomPasswordChangeForm
from datacleansing.settings import USER_DIR, MSG_FAIL_DATA_NONEXIST, MSG_FAIL_CHOICE, VOT, VAL, SEL, \
    MSG_SUCCESS_VAL, MSG_SUCCESS_VOTE, MSG_SUCCESS_RETRY, MSG_FAIL_LABEL_NONEXIST
from pages.decorators import user_login_required
from pages.models.image import ImageData, ImageLabel
from pages.models.models import FinalizedData
from pages.models.validate import ValidatingData
from pages.models.vote import VotingData, Choice
from pages.views.utils import get_assigned_tasks_context, done_assignment, \
    log as data_log, merge_validate_context, compute_progress, compute_paginator


@user_login_required
def profile(request):
    template = loader.get_template('{}/profile.html'.format(USER_DIR))
    context = {
        'title': _("Profile"),
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
    request.POST
    template = loader.get_template('{}/validating_tasks.html'.format(USER_DIR))

    # Initiate paginator
    data, task_num = get_assigned_tasks_context(request.user, ValidatingData)
    doing = compute_progress(request)
    page_obj = compute_paginator(request, data, task_num['done'], doing, task_num['total'])

    context = {
        'page_obj': page_obj,
        'title': _('Validating Tasks'),
        'num_done': task_num["done"],
        'num_total': task_num["total"],
        'num_doing': doing,
    }

    if request.method == 'POST':
        data = {}
        old_data = request.session.pop('data', False)

        if old_data:
            data = merge_validate_context(request.POST, old_data)
        else:
            data = request.POST

        if "submit" not in request.POST:
            request.session['data'] = data
            return HttpResponseRedirect(reverse('tasks/validate'))

        if isinstance(data['validate_ids'], list):
            validate_ids = set(data['validate_ids'])
        else:
            validate_ids = set(data['validate_ids'].split(','))
        for validate_id in validate_ids:
            validate_id = int(validate_id)
            try:
                task = ValidatingData.objects.get(pk=validate_id)
            except ValidatingData.DoesNotExist:
                messages.add_message(request, level=messages.ERROR,
                                     message=MSG_FAIL_DATA_NONEXIST.format(validate_id),
                                     extra_tags="danger")
                continue
            except ValueError:
                continue

            approve = data["approve_value_{}".format(validate_id)]
            new_ans = task.answer_text

            # User has done this assignment
            done_assignment(validate_id, request.user.id)

            if approve == "true":
                # if user approve the answer, add votes
                task.approve()
            elif approve == "false":
                # if user disapprove the answer, create VotingData and the choice
                task.disapprove(new_ans=data["new_ans_{}".format(validate_id)])

            task.validate()
            data_log(request.user, task, VAL, new_ans)
        messages.success(request, _(MSG_SUCCESS_VAL))
        return HttpResponseRedirect(reverse('tasks/validate'))
    return HttpResponse(template.render(request=request, context=context))


@user_login_required
@csrf_protect
def vote(request):
    template = loader.get_template('{}/voting_tasks.html'.format(USER_DIR))

    # Initiate paginator
    data, task_num = get_assigned_tasks_context(request.user, VotingData,
                                                condition=(lambda x: x.is_active and not x.is_contro))
    page_obj = compute_paginator(request, data, task_num['done'], 0, task_num['total'])

    for d in data:
        d.answers = d.choice_set.all()

    context = {
        'page_obj': page_obj,
        'num_done': task_num["done"],
        'num_total': task_num["total"],
        'num_doing': 0,
        'title': _('Voting Tasks'),
        'next': 'tasks/vote',
    }
    return HttpResponse(template.render(request=request, context=context))


@user_login_required
@csrf_protect
def vote_post(request, vote_id=None):
    if request.method == 'POST':
        try:
            choice = request.POST['choice']
            data = VotingData.objects.get(pk=vote_id)
            selected_choice = Choice.objects.get(data_id=vote_id, pk=choice)
        except ValueError:
            messages.add_message(request, level=messages.ERROR,
                                 message=_(MSG_FAIL_CHOICE), extra_tags="danger")
            return HttpResponseRedirect(reverse('tasks/vote'))
        except VotingData.DoesNotExist:
            messages.add_message(request, level=messages.ERROR,
                                 message=_(MSG_FAIL_DATA_NONEXIST.format(vote_id)), extra_tags="danger")
            return HttpResponseRedirect(reverse('tasks/vote'))
        except Choice.DoesNotExist:
            messages.add_message(request, level=messages.ERROR,
                                 message=_(MSG_FAIL_CHOICE), extra_tags="danger")
            return HttpResponseRedirect(reverse('tasks/vote'))

        done_assignment(vote_id, request.user.id)

        data.vote(selected_choice)

        messages.success(request, _(MSG_SUCCESS_VOTE))
        data_log(request.user, data, VOT, choice)

        next = request.META.get('HTTP_REFERER')
        if next is None:
            next = '/'
        return HttpResponseRedirect(next)


@user_login_required
@csrf_protect
def contro(request):
    template = loader.get_template('{}/contro_tasks.html'.format(USER_DIR))

    # Initiate paginator
    data, task_num = get_assigned_tasks_context(request.user, VotingData,
                                                condition=(lambda x: not x.is_active and x.is_contro))

    page_obj = compute_paginator(request, data, task_num['done'], 0, task_num['total'])

    for d in data:
        d.answers = d.choice_set.all()

    context = {
        'page_obj': page_obj,
        'num_done': task_num["done"],
        'num_total': task_num["total"],
        'num_doing': 0,
        'title': _('Controversial Tasks'),
        'next': 'tasks/contro',
    }
    return HttpResponse(template.render(request=request, context=context))

@user_login_required
@csrf_protect
def contro_post(request, contro_id):
    seleted = request.POST['selected']
    if seleted != "1":
        messages.add_message(request, level=messages.ERROR,
                             message=_(MSG_FAIL_CHOICE), extra_tags="danger")
        return HttpResponseRedirect(reverse('tasks/contro'))
    try:
        choice = request.POST['choice']
        data = VotingData.objects.get(pk=contro_id)
        if choice == "":
            new_ans = request.POST['new_ans']
            data.finalize(new_ans)
        else:
            try:
                selected_choice = Choice.objects.get(data=data, pk=choice)
                data.finalize(selected_choice.answer)
            except Choice.DoesNotExist:
                messages.add_message(request, level=messages.ERROR,
                                     message=_(MSG_FAIL_CHOICE), extra_tags="danger")
                return HttpResponseRedirect(reverse('tasks/contro'))
    except ValueError:
        messages.add_message(request, level=messages.ERROR,
                             message=_(MSG_FAIL_CHOICE), extra_tags="danger")
        return HttpResponseRedirect(reverse('tasks/contro'))
    except VotingData.DoesNotExist:
        messages.add_message(request, level=messages.ERROR,
                             message=_(MSG_FAIL_DATA_NONEXIST.format(contro_id)), extra_tags="danger")
        return HttpResponseRedirect(reverse('tasks/contro'))

    done_assignment(contro_id, request.user.id)

    messages.success(request, _(MSG_SUCCESS_VOTE))
    data_log(request.user, data, VOT, choice)

    next = request.META.get('HTTP_REFERER')
    if next is None:
        next = '/'
    return HttpResponseRedirect(next)

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
                                 message=_(MSG_FAIL_DATA_NONEXIST).format(data_id), extra_tags="danger")
            return HttpResponseRedirect(reverse('tasks/keywords'))

        done_assignment(data_id, request.user.id)

        data.update_keywords(qns_keywords, ans_keywords)
        messages.success(request, _(MSG_SUCCESS_VOTE))
        data_log(request.user, data, SEL, qns_keywords + "\n" + ans_keywords)
    else:
        template = loader.get_template('{}/keywords_tasks.html'.format(USER_DIR))

        # Initiate paginator
        data, task_num = get_assigned_tasks_context(request.user, FinalizedData)
        doing = compute_progress(request)
        page_obj = compute_paginator(request, data, task_num['done'], doing, task_num['total'])

        context = {
            'page_obj': page_obj,
            'title': _('Keyword Selection Tasks'),
            'num_done': task_num["done"],
            'num_total': task_num["total"],
            'num_doing': 0,
        }
        return HttpResponse(template.render(request=request, context=context))
    return HttpResponseRedirect(reverse('tasks/keywords'))


@user_login_required
@csrf_protect
def image(request, img_id=None):
    if request.method == "POST":
        try:
            data = ImageData.objects.all().get(pk=img_id)
            label_id = request.POST["select_label"]
            label = ImageLabel.objects.all().get(id=label_id)
        except ImageData.DoesNotExist:
            messages.add_message(request, level=messages.ERROR,
                                 message=_(MSG_FAIL_DATA_NONEXIST).format(img_id), extra_tags="danger")
            return HttpResponseRedirect(reverse('tasks/image'))
        except ImageLabel.DoesNotExist:
            messages.add_message(request, level=messages.ERROR,
                                 message=_(MSG_FAIL_LABEL_NONEXIST).format(label_id), extra_tags="danger")
            return HttpResponseRedirect(reverse('tasks/image'))

        done_assignment(img_id, request.user.id)

        data.vote(label)
        messages.success(request, _(MSG_SUCCESS_VOTE))
        data_log(request.user, data, VOT, label)
        return HttpResponseRedirect(reverse('tasks/image'))

    if request.method == "GET":
        template = loader.get_template('{}/image_tasks.html'.format(USER_DIR))
        data, task_num = get_assigned_tasks_context(request.user, ImageData)
        doing = compute_progress(request)
        page_obj = compute_paginator(request, data, task_num['done'], doing, task_num['total'])

        context = {
            'page_obj': page_obj,
            'title': _('Image Label Validation Tasks'),
            'num_done': task_num["done"],
            'num_total': task_num["total"],
            'num_doing': 0,
        }
        return HttpResponse(template.render(request=request, context=context))


def retry_sign_up(request):
    request.user.approve(None)
    messages.success(request, _(MSG_SUCCESS_RETRY))
    return HttpResponseRedirect('/')
