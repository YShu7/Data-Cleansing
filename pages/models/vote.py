from django.db import models
from django.contrib.auth import get_user_model
from math import ceil

from pages.models.models import Data, FinalizedData


class VotingData(Data):
    """
    Incorrect data whose answer needs to be updated.
    """
    data_ptr = models.OneToOneField(to=Data, on_delete=models.CASCADE, parent_link=True)
    is_active = models.BooleanField(default=False)
    num_votes = models.IntegerField(default=0)

    def __str__(self):
        return "Q: {}, T: {}".format(self.data_ptr.title, self.data_ptr.group)

    @classmethod
    def create(cls, title, group, is_active=False):
        try:
            data = Data.objects.get(title=title, group=group)
            voting_data = cls(pk=data.id, title=title, group=group, is_active=is_active)
        except Data.DoesNotExist:
            voting_data = cls(title=title, group=group, is_active=is_active)
        voting_data.save()
        return voting_data

    def finalize(self, choice):
        FinalizedData.create(title=self.data_ptr.title, ans=choice.answer, group=self.group)
        self.delete(keep_parents=True)

    def vote(self, selected_choice):
        # update num of votes of the selected choice
        selected_choice.vote()
        self.num_votes += 1
        self.save()

        # get the number of choices that have been made for this question
        choices = self.choice_set.all()

        # if enough users have made responses to this question and this choice has more than half of the votes,
        # this question is done
        if self.num_votes >= 5 and self.num_votes <= 15:
            for c in choices:
                if c.num_votes > ceil(self.num_votes / 2.0):
                    self.finalize(self, choice=c)
                else:
                    self.assignment_set.first().reassign(self, get_user_model().objects.all())
        if self.num_votes > 15:
            self.assignment_set.all().delete()

    def activate(self):
        self.is_active = True
        self.save()


class Choice(models.Model):
    data = models.ForeignKey(VotingData, models.CASCADE)
    answer = models.TextField(blank=False, null=False)
    num_votes = models.IntegerField(default=0)

    def __str__(self):
        return "ID: {}, A: {}, N: {}".format(self.data, self.answer, self.num_votes)

    def vote(self):
        self.num_votes += 1
        self.save()
