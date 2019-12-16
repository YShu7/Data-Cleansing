from django.db import models


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
        data = cls(question_text=qns, answer_text=ans,type=type)
        return data


class VotingData(models.Model):
    question_text = models.CharField(max_length=200)
    type = models.ForeignKey(Type, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "Q: {}, T: {}".format(self.question_text, self.type)

    @classmethod
    def create(cls, qns, type):
        data = cls(question_text=qns, type=type)
        return data


class Choice(models.Model):
    data = models.ForeignKey(VotingData, models.CASCADE)
    answer = models.TextField()
    num_votes = models.IntegerField()

    def __str__(self):
        return "ID: {}, A: {}, N: {}".format(self.data, self.answer, self.num_votes)

    @classmethod
    def create(cls, data, ans, num_votes):
        data = cls(data=data, answer=ans, num_votes=num_votes)
        return data