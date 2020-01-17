from django.db import models
from django.contrib.auth import get_user_model
from authentication.models import CustomGroup
from assign.models import Assignment


class Data(models.Model):
    title = models.CharField(max_length=200)
    group = models.ForeignKey(CustomGroup, on_delete=models.SET_NULL, null=True)

    class Meta:
        abstract=True


class FinalizedData(Data):
    answer_text = models.TextField()


class TaskData(Data):
    pass


class ValidatingData(TaskData):
    answer_text = models.TextField()
    num_approved = models.IntegerField(default=0)
    num_disapproved = models.IntegerField(default=0)

    def __str__(self):
        return "Q: {}, A: {}, T: {}, N: {}/{}".format(self.parent.question_text, self.answer_text, self.parent.group,
                                                      self.num_approved, self.num_disapproved)

    @classmethod
    def create(cls, data, ans, num_app, num_dis):
        data = cls(parent=data, answer_text=ans, num_approved=num_app, num_disapproved=num_dis)
        return data


class VotingData(TaskData):
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return "Q: {}, T: {}".format(self.parent.question_text, self.parent.group)

    @classmethod
    def create(cls, data, is_active):
        data = cls(parent=data, is_active=is_active)
        return data


class Choice(models.Model):
    data = models.ForeignKey(VotingData, models.CASCADE)
    answer = models.TextField()
    num_votes = models.IntegerField(default=0)

    def __str__(self):
        return "ID: {}, A: {}, N: {}".format(self.data, self.answer, self.num_votes)

    @classmethod
    def create(cls, data, ans, num_votes):
        data = cls(data=data, answer=ans, num_votes=num_votes)
        return data


class Log(models.Model):
    user = models.ForeignKey(get_user_model(), models.DO_NOTHING)
    task = models.ForeignKey(Assignment, models.DO_NOTHING)
    action = models.CharField(max_length=32)
    response = models.TextField()
    timestamp = models.DateTimeField()
    checked = models.BooleanField(default=False)