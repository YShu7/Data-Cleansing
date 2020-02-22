from django.test import TestCase
from pages.models.vote import VotingData, Choice
from pages.models.models import FinalizedData
from pages.models.image import ImageData, ImageLabel, FinalizedImageData
from authentication.models import CustomGroup


class VotingDataTestCase(TestCase):
    def setUp(self):
        group_names = ["KKH", "TPH", "AAH", "BH"]
        groups = []
        for group_name in group_names:
            group, _ = CustomGroup.objects.update_or_create(name=group_name)
            groups.append(group)

        for q in range(20):
            voting_data = VotingData.create(title=q, group=groups[0], is_active=True)
            for a in range(3):
                choice = Choice.objects.create(data=voting_data, answer=a, num_votes=0)

    def test_vote_finalize(self):
        voting_data = VotingData.objects.all()[0]
        pk = voting_data.id

        # reset new_votes
        choice = voting_data.choice_set.all()[0]
        choice.num_votes = 0
        choice.save()
        self.assertEqual(choice.num_votes, 0)

        # 1
        voting_data.vote(choice)
        self.assertEqual(choice.num_votes, 1)

        # 2, 3, 4
        voting_data.vote(choice)
        voting_data.vote(choice)
        self.assertEqual(choice.num_votes, 3)
        voting_data.vote(choice)

        # 5
        voting_data.vote(choice)
        self.assertIsNone(VotingData.objects.filter(pk=pk).first())
        self.assertIsNone(Choice.objects.filter(data=voting_data).first())
        filtered_data = FinalizedData.objects.filter(
            title=voting_data.data_ptr.title,
            answer_text=choice.answer,
            group=voting_data.group)
        self.assertIsNotNone(filtered_data.first(), "FinalizedData is not created.")
        self.assertEqual(filtered_data.first().pk, pk)


class ImageDataTestCase(TestCase):
    def test_vote_finalize(self):
        group, _ = CustomGroup.objects.update_or_create(name="KKH")
        img_data = ImageData.create(group=group,
                                    url='"https://media.timeout.com/images/105370171/630/472/image.jpg"')
        for a in range(3):
            label = ImageLabel.objects.create(image=img_data, label="Label_{}".format(a))

        pk = img_data.id

        # reset new_votes
        label = img_data.imagelabel_set.all()[0]
        label.num_votes = 0
        label.save()
        self.assertEqual(label.num_votes, 0)

        # 1
        img_data.vote(label)
        self.assertEqual(label.num_votes, 1)

        # 2, 3, 4
        img_data.vote(label)
        img_data.vote(label)
        self.assertEqual(label.num_votes, 3)
        img_data.vote(label)

        # 5
        img_data.vote(label)
        self.assertIsNone(ImageData.objects.filter(pk=pk).first())
        self.assertIsNone(ImageLabel.objects.filter(image=img_data).first())
        filtered_data = FinalizedImageData.objects.filter(
            title=img_data.title,
            image_url=img_data.image_url,
            group=img_data.group)
        self.assertIsNotNone(filtered_data.first(), "FinalizedData is not created.")
        self.assertEqual(filtered_data.first().pk, pk, "FinalizedData does not have the same id.")
