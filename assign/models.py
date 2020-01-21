from django.contrib.auth import get_user_model
from django.db import models


class Assignment(models.Model):
    tasker = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name="tasker_id")
    task = models.ForeignKey('pages.data', on_delete=models.CASCADE, verbose_name="task_id")
    done = models.BooleanField(default=False)

    def done(self):
        self.done = True
        self.save()
