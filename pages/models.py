from django.contrib.auth import get_user_model
from django.db import models

from authentication.models import CustomGroup


class Data(models.Model):
    title = models.CharField(max_length=200, blank=False)
    group = models.ForeignKey(CustomGroup, on_delete=models.CASCADE, blank=False)

    class Meta:
        unique_together = ("title", "group")


class FinalizedData(Data):
    answer_text = models.TextField(blank=False, null=False)

    @classmethod
    def create(cls, title, group, ans):
        try:
            data = Data.objects.get(title=title, group=group)
            finalized_data = cls(pk=data.id, answer_text=ans, title=title, group=group)
        except Data.DoesNotExist:
            finalized_data = cls(title=title, answer_text=ans, group=group)
        finalized_data.save()
        return finalized_data


class ValidatingData(Data):
    data_ptr = models.OneToOneField(to=Data, on_delete=models.CASCADE, parent_link=True)
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
        data = VotingData.create(title=self.title, group=self.group)
        Choice.objects.update_or_create(data=data, answer=new_ans)

    def validate(self):
        datas = VotingData.objects.filter(pk=self.id, group=self.data_ptr.group)
        if self.num_approved >= 2:
            # if enough user has approve the answer
            # the origin answer is considered to be correct
            FinalizedData.create(title=self.data_ptr.title, group=self.data_ptr.group, ans=self.answer_text)
            for data in datas:
                Choice.objects.filter(data=data).delete()
            self.delete(keep_parents=True)
        elif self.num_disapproved >= 2:
            # if enough user has disapprove the answer
            # the better answer should be selected by activating VotingData
            for data in datas:
                data.is_active = True
                data.save()
            self.delete()


class VotingData(Data):
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
            Data.objects.update_or_create(question_text=self.data_ptr.title, answer_text=selected_choice.answer,
                                          group=self.group)
            self.delete()


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


class Log(models.Model):
    user = models.ForeignKey(get_user_model(), models.CASCADE, related_name="data_log")
    task = models.ForeignKey(Data, models.CASCADE)
    action = models.CharField(max_length=32)
    response = models.TextField()
    timestamp = models.DateTimeField()
    checked = models.BooleanField(default=False)