import csv
import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_protect

from assign.models import Assignment
from assign.views import assign
from authentication.models import CustomGroup, Log as auth_log
from authentication.utils import get_approved_users, get_pending_users
from authentication.forms import CreateGroupForm
from datacleansing.settings import ADMIN_DIR, MSG_SUCCESS_VOTE, MSG_SUCCESS_ASSIGN, MSG_SUCCESS_SUM, \
    MSG_FAIL_DEL_GRP, MSG_SUCCESS_DEL_GRP, MSG_SUCCESS_CRT_GRP
from datacleansing.utils import get_pre_url, Echo
from pages.decorators import superuser_admin_login_required, admin_login_required, superuser_login_required
from pages.models import Data, ValidatingData, VotingData, FinalizedData, Log
from pages.views.utils import get_unassigned_voting_data, get_finalized_data, compute_group_point, \
    account_log, get_data_log_msg, get_auth_log_msg


@superuser_admin_login_required
def modify_users(request):
    admin = request.user
    if request.method == "POST":
        user = get_user_model().objects.get(id=request.POST["id"])
        if 'approve' in request.POST:
            user.approve(True)
            account_log(admin, AuthLog.AccountAction.APPROVE, user)
        if 'activate' in request.POST:
            user.activate(True)
            account_log(admin, AuthLog.AccountAction.ACTIVATE, user)
        if 'deactivate' in request.POST:
            user.activate(False)
            account_log(admin, AuthLog.AccountAction.DEACTIVATE, user)
        if 'reject' in request.POST:
            user.approve(False)
            account_log(admin, AuthLog.AccountAction.REJECT, user)

        if request.user.is_superuser:
            if 'is_admin' in request.POST:
                user.assign_admin(True)
            else:
                user.assign_admin(False)
        return HttpResponseRedirect(get_pre_url(request))
    else:
        template = loader.get_template('{}/modify_users.html'.format(ADMIN_DIR))
        user = request.user
        pending_users = get_pending_users(user.group, user.is_superuser)
        approved_users = get_approved_users(user.group, user.is_superuser)

        context = {
            'pending_users': pending_users,
            'approved_users': approved_users,
        }
        return HttpResponse(template.render(context=context, request=request))


@superuser_admin_login_required
def dataset(request, group_name="all"):
    template = loader.get_template('{}/dataset.html'.format(ADMIN_DIR))
    group = request.user.group

    # Retrieve data
    finalized_data = get_finalized_data(group_name)
    groups = CustomGroup.objects.all()

    # Initiate paginator
    paginator = Paginator(finalized_data, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Compute num of finalized data
    num_data = finalized_data.count()

    context = {
        'title': 'Data Set',
        'num_data': num_data,
        'page_obj': page_obj,
        'groups': groups,
        'group_name': group_name,
    }
    return HttpResponse(template.render(request=request, context=context))


@superuser_admin_login_required
def download_dataset(request, group_name=""):
    """A view that streams a large CSV file."""
    # Generate a sequence of rows. The range is based on the maximum number of
    # rows that can be handled by a single sheet in most spreadsheet
    # applications.
    finalized_data = get_finalized_data(group_name)

    rows = [["id", "question", "answer"]]
    rows += ([data.id, data.title, data.answer_text] for data in finalized_data)
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                     content_type="text/csv")
    filename = "dataset_{}_{}.csv".format(group_name, datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    response['Content-Disposition'] = 'attachment; filename=' + filename
    return response


@superuser_admin_login_required
@csrf_protect
def update(request, data_ptr_id=None):
    if request.method == 'POST':
        # update VotingData to Data directly
        voting_data = VotingData.objects.get(data_ptr_id=data_ptr_id)

        ans = request.POST["choice"]
        if ans == "":
            messages.add_message(request, level=messages.ERROR, extra_tags="danger", message="Please choose an answer.")
        else:
            FinalizedData.create(title=voting_data.title, group=voting_data.group, ans=ans)
            voting_data.delete(keep_parents=True)
            messages.success(request, MSG_SUCCESS_VOTE)
        return HttpResponseRedirect(get_pre_url(request))
    else:
        template = loader.get_template('{}/setting_tasks.html'.format(ADMIN_DIR))
        group = request.user.group

        # Retrieve data
        voting_data = get_unassigned_voting_data(group)
        context = {
            'title': 'Data Set',
            'questions': voting_data,
        }
        return HttpResponse(template.render(request=request, context=context))


@superuser_admin_login_required
def report(request, from_date=None, to_date=None):
    template = loader.get_template('{}/report.html'.format(ADMIN_DIR))

    i = datetime.now()
    if not from_date:
        from_date = '{}-{}-{}'.format(i.year, i.month, i.day)
    if not to_date:
        to_date = '{}-{}-{}'.format(i.year, i.month, i.day)
    users = get_approved_users(request.user.group)

    context = {
        'title': 'Report',
        'today': '{}-{}-{}'.format('%04d' % i.year, '%02d' % i.month, '%02d' % i.day),
        'users': users,
    }

    if request.user.is_superuser:
        groups = compute_group_point()
        context = {
            'title': 'Report',
            'today': '{}-{}-{}'.format('%04d' % i.year, '%02d' % i.month, '%02d' % i.day),
            'users': users,
            'names': json.dumps(groups['names']),
            'points': json.dumps(groups['points']),
            'num_ans': json.dumps(groups['num_ans']),
            'accuracy': json.dumps(groups['accuracy']),
        }

    return HttpResponse(template.render(context=context, request=request))


@superuser_admin_login_required
def download_report(request):
    """A view that streams a large CSV file."""
    rows = [["id", "username", "certificate", "point", "accuracy"]]
    rows += ([user.id, user.username, user.certificate, user.point, user.accuracy()] for user in
             get_approved_users(request.user.group))
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                     content_type="text/csv")
    filename = "report_{}.csv".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    response['Content-Disposition'] = 'attachment; filename=' + filename
    return response


