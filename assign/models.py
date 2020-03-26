from django.contrib.auth import get_user_model
from django.db import models

from pages.models.models import Data


class Assignment(models.Model):
    tasker = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name="tasker_id")
    task = models.ForeignKey(Data, on_delete=models.CASCADE, verbose_name="task_id")
    done = models.BooleanField(default=False)

    def is_done(self):
        self.done = True
        self.save()

    def __str__(self):
        return "{} {} {}".format(self.tasker.pk, self.task.title, self.done)