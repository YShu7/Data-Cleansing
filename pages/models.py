from django.db import models
from django.contrib.auth import get_user_model
from authentication.models import CustomGroup
from assign.models import Assignment


class Data(models.Model):
    title = models.CharField(max_length=200, blank=False, unique=True)
    group = models.ForeignKey(CustomGroup, on_delete=models.DO_NOTHING, blank=False)

    class Meta:
        abstract=True


class FinalizedData(Data):
    answer_text = models.TextField()

    @classmethod
    def create(cls, title, group, ans):
        data = cls(title=title, answer_text=ans, group=group)
        data.save()
        return data


class TaskData(Data):
    pass

    def __str__(self):
        return "ID: {}, Q: {}, G: {}".format(self.id, self.title, self.group.name)

    @classmethod
    def create(cls, title, group):
        data = cls(title=title, group=group)
        return data


class ValidatingData(TaskData):
    answer_text = models.TextField()
    num_approved = models.IntegerField(default=0)
    num_disapproved = models.IntegerField(default=0)

    def __str__(self):
        return "Q: {}, A: {}, T: {}, N: {}/{}".format(self.taskdata_ptr.title, self.answer_text, self.taskdata_ptr.group,
                                                      self.num_approved, self.num_disapproved)

    @classmethod
    def create(cls, data, ans, num_app=0, num_dis=0):
        validating_data = cls(title=data.title, group= data.group, answer_text=ans, num_approved=num_app, num_disapproved=num_dis)
        validating_data.save()
        return validating_data

    @classmethod
    def create_data(cls, title, group, ans, num_app, num_dis=0):
        validating_data = cls(title=title, group=group, answer_text=ans, num_approved=num_app,
                              num_disapproved=num_dis)
        validating_data.save()
        return validating_data


class VotingData(TaskData):
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return "Q: {}, T: {}".format(self.taskdata_ptr.title, self.taskdata_ptr.group)

    @classmethod
    def create(cls, data, is_active):
        voting_data = cls(title=data.title, group=data.group, is_active=is_active)
        voting_data.save()
        return voting_data

    @classmethod
    def create_data(cls, title, group, is_active):
        voting_data = cls(title=title, group=group, is_active=is_active)
        voting_data.save()
        return voting_data


class Choice(models.Model):
    data = models.ForeignKey(VotingData, models.CASCADE)
    answer = models.TextField()
    num_votes = models.IntegerField(default=0)

    def __str__(self):
        return "ID: {}, A: {}, N: {}".format(self.data, self.answer, self.num_votes)

    @classmethod
    def create(cls, data, ans, num_votes):
        data = cls(data=data, answer=ans, num_votes=num_votes)
        data.save()
        return data


class Log(models.Model):
    user = models.ForeignKey(get_user_model(), models.DO_NOTHING)
    task = models.ForeignKey(Assignment, models.DO_NOTHING)
    action = models.CharField(max_length=32)
    response = models.TextField()
    timestamp = models.DateTimeField()
    checked = models.BooleanField(default=False)