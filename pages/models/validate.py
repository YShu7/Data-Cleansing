from django.db import models

from pages.models.models import Data, FinalizedData
from pages.models.vote import VotingData, Choice


class ValidatingData(Data):
    """
    Data that are waiting to be validated as correct or not.
    """
    data_ptr = models.OneToOneField(to=Data, on_delete=models.CASCADE, parent_link=True)
    answer_text = models.TextField(blank=False, null=False)
    num_approved = models.IntegerField(default=0)
    num_disapproved = models.IntegerField(default=0)

    @classmethod
    def create(cls, title, group, ans, num_app=0, num_dis=0):
        try:
            data = Data.objects.get(title=title, group=group)
            validating_data = cls(pk=data.id, title=title, group=group, answer_text=ans,
                                  num_approved=num_app, num_disapproved=num_dis)
        except Data.DoesNotExist:
            validating_data = cls(title=title, group=group, answer_text=ans,
                                  num_approved=num_app, num_disapproved=num_dis)
        validating_data.save()
        return validating_data

    def approve(self):
        self.num_approved += 1
        self.save()

    def disapprove(self, new_ans):
        self.num_disapproved += 1
        self.save()
        data = VotingData.create(title=self.title, group=self.group)
        Choice.objects.update_or_create(data=data, answer=new_ans)

    def validate(self):
        try:
            data = VotingData.objects.get(pk=self.id)
        except VotingData.DoesNotExist:
            return
        if self.num_approved >= 2:
            # if enough user has approve the answer
            # the origin answer is considered to be correct
            FinalizedData.create(title=self.data_ptr.title, group=self.data_ptr.group, ans=self.answer_text)
            data.choice_set.all().delete()
            self.delete(keep_parents=True)
            data.delete(keep_parents=True)
        elif self.num_disapproved >= 2:
            # if enough user has disapprove the answer
            # the better answer should be selected by activating VotingData
            data.activate()
            self.delete(keep_parents=True)
