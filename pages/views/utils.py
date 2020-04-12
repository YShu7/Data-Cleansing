from django.conf import settings
from django.core.paginator import Paginator
from django.utils import timezone

from assign.models import Assignment
from authentication.utils import get_group_report
from pages.models.models import FinalizedData, CustomGroup, Data, Log as DataLog
from pages.models.vote import VotingData


def get_assigned_tasks_context(user, model, condition=(lambda x: True)):
    all_data_todo = [i.task for i in Assignment.objects.all().filter(tasker_id=user.id, done=False)]
    all_data_done = [i.task for i in Assignment.objects.all().filter(tasker_id=user.id, done=True)]

    todo_num = len(all_data_todo)
    done_num = len(all_data_done)

    data = []
    for d in all_data_todo:
        try:
            d_obj = model.objects.get(pk=d)
            if condition(d_obj):
                data.append(d_obj)
            else:
                todo_num -= 1
        except model.DoesNotExist:
            todo_num -= 1

    for d in all_data_done:
        try:
            d_obj = model.objects.get(pk=d)
            if condition(d_obj):
                pass
            else:
                done_num -= 1
        except model.DoesNotExist:
            done_num -= 1

    total_num = todo_num + done_num
    num = {
        'todo': todo_num,
        'done': done_num,
        'total': total_num,
    }
    return data, num


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


def get_finalized_data(group_name=None):
    finalized_data = FinalizedData.objects.all()
    if group_name and group_name != "all":
        group = CustomGroup.objects.get(name=group_name)
        finalized_data = finalized_data.filter(group=group)
    return finalized_data


def log(user, task, action, response):
    DataLog.objects.update_or_create(user=user, task=Data.objects.get(id=task.id), action=action,
                                     response=response, timestamp=timezone.now())


def get_controversial_voting_data(group=None, search_term=None):
    if group:
        voting_data = VotingData.objects.filter(num_votes__gt=15, group=group)
    if search_term:
        voting_data = VotingData.objects.filter(num_votes__gt=15, title__icontains=search_term)
    if group is None and search_term is None:
        voting_data = VotingData.objects.filter(num_votes__gt=15)

    # get all VotingData objects and combine them with their respective choices
    voting_data_list = []
    for data in voting_data:
        voting_data_list.append(data)
        data.answers = data.choice_set.all()

    return voting_data_list


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


def get_num_per_group_dict(model, condition=lambda x: x is not None):
    group_values = [x.group.id for x in model.objects.all() if condition and x.group is not None]
    group_keys = [group.id for group in CustomGroup.objects.all()]
    num_per_groups_dict = dict.fromkeys(group_keys, 0)
    for grp in group_values:
        num_per_groups_dict[grp] += 1
    return num_per_groups_dict


def get_group_info_context(groups, info_dict):
    groups_info = []
    for grp in groups:
        group_info = {'name': grp.name, 'created_at': grp.created_at, 'updated_at': grp.updated_at}
        for k in info_dict:
            v = 0
            if grp.id in info_dict[k]:
                v = info_dict[k][grp.id]

            group_info[k] = v
        groups_info.append(group_info)
    return groups_info


def merge_validate_context(new_data, old_data):
    if 'validate_ids' in old_data:
        if isinstance(old_data['validate_ids'], list):
            validate_ids = old_data['validate_ids']
        else:
            validate_ids = old_data['validate_ids'].split(',')
    else:
        validate_ids = []

    if 'validate_ids' in new_data:
        validate_ids.extend(new_data['validate_ids'].split(','))

    for k in new_data:
        old_data[k] = new_data[k]
    new_data = old_data

    new_data['validate_ids'] = get_ids(validate_ids)

    return new_data


def get_ids(validate_ids):
    if not isinstance(validate_ids, list):
        validate_ids = validate_ids.split(',')

    id_set = set(validate_ids)
    id_list = []
    for idx in id_set:
        if isinstance(idx, int) or idx.isdigit():
            id_list.append(idx)
    return id_list


def done_assignment(task_id, tasker_id):
    try:
        assign = Assignment.objects.get(task_id=task_id, tasker_id=tasker_id)
        assign.is_done()
    except Assignment.DoesNotExist:
        pass


def compute_paginator(request, data, num_done=0, num_doing=0, total=None):
    paginator = Paginator(data, 1)
    page_num = request.GET.get('page')
    try:
        if page_num is None:
            page_num = 1
        else:
            page_num = int(page_num)
    except ValueError:
        page_num = 1

    if not total or num_done + num_doing + 1 <= page_num:
        pass
    else:
        page_num = page_num + num_done
    page_obj = paginator.get_page(page_num)
    return page_obj


def compute_progress(request):
    try:
        return len(get_ids(request.session['data']['validate_ids']))
    except Exception:
        return 0
