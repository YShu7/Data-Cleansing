from pages.models import *
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