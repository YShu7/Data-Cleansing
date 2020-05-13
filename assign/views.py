import random
import sys
from math import floor

from pages.models.models import Data

PREDEFINED_MAX = sys.maxsize
NUM_USER_PER_TASK = 3


def assign(all_users, AssignModel, all_tasks, TaskModel=Data, num_task_per_user=PREDEFINED_MAX, num_user_per_task=NUM_USER_PER_TASK):
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
    num_loop = min(num_task_per_user, floor(num_tasks * num_user_per_task / num_users))

    if num_tasks == 0:
        return

    tasks = [i for i in all_tasks]
    random_tasks = []
    for _ in range(num_user_per_task):
        random_tasks += tasks

    for user in all_users:
        for _ in range(num_loop):
            task = random.choice(random_tasks)
            if AssignModel.objects.filter(tasker=user, task=task).count() == 0:
                AssignModel.objects.create(tasker=user, task=task, done=False)
                random_tasks.remove(task)
