from django.db import models
from django.contrib.auth import get_user_model
from math import ceil

from assign.models import Assignment
from pages.models.models import Data


class ImageData(Data):
    image_url = models.URLField(unique=True)
    is_contro = models.BooleanField(default=False)
    num_votes = models.IntegerField(default=0)

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
        num_votes = selected_choice.vote()

        # get the number of choices that have been made for this question
        choices = self.imagelabel_set.all()

        # if enough users have made responses to this question and this choice has the maximum num of votes,
        # this question is done
        reassigned = True
        if num_votes >= 5 and num_votes <= 15:
            for c in choices:
                if c.num_votes >= ceil(num_votes / 2.0):
                    FinalizedImageData.create_from_imagedata(data=self)
                    self.delete(keep_parents=True)
                    return
            reassigned = Assignment.reassign(self, get_user_model().objects.all())

        if num_votes > 15 or not reassigned:
            self.is_contro = True
            self.save()
            self.assignment_set.all().delete()


class ImageLabel(models.Model):
    image = models.ForeignKey(ImageData, models.CASCADE)
    label = models.CharField(blank=False, null=False, max_length=200)
    num_votes = models.IntegerField(default=0)

    def vote(self):
        self.num_votes += 1
        self.save()
        self.image.num_votes += 1
        self.image.save()
        return self.image.num_votes


class FinalizedImageData(Data):
    image_url = models.URLField(unique=True)
    label = models.CharField(blank=False, null=False, max_length=200)

    @classmethod
    def create(cls, group, url, label, title=None):
        if title is None:
            title = url
        try:
            data = Data.objects.get(title=title, group=group)
            image_data = cls(pk=data.id, title=title, group=group, label=label, image_url=url)
        except Data.DoesNotExist:
            image_data = cls(title=title, group=group, label=label, image_url=url)
        image_data.save()
        return image_data

    @classmethod
    def create_from_imagedata(cls, data):
        labels = data.imagelabel_set.all()
        label = labels.first()
        for l in labels:
            if l.num_votes > label.num_votes:
                label = l
        return FinalizedImageData.create(group=data.group, title=data.title, label=label.label, url=data.image_url)
