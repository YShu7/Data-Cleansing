from django.contrib.auth import get_user_model
from django.db import models

from authentication.models import CustomGroup


class Data(models.Model):
    title = models.CharField(max_length=200, blank=False)
    group = models.ForeignKey(CustomGroup, on_delete=models.CASCADE, blank=False)

    class Meta:
        unique_together = ("title", "group")


class FinalizedData(Data):
    """
    Checked data whose question and answer are confirmed to be correct.
    Keywords are required to improve the training accuracy.
    """
    answer_text = models.TextField(blank=False, null=False)
    qns_keywords = models.TextField(blank=False, null=False, default="")
    ans_keywords = models.TextField(blank=False, null=False, default="")

    @classmethod
    def create(cls, title, group, ans):
        try:
            data = Data.objects.get(title=title, group=group)
            finalized_data = cls(pk=data.id, answer_text=ans, title=title, group=group)
        except Data.DoesNotExist:
            finalized_data = cls(title=title, answer_text=ans, group=group)
        finalized_data.save()
        return finalized_data

    def update_keywords(self, qns, ans):
        self.qns_keywords = self.qns_keywords + qns
        self.ans_keywords = self.ans_keywords + ans
        self.save()

    def get_keywords(self):
        context = {
            "qns": self.qns_keywords.split(","),
            "ans": self.ans_keywords.split(","),
        }
        return context


class Log(models.Model):
    user = models.ForeignKey(get_user_model(), models.CASCADE, related_name="data_log")
    task = models.ForeignKey(Data, models.CASCADE)
    action = models.CharField(max_length=32)
    response = models.TextField()
    timestamp = models.DateTimeField()
    checked = models.BooleanField(default=False)
