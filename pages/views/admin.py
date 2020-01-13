from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from pages.views.helper import *
from authentication.models import *
from assign.views import assign
import csv
import time
import datetime
import json
from django.contrib import messages

ADMIN_DIR = 'pages/admin'
USER_DIR = 'pages/user'
AUTH_DIR = 'authentication'

MSG_SUCCESS = "User registration succeed"
MSG_FAIL_EMAIL = "Email {} has been used"
MSG_FAIL_CERTI = "Certificate {} has been used"
MSG_FAIL_FILL = "Please fill in all fields."


@login_required
def index(request):
    """A view that provides necessary input fields for registering new users."""
    user = request.user
    if user is not None:
        if user.is_superuser:
            template = loader.get_template('{}/admin.html'.format(ADMIN_DIR))

            context = {
                'specs': Specialization.objects.all(),
                'groups': CustomGroup.objects.all(),
                'login_user': request.user,
            }

            # deal with messages passed from the previous page
            obj = request.session.pop('obj', False)
            if obj:
                context['obj'] = obj

            success = request.session.pop('success', False)
            if success:
                messages.success(request, success)

            fail = request.session.pop('error', False)
            if fail:
                messages.add_message(request, messages.ERROR, message=fail, extra_tags="danger")

            return HttpResponse(template.render(context=context, request=request))
        else:
            return HttpResponseRedirect('/')
    else:
        template = loader.get_template('{}/login.html'.format(AUTH_DIR))
        context = {
            'title': 'Log In',
            'error': "Invalid Log In"
        }
    return HttpResponse(template.render(context))


@login_required
@csrf_exempt
def add_user(request):
    """A view that tries to create new user with POST data and pass messages to the next page with session."""
    if request.method == "POST":
        username = request.POST["username"]
        certificate = request.POST["certificate"]
        email = request.POST["email"]
        group = CustomGroup.objects.get(id=request.POST["group"])

        # if any of the necessary fields is empty, return error message
        if not username or not certificate or not email or not group:
            request.session['error'] = MSG_FAIL_FILL
            request.session['obj'] = request.POST
            return HttpResponseRedirect('/')

        user = None
        try:
            # if a user with the same email has been created
            user = CustomUser.objects.get(email=email)
            request.session['error'] = MSG_FAIL_EMAIL.format(email)
        except Exception:
            pass

        try:
            # if a user with the same certificate has been created
            user = CustomUser.objects.get(certificate=certificate)
            request.session['error'] = MSG_FAIL_CERTI.format(certificate)
        except Exception:
            pass

        if user:
            request.session['obj'] = request.POST
            return HttpResponseRedirect('/')
        else:
            CustomUser.objects.create_user(email=email, certificate=certificate, username=username,
                                           group=group, password="123456")
            request.session['success'] = MSG_SUCCESS
            return HttpResponseRedirect('/')
    else:
        return HttpResponse("Request method is not allowed.")


@login_required
def dataset(request):
    template = loader.get_template('{}/dataset.html'.format(ADMIN_DIR))

    # get all VotingData ids that are not allocated to any user
    ids = [i.id for i in VotingData.objects.all()]
    exclude_ids = [i.task.id for i in Assignment.objects.all()]
    for exclude_id in exclude_ids:
        ids.remove(exclude_id)

    # get all VotingData objects and combine them with their respective choices
    voting_data = []
    for id in ids:
        voting_data.append(VotingData.objects.get(id=id))
    for data in voting_data:
        data.answers = Choice.objects.filter(data_id=data.id)

    # calculate num of data of each type
    types = Type.objects.all()
    num_data = {}
    num_data["all"] = Data.objects.all().count()
    for type in types:
        num_data[type.type] = Data.objects.all().filter(type=type).count()

    context = {
        'title': 'Data Set',
        'num_data': num_data,
        'data': voting_data,
        'types': types,
        'login_user': request.user,
    }
    return HttpResponse(template.render(context=context))


@login_required
def download_dataset(request):
    """A view that streams a large CSV file."""
    # Generate a sequence of rows. The range is based on the maximum number of
    # rows that can be handled by a single sheet in most spreadsheet
    # applications.
    rows = ([data.id, data.question_text, data.answer_text, data.type] for data in Data.objects.all())
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                     content_type="text/csv")
    filename = "{}.csv".format(time.time())
    response['Content-Disposition'] = 'attachment; filename=' + filename
    return response

@login_required
@csrf_exempt
def update(request, question_id):
    if request.method == 'POST':
        # update VotingData to Data directly
        data = VotingData.objects.get(id=question_id)
        ans = request.POST["choice"]
        Data.objects.update_or_create(question_text=data.question_text, answer_text=ans, type=data.type)
        data.delete()
    else:
        HttpResponse("Request method is not allowed.")
    return HttpResponseRedirect("/dataset")


@login_required
def report(request):
    template = loader.get_template('{}/report.html'.format(ADMIN_DIR))
    i = datetime.datetime.now()
    users = CustomUser.objects.all()
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


def download_report(request):
    """A view that streams a large CSV file."""
    rows = ([data.id, data.question_text, data.answer_text, data.type] for data in Data.objects.all())
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


def assign_tasks(request):
    assign(CustomUser, Assignment, 10, ValidatingData, TaskData)
    assign(CustomUser, Assignment, 10, VotingData, TaskData)
    return HttpResponse("Assign Tasks Succeed")


def summarize(request):
    users = get_user_model().objects.all()
    logs = Log.objects.all().filter(checked=False)
    for user in users:
        user_logs = logs.filter(tasker=user)
        for user_log in user_logs:
            user_response = user_log.response
            data = Data.objects.filter(question_text=user_log.task.task.question_data)
            if data and user_response == data.answer_text:
                user.ans_is(True)
            else:
                user.ans_is(False)