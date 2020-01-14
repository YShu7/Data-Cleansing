from django.db import models
from authentication.models import CustomUser
from pages.models import VotingData, ValidatingData, TaskData


class Assignment(models.Model):
    tasker = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="tasker_id")
    task = models.ForeignKey(TaskData, on_delete=models.CASCADE, verbose_name="task_id")
    done = models.BooleanField(default=False)
