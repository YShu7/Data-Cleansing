from math import floor
import random


def assign(UserModel, TaskModel, AssignModel, PREDEFINED_MAX):
    AssignModel.objects.all().delete()

    all_taskers = UserModel.objects.all().filter(is_active=True, is_superuser=False)
    num_taskers = all_taskers.count()
    num_tasks = TaskModel.objects.count()
    num_tasks_per_user = min(PREDEFINED_MAX, floor(num_tasks/num_taskers))
    print(num_tasks_per_user)

    random_tasks = [i for i in TaskModel.objects.all()]
    random.shuffle(random_tasks)
    for i, tasker in enumerate(all_taskers):
        for j in range(i*num_tasks_per_user, (i+1)*num_tasks_per_user):
            AssignModel.objects.update_or_create(tasker=tasker, task=random_tasks[j])