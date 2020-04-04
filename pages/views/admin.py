import csv
import io
import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.template import loader
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect

from assign.models import Assignment
from assign.views import assign
from authentication.forms import CreateGroupForm
from authentication.models import CustomGroup, Log as AuthLog
from authentication.utils import get_approved_users, get_pending_users, \
    log as account_log, get_log_msg as get_auth_log_msg
from datacleansing.settings import ADMIN_DIR, MSG_SUCCESS_VOTE, MSG_SUCCESS_ASSIGN, MSG_SUCCESS_SUM, \
    MSG_FAIL_DEL_GRP, MSG_SUCCESS_DEL_GRP, MSG_SUCCESS_CRT_GRP, MSG_SUCCESS_IMPORT
from datacleansing.utils import get_pre_url, Echo
from pages.decorators import superuser_admin_login_required, admin_login_required, superuser_login_required
from pages.models.models import Data, FinalizedData, Log
from pages.models.validate import ValidatingData
from pages.models.vote import VotingData
from pages.views.utils import get_unassigned_voting_data, get_finalized_data, get_group_report_context, \
    get_log_msg as get_data_log_msg, get_admin_logs, get_num_per_group_dict, get_group_info_context


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
        return HttpResponseRedirect(reverse('modify_users'))
    else:
        template = loader.get_template('{}/modify_users.html'.format(ADMIN_DIR))
        user = request.user
        pending_users = get_pending_users(getattr(user, 'group'))
        approved_users = get_approved_users(getattr(user, 'group'))

        context = {
            'title': _('Users'),
            'pending_users': pending_users,
            'approved_users': approved_users,
        }
        return HttpResponse(template.render(context=context, request=request))


@superuser_admin_login_required
def dataset(request, group_name="all"):
    template = loader.get_template('{}/dataset.html'.format(ADMIN_DIR))

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
        'title': _('Data Set'),
        'num_data': num_data,
        'page_obj': page_obj,
        'groups': groups,
        'group_name': _(group_name),
    }
    return HttpResponse(template.render(request=request, context=context))


@superuser_admin_login_required
def download_dataset(_, group_name=""):
    """A view that streams a large CSV file."""
    # Generate a sequence of rows. The range is based on the maximum number of
    # rows that can be handled by a single sheet in most spreadsheet
    # applications.
    finalized_data = get_finalized_data(group_name)

    rows = [["id", "question", "qns_keywords", "answer", "ans_keywords"]]
    rows += ([data.id, data.title, data.get_keywords()["qns"],
              data.answer_text, data.get_keywords()["ans"]] for data in finalized_data)
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

        # Retrieve data
        search_term = None
        if 'search' in request.GET:
            search_term = request.GET['search']
        voting_data = get_unassigned_voting_data(getattr(request.user, 'group'), search_term)

        # Initiate paginator
        paginator = Paginator(voting_data, 25)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'title': _('Data Set'),
            'page_obj': page_obj,
            'data': VotingData.objects.all(),
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
    users = get_approved_users(getattr(request.user, 'group'), )

    context = {
        'title': _('Report'),
        'today': '{}-{}-{}'.format('%04d' % i.year, '%02d' % i.month, '%02d' % i.day),
        'from_date': from_date,
        'to_date': to_date,
        'users': users,
    }

    if request.user.is_superuser:
        groups = get_group_report_context()
        context = {
            'title': _('Report'),
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
    rows = [[_("id"), _("username"), _("certificate"), _("point"), _("accuracy")]]
    rows += ([user.id, user.username, user.certificate, user.point, user.accuracy()] for user in
             get_approved_users(group=getattr(request.user, 'group')))
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
    logs = get_admin_logs(request.user, Log.objects.all(), get_data_log_msg, 'user')
    data_logs = get_admin_logs(request.user, AuthLog.objects.all(), get_auth_log_msg, 'admin')
    logs.extend(data_logs)
    context = {
        'title': _("Admin Log"),
        'logs': logs,
    }
    return HttpResponse(template.render(context=context, request=request))


@admin_login_required
def import_dataset(request):
    # declaring template
    try:
        csv_file = request.FILES['file']
    except KeyError:
        messages.add_message(request, messages.ERROR, _('No file is input.'), extra_tags="danger")
        return HttpResponseRedirect(get_pre_url(request))
    try:
        qns_col = int(request.POST['qns_col'])
        ans_col = int(request.POST['ans_col'])
    except KeyError:
        messages.add_message(request, messages.ERROR, _('No column index is input.'), extra_tags="danger")
        return HttpResponseRedirect(get_pre_url(request))

    # let's check if it is a csv file
    if not csv_file.name.endswith('.csv'):
        messages.add_message(request, messages.ERROR, _('Input file is not a .csv file.'), extra_tags="danger")
        return HttpResponseRedirect(get_pre_url(request))
    data_set = csv_file.read().decode('UTF-8')
    # setup a stream which is when we loop through each line we are able to handle a data in a stream

    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string):
        ValidatingData.create(
            title=column[qns_col],
            ans=column[ans_col],
            group=request.user.group,
        )
    messages.success(request, MSG_SUCCESS_IMPORT)
    return HttpResponseRedirect(get_pre_url(request))


