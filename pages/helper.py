from .models import *


def get_tasks_context(user):
    voting_data = VotingData.objects.all().filter(activate=True)
    for data in voting_data:
        data.answers = Choice.objects.filter(data_id=data.id)
    context = {
        'question_list_validating': ValidatingData.objects.all(),
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