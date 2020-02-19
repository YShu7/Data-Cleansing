from django.db import models
from pages.models.models import Data


class ImageData(Data):
    image_url = models.URLField(unique=True)

    @classmethod
    def create(cls, group, url, title=None):
        if title is None:
            title = url
        try:
            data = Data.objects.get(title=title, group=group)
            image_data = cls(pk=data.id, title=title, group=group, image_url=url)
        except Data.DoesNotExist:
            image_data = cls(title=title, group=group, image_url=url)
        image_data.save()
        return image_data

    def vote(self, selected_choice):
        # update num of votes of the selected choice
        selected_choice.vote()

        # get the number of choices that have been made for this question
        choices = self.imagelabel_set.all()
        sum_votes = 0
        max_votes = selected_choice.num_votes
        for c in choices:
            sum_votes += c.num_votes
            max_votes = max(max_votes, c.num_votes)

        # if enough users have made responses to this question and this choice has the maximum num of votes,
        # this question is done
        if sum_votes >= 5 and selected_choice.num_votes == max_votes:
            FinalizedImageData.create_from_parent(data=self)
            self.delete()


class ImageLabel(models.Model):
    image = models.ForeignKey(ImageData, models.CASCADE)
    label = models.TextField(blank=False, null=False)
    num_votes = models.IntegerField(default=0)

    def vote(self):
        self.num_votes += 1
        self.save()
