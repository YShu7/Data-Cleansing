import csv
from datetime import datetime
import json

from django.core.paginator import Paginator
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_protect

from assign.views import assign
from assign.models import Assignment
from pages.views.utils import *
from pages.decorators import superuser_admin_login_required, admin_login_required


ADMIN_DIR = 'pages/admin'
USER_DIR = 'pages/user'
AUTH_DIR = 'authentication'


@superuser_admin_login_required
def modify_users(request):
    if request.method == "POST":
        user = get_user_model().objects.get(id=request.POST["id"])
        if 'approve' in request.POST:
            user.approve(True)
        if 'activate' in request.POST:
            user.activate(True)
        if 'deactivate' in request.POST:
            user.activate(False)
        if 'reject' in request.POST:
            user.delete()
        return HttpResponseRedirect('/')
    else:
        template = loader.get_template('{}/modify_users.html'.format(ADMIN_DIR))
        user = request.user
        pending_users = get_pending_users(user.group, user.is_superuser)
        approved_users = get_approved_users(user.group, user.is_superuser)

        context = {
            'login_user': user,
            'pending_users': pending_users,
            'approved_users': approved_users,
        }
        return HttpResponse(template.render(context=context, request=request))


@superuser_admin_login_required
def dataset(request, group_name="all"):
    template = loader.get_template('{}/dataset.html'.format(ADMIN_DIR))
    group = request.user.group

    # get all VotingData ids that are not allocated to any user
    voting_data = VotingData.objects.all()
    if group:
        voting_data = voting_data.filter(group=group)
    ids = [i.id for i in voting_data]
    #exclude_ids = [i.task.id for i in Assignment.objects.all()]
    exclude_ids = []
    for exclude_id in exclude_ids:
        if exclude_id in ids:
            ids.remove(exclude_id)

    # get all VotingData objects and combine them with their respective choices
    voting_data = []
    for id in ids:
        voting_data.append(VotingData.objects.get(id=id))
    for data in voting_data:
        data.answers = Choice.objects.filter(data_id=data.id)

    finalized_data = get_finalized_data(group_name)
    paginator = Paginator(finalized_data, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    num_data = finalized_data.count()
    groups = CustomGroup.objects.all()

    context = {
        'title': 'Data Set',
        'num_data': num_data,
        'page_obj': page_obj,
        'groups': groups,
        'data': voting_data,
        'login_user': request.user,
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
def update(request, taskdata_ptr_id):
    if request.method == 'POST':
        # update VotingData to Data directly
        voting_data = VotingData.objects.get(data_ptr_id=taskdata_ptr_id)

        ans = request.POST["choice"]
        if ans == "":
            messages.add_message(request, level=messages.ERROR, extra_tags="danger", message="Please choose an answer.")
        else:
            FinalizedData.create(title=voting_data.title, group=voting_data.group, ans=ans)
            voting_data.delete(keep_parents=True)
            messages.success(request, "Update Succeed.")
    return HttpResponseRedirect("/dataset")


@superuser_admin_login_required
def report(request):
    template = loader.get_template('{}/report.html'.format(ADMIN_DIR))
    i = datetime.now()
    users = get_approved_users(request.user.group)

    context = {
        'title': 'Report',
        'today': '{}-{}-{}'.format(i.year, i.month, i.day),
        'users': users,
        'login_user': request.user,
    }

    if request.user.is_superuser:
        groups = compute_group_point()
        context = {
            'title': 'Report',
            'today': '{}-{}-{}'.format(i.year, i.month, i.day),
            'users': users,
            'names': json.dumps(groups['names']),
            'points': json.dumps(groups['points']),
            'num_ans': json.dumps(groups['num_ans']),
            'accuracy': json.dumps(groups['accuracy']),
            'login_user': request.user,
        }

    return HttpResponse(template.render(context=context))


@superuser_admin_login_required
def download_report(request):
    """A view that streams a large CSV file."""
    rows = [["id", "username", "certificate", "point", "accuracy"]]
    rows += ([user.id, user.username, user.certificate, user.point, user.accuracy()] for user in get_approved_users(request.user.group))
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
        for log in logs:
            if log.user.is_superuser or log.user.is_admin:
                logs.append(log)
    else:
        for log in logs:
            if log.user.is_admin and log.user.group == request.user.group:
                logs.append(log)
    context = {
        'title': "Admin Log",
        'login_user': request.user,
        'logs': logs,
    }
    return HttpResponse(template.render(context=context))


@admin_login_required
def assign_tasks(request):
    group = request.user.group
    users = get_user_model().objects.filter(is_active=True, is_approved=True, is_admin=False)
    validating_data = ValidatingData.objects.all()
    voting_data = VotingData.objects.filter(is_active=True)

    if request.user.group:
        users = users.filter(group=group)
        validating_data = validating_data.filter(group=group)
        voting_data = voting_data.filter(group=group)
    Assignment.objects.filter(done=False).delete()
    assign(users, Assignment, validating_data, Data)
    assign(users, Assignment, voting_data, Data)

    messages.success(request, "Assign Tasks Succeed")
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

    messages.success(request, "Summarize Succeed")
    return HttpResponseRedirect(get_pre_url(request))
