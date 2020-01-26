from django.utils import timezone
from django.conf import settings
from django.db.models import Count

from assign.models import Assignment
from authentication.utils import get_group_report
from pages.models import ValidatingData, VotingData, Choice, FinalizedData, CustomGroup, Log as DataLog


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


def get_group_report_context():
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


def log(user, task, action, response):
    DataLog.objects.update_or_create(user=user, task=task, action=action,
                                     response=response, timestamp=timezone.now())


def get_unassigned_voting_data(group, search_term=None):
    # get all VotingData ids that are not allocated to any user
    voting_data = VotingData.objects.all()
    if group:
        voting_data = voting_data.filter(group=group)
    if search_term:
        voting_data = voting_data.filter(title__icontains=search_term)
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


def get_log_msg(log_obj):
    return {
        "logger": "{}({})".format(log_obj.user.username, log_obj.user.certifacate),
        "timestamp": log_obj.timestamp,
        "msg": "{} {} with response {}".format(log_obj.action, log_obj.task_id, log_obj.response)
    }


def get_admin_logs(user, logs, func, logger):
    if user.is_superuser:
        return [func(this_log) for this_log in logs
                if getattr(this_log, logger).is_superuser or getattr(this_log, logger).is_admin]
    else:
        return [func(this_log) for this_log in logs
                if getattr(this_log, logger).is_admin and getattr(this_log, logger).group == user.group]


def get_num_per_group_dict(model):
    num_per_groups = model.objects.values('group').annotate(dcount=Count('group'))
    num_per_groups_dict = {}
    for num_per_group in num_per_groups:
        num_per_groups_dict[num_per_group['group']] = num_per_group['dcount']
    return num_per_groups_dict


def get_group_info_context(groups, info_dict):
    groups_info = []
    for grp in groups:
        group_info = {'name': grp.name}
        for k in info_dict:
            v = 0
            if grp.id in info_dict[k]:
                v = info_dict[k][grp.id]

            group_info[k] = v
        groups_info.append(group_info)
    return groups_info
