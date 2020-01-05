from math import floor
import random


def assign(UserModel, AssignModel, PREDEFINED_MAX, SubTaskModel, TaskModel=None, ):
    AssignModel.objects.all().delete()

    all_taskers = UserModel.objects.all().filter(is_active=True, is_superuser=False)
    num_taskers = all_taskers.count()
    num_tasks = SubTaskModel.objects.count()
    num_tasks_per_user = min(PREDEFINED_MAX, floor(num_tasks/num_taskers))

    random_tasks = [i for i in SubTaskModel.objects.all()]
    random.shuffle(random_tasks)
    for i, tasker in enumerate(all_taskers):
        for j in range(i*num_tasks_per_user, (i+1)*num_tasks_per_user):
            if not TaskModel:
                AssignModel.objects.update_or_create(tasker=tasker, task=random_tasks[j])
            else:
                AssignModel.objects.update_or_create(tasker=tasker, task=TaskModel.objects.get(id=random_tasks[j].question.id))