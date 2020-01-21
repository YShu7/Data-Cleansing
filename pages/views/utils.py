from authentication.utils import *
from pages.models import *
from assign.models import Assignment

from django.utils import timezone


def get_assigned_tasks_context(user):
    data = [i.task for i in Assignment.objects.all().filter(tasker_id=user.id, done=False)]

    validating_data = []
    voting_data = []
    for d in data:
        try:
            validating_d = ValidatingData.objects.get(pk=d)
            validating_data.append(validating_d)
        except:
            voting_d = VotingData.objects.get(pk=d)
            voting_data.append(voting_d)

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
        'title': "Profile",
        'login_user': user,
    }
    return context


def compute_group_point():
    groups = CustomGroup.objects.all()

    names = []
    points = []
    num_ans = []
    accu = []
    for group in groups:
        names.append(group.name)
        dict = get_group_report(group)
        points.append(dict["point"])
        num_ans.append(dict["num_ans"])
        accu.append(dict["accuracy"])

    context = {
        'names': names,
        'points': points,
        'num_ans': num_ans,
        'accuracy': accu,
    }
    return context


def get_finalized_data(group_name):
    finalized_data = FinalizedData.objects.all()
    if group_name and group_name != "all":
        group = CustomGroup.objects.get(name=group_name)
        finalized_data = finalized_data.filter(group=group)
    return finalized_data


def log(user, task, action, response):
    Log.objects.update_or_create(user=user, task=task, action=action,
                                 response=response, timestamp=timezone.now())