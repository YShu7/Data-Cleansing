from django.db import models

# Create your models here.
class Data(models.Model):
    question_text = models.CharField(max_length=200)
    answer_text = models.TextField()
    type_text = models.CharField(max_length=100)

    @classmethod
    def create(cls, qns, ans, type):
        data = cls(question_text=qns, answer_text=ans,type_text=type)
        # do something with the book
        return data

class VotingData(models.Model):
    question_text = models.CharField(max_length=200)
    answer_text_1 = models.TextField()
    answer_text_2 = models.TextField()
    answer_text_3 = models.TextField()
    type_text = models.CharField(max_length=100)

    @classmethod
    def create(cls, qns, ans1, ans2, ans3, type):
        data = cls(question_text=qns, answer_text_1=ans1, answer_text_2=ans2, answer_text_3=ans3,type_text=type)
        # do something with the book
        return data