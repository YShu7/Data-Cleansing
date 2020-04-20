from django.db import models
from django.contrib.auth import get_user_model
from math import ceil

from assign.models import Assignment
from pages.models.models import Data, FinalizedData


class VotingData(Data):
    """
    Incorrect data whose answer needs to be updated.
    """
    data_ptr = models.OneToOneField(to=Data, on_delete=models.CASCADE, parent_link=True)
    is_active = models.BooleanField(default=False)
    is_contro = models.BooleanField(default=False)
    num_votes = models.IntegerField(default=0)

    @classmethod
    def create(cls, title, group, is_active=False):
        try:
            data = Data.objects.get(title=title, group=group)
            voting_data = cls(pk=data.id, title=title, group=group, is_active=is_active)
        except Data.DoesNotExist:
            voting_data = cls(title=title, group=group, is_active=is_active)
        voting_data.save()
        return voting_data

    def vote(self, selected_choice):
        # update num of votes of the selected choice
        num_votes = selected_choice.vote()

        # get the number of choices that have been made for this question
        choices = self.choice_set.all()

        # if enough users have made responses to this question and this choice has more than half of the votes,
        # this question is done
        reassigned = True
        if num_votes >= 5 and num_votes <= 15:
            for c in choices:
                if c.num_votes >= ceil(num_votes / 2.0):
                    FinalizedData.create(title=self.data_ptr.title, ans=c.answer, group=self.group)
                    self.delete(keep_parents=True)
                    return
            reassigned = Assignment.reassign(self, get_user_model().objects.all())

        if num_votes > 15 or not reassigned:
            self.is_contro = True
            self.save()
            self.assignment_set.all().delete()

    def activate(self, is_active=True):
        self.is_active = is_active
        self.save()


class Choice(models.Model):
    data = models.ForeignKey(VotingData, models.CASCADE)
    answer = models.TextField(blank=False, null=False)
    num_votes = models.IntegerField(default=0)

    def vote(self):
        self.num_votes += 1
        self.save()
        self.data.num_votes += 1
        self.data.save()
        return self.data.num_votes
