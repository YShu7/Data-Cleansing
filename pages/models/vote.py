from django.db import models
from pages.models.models import Data, FinalizedData


class VotingData(Data):
    """
    Incorrect data whose answer needs to be updated.
    """
    data_ptr = models.OneToOneField(to=Data, on_delete=models.CASCADE, parent_link=True)
    is_active = models.BooleanField(default=False)

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

    def vote(self, selected_choice):
        # update num of votes of the selected choice
        selected_choice.vote()

        # get the number of choices that have been made for this question
        choices = Choice.objects.filter(data_id=self.id)
        sum_votes = 0
        max_votes = selected_choice.num_votes
        for c in choices:
            sum_votes += c.num_votes
            max_votes = max(max_votes, c.num_votes)

        # if enough users have made responses to this question and this choice has the maximum num of votes,
        # this question is done
        if sum_votes >= 5 and selected_choice.num_votes == max_votes:
            FinalizedData.create(title=self.data_ptr.title, ans=selected_choice.answer, group=self.group)
            self.delete(keep_parents=True)


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

    def vote(self):
        self.num_votes += 1
        self.save()
