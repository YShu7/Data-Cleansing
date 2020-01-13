from pages.models import *
from authentication.models import *
from authentication.helper import *
from assign.models import Assignment


def get_tasks_context(user):
    validating_data = [i.task for i in Assignment.objects.all().filter(tasker_id=user.id, done=False)]

    voting_data = [i.task for i in Assignment.objects.all().filter(tasker_id=user.id, done=False)]

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


class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value