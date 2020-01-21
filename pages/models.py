from django.db import models
from django.contrib.auth import get_user_model
from authentication.models import CustomGroup


class Data(models.Model):
    title = models.CharField(max_length=200, blank=False)
    group = models.ForeignKey(CustomGroup, on_delete=models.DO_NOTHING, blank=False)

    class Meta:
        unique_together = ("title", "group")


class FinalizedData(Data):
    answer_text = models.TextField(blank=False, null=False)

    @classmethod
    def create(cls, title, group, ans):
        try:
            data = Data.objects.get(title=title, group=group)
            finalized_data = cls(pk=data.id, answer_text=ans, title=title, group=group)
        except Exception:
            finalized_data = cls(title=title, answer_text=ans, group=group)
        finalized_data.save()
        return finalized_data


class ValidatingData(Data):
    answer_text = models.TextField(blank=False, null=False)
    num_approved = models.IntegerField(default=0)
    num_disapproved = models.IntegerField(default=0)

    def __str__(self):
        return "Q: {}, A: {}, T: {}, N: {}/{}".format(self.data_ptr.title, self.answer_text, self.data_ptr.group,
                                                      self.num_approved, self.num_disapproved)


    @classmethod
    def create(cls, title, group, ans, num_app=0, num_dis=0):
        try:
            data = Data.objects.get(title=title, group=group)
            validating_data = cls(pk=data.id, title=title, group=group, answer_text=ans, num_approved=num_app,
                                  num_disapproved=num_dis)
        except Exception:
            validating_data = cls(title=title, group=group, answer_text=ans, num_approved=num_app,
                                  num_disapproved=num_dis)
        validating_data.save()
        return validating_data


class VotingData(Data):
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return "Q: {}, T: {}".format(self.data_ptr.title, self.data_ptr.group)

    @classmethod
    def create(cls, title, group, is_active):
        try:
            data = Data.objects.filter(title=title, group=group)
            voting_data = cls(pk=data.id, title=title, group=group, is_active=is_active)
        except Exception:
            voting_data = cls(title=title, group=group, is_active=is_active)
        voting_data.save()
        return voting_data


class Choice(models.Model):
    data = models.ForeignKey(VotingData, models.CASCADE)
    answer = models.TextField(blank=False, null=False)
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
    task = models.ForeignKey(Data, models.DO_NOTHING)
    action = models.CharField(max_length=32)
    response = models.TextField()
    timestamp = models.DateTimeField()
    checked = models.BooleanField(default=False)
