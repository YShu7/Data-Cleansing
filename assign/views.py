import random
import sys
from math import floor

from pages.models.models import Data


def assign(all_users, AssignModel, all_tasks, TaskModel=Data, PREDEFINED_MAX=sys.maxsize, NUM_USER_PER_TASK=3):
    try:
        num_users = all_users.count()
    except TypeError:
        num_users = len(all_users)

    if num_users == 0:
        return

    try:
        num_tasks = all_tasks.count()
    except TypeError:
        num_tasks = len(all_tasks)
    num_tasks_per_user = min(PREDEFINED_MAX, floor(num_tasks * NUM_USER_PER_TASK / num_users))

    tasks = [i for i in all_tasks]
    random_tasks = []
    for _ in range(NUM_USER_PER_TASK):
        random.shuffle(tasks)
        random_tasks += tasks

    for i, user in enumerate(all_users):
        for j in range(i * num_tasks_per_user, (i + 1) * num_tasks_per_user):
            if not TaskModel:
                AssignModel.objects.update_or_create(tasker=user, task=random_tasks[j], done=False)
            else:
                AssignModel.objects.update_or_create(tasker=user,
                                                     task=TaskModel.objects.get(id=random_tasks[j].data_ptr_id),
                                                     done=False)
