from django.db import models
from authentication.models import CustomUser
from pages.models import VotingData, ValidatingData


class AssignmentValidate(models.Model):
    tasker = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="tasker_id")
    task = models.ForeignKey(ValidatingData, on_delete=models.CASCADE, verbose_name="task_id")
    done = models.BooleanField(default=False)


class AssignmentVote(models.Model):
    tasker = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="tasker_id")
    task = models.ForeignKey(VotingData, on_delete=models.CASCADE, verbose_name="task_id")
    done = models.BooleanField(default=False)
