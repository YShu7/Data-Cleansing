import csv
import datetime
import json
import time

from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt

from assign.views import assign
from pages.views.helper import *
from pages.decorators import admin_login_required


ADMIN_DIR = 'pages/admin'
USER_DIR = 'pages/user'
AUTH_DIR = 'authentication'


@admin_login_required
def modify_users(request):
    if request.method == "POST":
        user = get_approved_users(request.user.group).get(id=request.POST["id"])
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
        if request.user.is_admin:
            template = loader.get_template('{}/admin.html'.format(ADMIN_DIR))

            context = {
                'pending_users': get_pending_users(request.user.group),
                'approved_users': get_approved_users(request.user.group),
                'login_user': request.user,
            }
            return HttpResponse(template.render(context=context, request=request))
        else:
            return HttpResponseRedirect('/')


@admin_login_required
def dataset(request):
    template = loader.get_template('{}/dataset.html'.format(ADMIN_DIR))

    # get all VotingData ids that are not allocated to any user
    ids = [i.id for i in VotingData.objects.filter(group=request.user.group)]
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

    # calculate num of data of each type

    finalized_data = FinalizedData.objects.filter(group=request.user.group)
    paginator = Paginator(finalized_data, 3)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    num_data = finalized_data.count()

    context = {
        'title': 'Data Set',
        'num_data': num_data,
        'page_obj': page_obj,
        'data': voting_data,
        'login_user': request.user,
    }
    return HttpResponse(template.render(context=context))


@admin_login_required
def download_dataset(request):
    """A view that streams a large CSV file."""
    # Generate a sequence of rows. The range is based on the maximum number of
    # rows that can be handled by a single sheet in most spreadsheet
    # applications.
    rows = [["id", "question", "answer"]]
    rows = ([data.id, data.title, data.answer_text] for data in FinalizedData.objects.all())
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                     content_type="text/csv")
    filename = "{}.csv".format(time.time())
    response['Content-Disposition'] = 'attachment; filename=' + filename
    return response


@admin_login_required
@csrf_exempt
def update(request, question_id):
    if request.method == 'POST':
        # update VotingData to Data directly
        data = VotingData.objects.get(question_id=question_id)
        ans = request.POST["choice"]
        Data.objects.update_or_create(question_text=data.question.question_text, answer_text=ans, type=data.type)
        data.delete()
    else:
        HttpResponse("Request method is not allowed.")
    return HttpResponseRedirect("/dataset")


@admin_login_required
def report(request):
    template = loader.get_template('{}/report.html'.format(ADMIN_DIR))
    i = datetime.datetime.now()
    users = get_approved_users(request.user.group)
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


@admin_login_required
def download_report(request):
    """A view that streams a large CSV file."""
    rows = [["id", "username", "certificate", "point", "accuracy"]]
    rows += ([user.id, user.username, user.certificate, user.point, user.accuracy()] for user in get_approved_users(request.user.group))
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                     content_type="text/csv")
    filename = "{}.csv".format(time.time())
    response['Content-Disposition'] = 'attachment; filename=' + filename
    return response


def log(request):
    template = loader.get_template('{}/log.html'.format(ADMIN_DIR))
    context = {
        'title': "Admin Log",
        'login_user': request.user,
        'logs': Log.objects.all(),
    }
    return HttpResponse(template.render(context=context))


@admin_login_required
def assign_tasks(request):
    users = get_user_model().objects.filter(is_active=True, is_approved=True, is_admin=False)
    assign(users, Assignment, ValidatingData.objects.all(), TaskData)
    assign(users, Assignment, VotingData.objects.filter(is_active=True), TaskData)
    return HttpResponse("Assign Tasks Succeed")


@admin_login_required
def summarize(request):
    users = get_approved_users(request.user.group)
    logs = Log.objects.all().filter(checked=False)
    for user in users:
        user_logs = logs.filter(user=user)
        for user_log in user_logs:
            user_response = user_log.response
            data = Data.objects.filter(question_text=user_log.task.task.question_text)
            if data and user_response == data.answer_text:
                user.ans_is(True)
            else:
                user.ans_is(False)
    return HttpResponse("Summarize Succeed")
