from pages.models import *
from authentication.models import *
from assign.models import AssignmentVote, AssignmentValidate


def get_tasks_context(user):
    validating_data = [i.task for i in AssignmentValidate.objects.all().filter(tasker_id=user.id, done=False)]

    voting_data = [i.task for i in AssignmentVote.objects.all().filter(tasker_id=user.id, done=False)]

    for data in voting_data:
        data.answers = Choice.objects.filter(data_id=data.id)

    context = {
        'question_list_validating': validating_data,
        'question_list_voting': voting_data,
        'login_user': user,
        'title': 'Tasks'
    }
    return context


def get_profile_context(user):
    context = {
        'user': user
    }
    return context


def comupte_group_point(users):
    groups = CustomGroup.objects.all()

    name = []
    name_idx = [0]
    curr_idx = 0
    for group in groups:
        name.append(group.name)
        curr_idx += len(group.name)
        name_idx.append(curr_idx)
    context = {
        'names': name,
        'names_idx': name_idx,
    }
    return context