@admin_login_required
def assign_tasks(request):
    grp = getattr(request.user, 'group')
    users = get_user_model().objects.filter(is_active=True, is_approved=True, is_admin=False, group=grp)
    validating_data = ValidatingData.objects.filter(group=grp)
    voting_data = VotingData.objects.filter(is_active=True, group=grp, num_votes__lte=15)

    Assignment.objects.all().delete()
    assign(users, Assignment, validating_data, Data)
    assign(users, Assignment, voting_data, Data)

    messages.success(request, MSG_SUCCESS_ASSIGN)
    return HttpResponseRedirect(get_pre_url(request))


@admin_login_required
def summarize(request):
    users = get_approved_users(getattr(request.user, 'group'))
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
            except FinalizedData.DoesNotExist:
                pass

    messages.success(request, MSG_SUCCESS_SUM)
    return HttpResponseRedirect(get_pre_url(request))


@superuser_login_required
def group(request):
    template = loader.get_template('{}/group.html'.format(ADMIN_DIR))

    user_per_groups_dict = get_num_per_group_dict(get_user_model())
    admin_per_groups_dict = get_num_per_group_dict(get_user_model(), condition={lambda x: x.is_admin})
    data_per_group_dict = get_num_per_group_dict(FinalizedData)
    groups_info = get_group_info_context(CustomGroup.objects.all(),
                                         {'user_num': user_per_groups_dict,
                                          'admin_num': admin_per_groups_dict,
                                          'data_num': data_per_group_dict})

    context = {
        'title': _('Groups'),
        'groups': groups_info,
        'delete_check_id': 'input',
        'delete_confirm_id': 'confirm_input',
        'create_form': CreateGroupForm(),
    }
    return HttpResponse(template.render(context=context, request=request))


@superuser_login_required
def group_details(request, group_name):
    template = loader.get_template('{}/group_details.html'.format(ADMIN_DIR))
    group = CustomGroup.objects.get(name=group_name)

    # Retrieve data
    finalized_data = get_finalized_data(group_name)

    # Initiate paginator
    paginator = Paginator(finalized_data, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': group_name,
        'pending_users': get_pending_users(group),
        'approved_users': get_approved_users(group),
        'page_obj': page_obj,
    }
    return HttpResponse(template.render(context=context, request=request))


@superuser_login_required
def delete_group(request):
    if request.method == "POST":
        group_name = request.POST["input"]
        if group_name == request.POST["confirm_input"]:
            CustomGroup.objects.get(name=group_name).delete()
            messages.success(request, MSG_SUCCESS_DEL_GRP.format(group_name))
        else:
            messages.add_message(request, level=messages.ERROR, extra_tags="danger", message=MSG_FAIL_DEL_GRP)
    url = get_pre_url(request)
    return HttpResponseRedirect('/' if url is None else url)


@superuser_login_required
def create_group(request):
    form_obj = CreateGroupForm(request.POST)
    if form_obj.is_valid():
        form_obj.save()
        messages.success(request, MSG_SUCCESS_CRT_GRP.format(form_obj.data.get('name')))
    else:
        error = ""
        for error in form_obj.errors:
            error = form_obj.errors[error][0]
            if error:
                break
        messages.add_message(request, level=messages.ERROR, extra_tags="danger", message=error)

    url = get_pre_url(request)
    return HttpResponseRedirect('/' if url is None else url)
