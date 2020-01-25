from django.utils import timezone

from assign.models import Assignment
from authentication.utils import get_group_report
from pages.models import ValidatingData, VotingData, Choice, FinalizedData, CustomGroup, Log


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
        'login_user': user,
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


def log(user, task, action, response):
    Log.objects.update_or_create(user=user, task=task, action=action,
                                 response=response, timestamp=timezone.now())


def get_unassigned_voting_data(group):
    # get all VotingData ids that are not allocated to any user
    voting_data = VotingData.objects.all()
    if group:
        voting_data = voting_data.filter(group=group)
    voting_ids = [i.id for i in voting_data]

    exclude_ids = [i.task.id for i in Assignment.objects.all()]
    for exclude_id in exclude_ids:
        if exclude_id in voting_ids:
            voting_ids.remove(exclude_id)

    # get all VotingData objects and combine them with their respective choices
    voting_data = []
    for voting_id in voting_ids:
        voting_data.append(VotingData.objects.get(id=voting_id))
    for data in voting_data:
        data.answers = Choice.objects.filter(data_id=data.id)
