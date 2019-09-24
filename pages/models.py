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