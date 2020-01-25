from django.utils import timezone
from django.conf import settings

from assign.models import Assignment
from authentication.utils import get_group_report
from authentication.models import Log as auth_log
from pages.models import ValidatingData, VotingData, Choice, FinalizedData, CustomGroup, Log as data_log


def get_assigned_tasks_context(user):
    data = [i.task for i in Assignment.objects.all().filter(tasker_id=user.id, done=False)]

    validating_data = []
    voting_data = []
    for d in data:
        try:
            validating_d = ValidatingData.objects.get(pk=d)
            validating_data.append(validating_d)
        except ValidatingData.DoesNotExist:
            voting_d = VotingData.objects.get(pk=d)
            voting_data.append(voting_d)

    for data in voting_data:
        data.answers = Choice.objects.filter(data_id=data.id)

    context = {
        'question_list_validating': validating_data,
        'question_list_voting': voting_data,
    }
    return context


def get_profile_context(user):
    context = {
        'title': "Profile",
    }
    return context


def compute_group_point():
    groups = CustomGroup.objects.all()

    names = []
    points = []
    num_ans = []
    accuracy = []
    for group in groups:
        names.append(group.name)
        group_dict = get_group_report(group)
        points.append(group_dict["point"])
        num_ans.append(group_dict["num_ans"])
        accuracy.append(group_dict["accuracy"])

    context = {
        'names': names,
        'points': points,
        'num_ans': num_ans,
        'accuracy': accuracy,
    }
    return context


def get_finalized_data(group_name):
    finalized_data = FinalizedData.objects.all()
    if group_name and group_name != "all":
        group = CustomGroup.objects.get(name=group_name)
        finalized_data = finalized_data.filter(group=group)
    return finalized_data


def data_log(user, task, action, response):
    data_log.objects.update_or_create(user=user, task=task, action=action,
                                 response=response, timestamp=timezone.now())


def account_log(admin, action, account, msg=""):
    auth_log.objects.update_or_create(admin=admin, action=action, account=account, extra_msg=msg, timestamp=timezone.now())


def get_unassigned_voting_data(group):
    # get all VotingData ids that are not allocated to any user
    voting_data = VotingData.objects.all()
    if group:
        voting_data = voting_data.filter(group=group)
    voting_ids = [i.id for i in voting_data]

    exclude_ids = [i.task.id for i in Assignment.objects.all()]

    if settings.DEBUG:
        exclude_ids = []
    for exclude_id in exclude_ids:
        if exclude_id in voting_ids:
            voting_ids.remove(exclude_id)

    # get all VotingData objects and combine them with their respective choices
    voting_data = []
    for voting_id in voting_ids:
        voting_data.append(VotingData.objects.get(id=voting_id))
    for data in voting_data:
        data.answers = Choice.objects.filter(data_id=data.id)

    return voting_data


def get_data_log_msg(log):
    return {
        "logger": "{}({})".format(log.user.username, log.user.certifacate),
        "timestamp": log.timestamp,
        "msg": "{} {} with response {}".format(log.action, log.task_id, log.response)
    }


def get_auth_log_msg(log):
    return {
        "logger": "{}({})".format(log.admin.username, log.admin.certificate),
        "timestamp": log.timestamp,
        "msg": "{} {}({})".format(log.get_action_display(), log.account.username, log.account.certificate),
        "extra": log.extra_msg,
    }
