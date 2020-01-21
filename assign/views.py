from math import floor
import random
import sys


def assign(all_taskers, AssignModel, all_tasks, TaskModel=None, PREDEFINED_MAX=sys.maxsize, NUM_USER_PER_TASK=3):
    num_taskers = all_taskers.count()
    num_tasks = all_tasks.count()
    num_tasks_per_user = min(PREDEFINED_MAX, floor(num_tasks * NUM_USER_PER_TASK/num_taskers))

    tasks = [i for i in all_tasks]
    random_tasks = []
    for _ in range(NUM_USER_PER_TASK):
        random.shuffle(tasks)
        random_tasks += tasks

    for i, tasker in enumerate(all_taskers):
        for j in range(i*num_tasks_per_user, (i+1)*num_tasks_per_user):
            if not TaskModel:
                AssignModel.objects.update_or_create(tasker=tasker, task=random_tasks[j])
            else:
                AssignModel.objects.update_or_create(tasker=tasker, task=TaskModel.objects.get(id=random_tasks[j].data_ptr_id))