@superuser_admin_login_required
def log(request):
    template = loader.get_template('{}/log.html'.format(ADMIN_DIR))
    all_logs = Log.objects.all()
    logs = []
    if request.user.is_superuser:
        for log in all_logs:
            if log.user.is_superuser or log.user.is_admin:
                logs.append(get_data_log_msg(log))
    else:
        for log in all_logs:
            if log.user.is_admin and log.user.group == request.user.group:
                logs.append(get_data_log_msg(log))

    data_logs = auth_log.objects.all()
    for log in data_logs:
        logs.append(get_auth_log_msg(log))
    context = {
        'title': "Admin Log",
        'logs': logs,
    }
    return HttpResponse(template.render(context=context, request=request))


@admin_login_required
def assign_tasks(request):
    group = request.user.group
    users = get_user_model().objects.filter(is_active=True, is_approved=True, is_admin=False, group=group)
    validating_data = ValidatingData.objects.filter(group=group)
    voting_data = VotingData.objects.filter(is_active=True, group=group)

    Assignment.objects.all().delete()
    assign(users, Assignment, validating_data, Data)
    assign(users, Assignment, voting_data, Data)

    messages.success(request, MSG_SUCCESS_ASSIGN)
    return HttpResponseRedirect(get_pre_url(request))


@admin_login_required
def summarize(request):
    users = get_approved_users(request.user.group)
    logs = Log.objects.all().filter(checked=False)
    for user in users:
        user_logs = logs.filter(user=user)
        for user_log in user_logs:
            user_response = user_log.response
            try:
                data = FinalizedData.objects.get(title=user_log.task.task.title)
                if data and user_response == data.answer_text:
                    user.ans_is(True)
                else:
                    user.ans_is(False)
            except:
                pass

    messages.success(request, MSG_SUCCESS_SUM)
    return HttpResponseRedirect(get_pre_url(request))


@superuser_login_required
def group(request):
    template = loader.get_template('{}/group.html'.format(ADMIN_DIR))
    context = {
        'groups': CustomGroup.objects.all(),
        'delete_check_id': 'group_name',
        'delete_confirm_id': 'confirm_input',
        'create_form': CreateGroupForm(),
    }
    return HttpResponse(template.render(context=context, request=request))


@superuser_login_required
def delete_group(request):
    if request.method == "POST":
        group_name = request.POST["group_name"]
        if group_name == request.POST["confirm_input"]:
            CustomGroup.objects.get(name=group_name).delete()
            messages.success(request, MSG_SUCCESS_DEL_GRP.format(group_name))
        else:
            messages.add_message(request, level=messages.ERROR, extra_tags="danger", message=MSG_FAIL_DEL_GRP)
    return HttpResponseRedirect(get_pre_url(request))


@superuser_login_required
def create_group(request):
    form_obj = CreateGroupForm(request.POST)
    if form_obj.is_valid():
        form_obj.save()
        messages.success(request, MSG_SUCCESS_CRT_GRP.format(form_obj.data.get('name')))
    else:
        for error in form_obj.errors:
            error = form_obj.errors[error][0]
            if error:
                break
        messages.add_message(request, level=messages.ERROR, extra_tags="danger", message=error)
    return HttpResponseRedirect(get_pre_url(request))