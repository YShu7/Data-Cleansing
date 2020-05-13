from django.contrib.auth import get_user_model
from django.db import models
import random

from pages.models.models import Data


class Assignment(models.Model):
    tasker = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name="tasker_id")
    task = models.ForeignKey(Data, on_delete=models.CASCADE, verbose_name="task_id")
    done = models.BooleanField(default=False)

    def is_done(self):
        self.done = True
        self.save()

    @classmethod
    def reassign(cls, task, all_users):
        assigned_taskers = [a.tasker for a in Assignment.objects.filter(task=task)]
        all_users = [user for user in all_users]

        target_new_users = 2
        num_new_users = 0
        while num_new_users != target_new_users and len(all_users) != 0:
            new_user = random.choice(all_users)
            all_users.remove(new_user)
            if new_user in assigned_taskers:
                continue
            else:
                new_assign = cls(tasker=new_user, task=task)
                new_assign.save()
                num_new_users += 1
        if num_new_users == 2:
            return True
        else:
            return False

    @classmethod
    def reassign_contro(cls, task, tasker):
        task.activate(False)
        task.assignment_set.all().delete()
        Assignment.objects.create(tasker=tasker, task=task)