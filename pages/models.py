from django.db import models
from django.contrib.auth import get_user_model


class Type(models.Model):
    type = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.type


class Data(models.Model):
    question_text = models.CharField(max_length=200)
    answer_text = models.TextField()
    type = models.ForeignKey(Type, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "Q: {}, A: {}, T: {}".format(self.question_text, self.answer_text, self.type)

    @classmethod
    def create(cls, qns, ans, type):
        data = cls(question=qns, answer_text=ans,type=type)
        return data


class TaskData(models.Model):
    question_text = models.CharField(max_length=200, unique=True, null=False)


class ValidatingData(models.Model):
    question = models.ForeignKey(TaskData, related_name='validating_question', on_delete=models.CASCADE, primary_key=True)
    answer_text = models.TextField()
    num_approved = models.IntegerField(default=0)
    num_disapproved = models.IntegerField(default=0)
    type = models.ForeignKey(Type, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "Q: {}, A: {}, T: {}, N: {}/{}".format(self.question.question_text, self.answer_text, self.type,
                                                      self.num_approved, self.num_disapproved)

    @classmethod
    def create(cls, qns, ans, type, num_app, num_dis):
        data = cls(question=qns, answer_text=ans,type=type, num_approved=num_app, num_disapproved=num_dis)
        return data


class VotingData(models.Model):
    question = models.ForeignKey(TaskData, related_name='voting_question', on_delete=models.CASCADE, primary_key=True)
    type = models.ForeignKey(Type, on_delete=models.SET_NULL, null=True)
    activate = models.BooleanField(default=False)

    def __str__(self):
        return "Q: {}, T: {}".format(self.question.question_text, self.type)

    @classmethod
    def create(cls, qns, type):
        data = cls(question=qns, type=type)
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

from assign.models import Assignment
class Log(models.Model):
    user = models.ForeignKey(get_user_model(), models.DO_NOTHING)
    task = models.ForeignKey(Assignment, models.DO_NOTHING)
    status = models.CharField(max_length=32)