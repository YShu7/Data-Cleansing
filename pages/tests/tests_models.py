from django.test import TestCase

from authentication.models import CustomGroup, CustomUser
from assign.models import Assignment
from pages.models.image import ImageData, ImageLabel, FinalizedImageData
from pages.models.models import FinalizedData
from pages.models.validate import ValidatingData
from pages.models.vote import VotingData, Choice


class VotingDataTestCase(TestCase):
    def setUp(self):
        group_names = ["KKH", "TPH", "AAH", "BH"]
        self.groups = []
        for group_name in group_names:
            group, _ = CustomGroup.objects.update_or_create(name=group_name)
            self.groups.append(group)

        for q in range(20):
            voting_data = VotingData.create(title=q, group=self.groups[0], is_active=True)
            for a in range(3):
                choice = Choice.objects.create(data=voting_data, answer=a, num_votes=0)

        self.user = CustomUser.objects.create_user(
            email='user@gmail.com', username='user', certificate='G123456M',
            password='password', group=self.groups[0])

    def test_vote_has_result(self):
        voting_data = VotingData.objects.all()[0]
        selected_choice = voting_data.choice_set.all()[0]
        other_choice1 = voting_data.choice_set.all()[1]

        voting_data.vote(selected_choice)
        self.assertEqual(voting_data.num_votes, 1)

        voting_data.vote(selected_choice)
        voting_data.vote(selected_choice)
        voting_data.vote(other_choice1)
        voting_data.vote(other_choice1)
        self.assertEqual(voting_data.num_votes, 5)
        self.assertIsNone(VotingData.objects.filter(pk=voting_data.pk).first())
        self.assertIsNotNone(FinalizedData.objects.filter(
            title=voting_data.data_ptr.title,
            answer_text=selected_choice.answer,
            group=voting_data.group
        ).first())

    def test_vote_no_result_no_user(self):
        voting_data = VotingData.objects.all()[1]
        selected_choice = voting_data.choice_set.all()[0]
        other_choice1 = voting_data.choice_set.all()[1]
        other_choice2 = voting_data.choice_set.all()[2]

        voting_data.vote(selected_choice)
        self.assertEqual(voting_data.num_votes, 1)

        voting_data.vote(selected_choice)
        voting_data.vote(other_choice1)
        voting_data.vote(other_choice1)
        voting_data.vote(other_choice2)
        self.assertEqual(voting_data.num_votes, 5)
        self.assertIsNotNone(VotingData.objects.filter(pk=voting_data.pk).first())
        self.assertIsNone(FinalizedData.objects.filter(
            title=voting_data.data_ptr.title,
            group=voting_data.group
        ).first())
        self.assertEqual(Assignment.objects.filter(task=voting_data, done=False).count(), 0)

    def test_vote_no_result(self):
        for i in range(5):
            CustomUser.objects.create_user(
                email='user{}@gmail.com'.format(i), username='user'.format(i), certificate='G123456{}M'.format(i),
                password='password', group=self.user.group)
        voting_data = VotingData.objects.all()[2]
        selected_choice = voting_data.choice_set.all()[0]
        other_choice1 = voting_data.choice_set.all()[1]
        other_choice2 = voting_data.choice_set.all()[2]

        voting_data.vote(selected_choice)
        self.assertEqual(voting_data.num_votes, 1)

        voting_data.vote(selected_choice)
        voting_data.vote(other_choice1)
        voting_data.vote(other_choice1)
        voting_data.vote(other_choice2)
        self.assertEqual(voting_data.num_votes, 5)
        self.assertIsNotNone(VotingData.objects.filter(pk=voting_data.pk).first())
        self.assertIsNone(FinalizedData.objects.filter(
            title=voting_data.data_ptr.title,
            group=voting_data.group
        ).first())
        self.assertEqual(Assignment.objects.filter(task=voting_data, done=False).count(), 2)


class ImageDataTestCase(TestCase):
    def setUp(self) -> None:
        group_names = ["KKH", "TPH", "AAH", "BH"]
        self.groups = []
        for group_name in group_names:
            group, _ = CustomGroup.objects.update_or_create(name=group_name)
            self.groups.append(group)

        for q in range(20):
            img_data = ImageData.create(group=group,
                                        url='"https://media.timeout.com/images/105370171/630/{}/image.jpg"'.format(q))
            for a in range(3):
                label = ImageLabel.objects.create(image=img_data, label="Label_{}".format(a))

        self.user = CustomUser.objects.create_user(
            email='user@gmail.com', username='user', certificate='G123456M',
            password='password', group=self.groups[0])

    def test_vote_finalize_has_result(self):
        img_data = ImageData.objects.all()[0]

        selected_label = img_data.imagelabel_set.all()[0]
        other_label1 = img_data.imagelabel_set.all()[1]

        img_data.vote(selected_label)
        self.assertEqual(img_data.num_votes, 1)

        img_data.vote(selected_label)
        img_data.vote(selected_label)
        img_data.vote(other_label1)
        img_data.vote(other_label1)
        self.assertEqual(img_data.num_votes, 5)
        self.assertIsNone(ImageData.objects.filter(pk=img_data.pk).first())
        self.assertIsNotNone(FinalizedImageData.objects.filter(
            image_url=img_data.title,
            label=selected_label.label,
            group=img_data.group
        ).first())

    def test_vote_finalize_no_result_no_user(self):
        img_data = ImageData.objects.all()[1]
        selected_label = img_data.imagelabel_set.all()[0]
        other_label1 = img_data.imagelabel_set.all()[1]
        other_label2 = img_data.imagelabel_set.all()[2]

        img_data.vote(selected_label)
        self.assertEqual(img_data.num_votes, 1)

        img_data.vote(other_label2)
        img_data.vote(other_label1)
        img_data.vote(other_label1)
        img_data.vote(other_label2)
        self.assertEqual(img_data.num_votes, 5)
        self.assertIsNotNone(ImageData.objects.filter(pk=img_data.pk).first())
        self.assertIsNone(FinalizedImageData.objects.filter(
            image_url=img_data.title,
            group=img_data.group
        ).first())
        self.assertEqual(Assignment.objects.filter(task=img_data, done=False).count(), 0)

    def test_vote_finalize_no_result(self):
        for i in range(5):
            CustomUser.objects.create_user(
                email='user{}@gmail.com'.format(i), username='user{}'.format(i),
                certificate='G123456{}M'.format(i), password='password', group=self.user.group)
        img_data = ImageData.objects.all()[2]
        selected_label = img_data.imagelabel_set.all()[0]
        other_label1 = img_data.imagelabel_set.all()[1]
        other_label2 = img_data.imagelabel_set.all()[2]

        img_data.vote(selected_label)
        self.assertEqual(img_data.num_votes, 1)

        img_data.vote(other_label2)
        img_data.vote(other_label1)
        img_data.vote(other_label1)
        img_data.vote(other_label2)
        self.assertEqual(img_data.num_votes, 5)
        self.assertIsNotNone(ImageData.objects.filter(pk=img_data.pk).first())
        self.assertIsNone(FinalizedImageData.objects.filter(
            image_url=img_data.title,
            group=img_data.group
        ).first())
        self.assertEqual(Assignment.objects.filter(task=img_data, done=False).count(), 2)


class ValidatingDataTestCase(TestCase):
    def setUp(self) -> None:
        group_names = ["KKH", "TPH", "AAH", "BH"]
        groups = []
        for group_name in group_names:
            group, _ = CustomGroup.objects.update_or_create(name=group_name)
            groups.append(group)

        for q in range(5):
            val_data = ValidatingData.create(title=q, group=groups[0], ans=q)

        user = CustomUser.objects.create_user(email='user@gmail.com', username='user', certificate='G123456M',
                                              password='password', group=groups[0])

    def test_approve(self):
        data = ValidatingData.objects.all()[0]
        data.approve()
        self.assertEqual(data.num_approved, 1)
        self.assertEqual(data.num_disapproved, 0)

    def test_disapprove(self):
        data = ValidatingData.objects.all()[0]
        new_ans = "New_Ans"
        data.disapprove(new_ans)
        self.assertEqual(data.num_approved, 0)
        self.assertEqual(data.num_disapproved, 1)
        voting_data = VotingData.objects.filter(title=data.title, group=data.group).first()
        self.assertIsNotNone(voting_data)
        self.assertIn(new_ans, [c.answer for c in voting_data.choice_set.all()])

    def test_validate(self):
        data = ValidatingData.objects.all()[0]
        data.approve()
        data.disapprove("New Answer")
        data.approve()
        data.validate()
        self.assertIsNotNone(FinalizedData.objects.filter(
            title=data.title,
            answer_text=data.answer_text,
            group=data.group
        ).first())
        self.assertIsNone(ValidatingData.objects.filter(
            title=data.title,
            answer_text=data.answer_text,
            group=data.group
        ).first())
        self.assertIsNone(VotingData.objects.filter(
            title=data.title,
            group=data.group
        ).first())

        data = ValidatingData.objects.all()[0]
        new_ans1 = "New Answer1"
        new_ans2 = "New Answer2"
        data.approve()
        data.disapprove(new_ans1)
        data.disapprove(new_ans2)
        data.validate()
        self.assertIsNone(FinalizedData.objects.filter(
            title=data.title,
            answer_text=data.answer_text,
            group=data.group
        ).first())
        self.assertIsNone(ValidatingData.objects.filter(
            title=data.title,
            answer_text=data.answer_text,
            group=data.group
        ).first())
        voting_data = VotingData.objects.filter(
            title=data.title,
            group=data.group,
            is_active=True
        ).first()
        self.assertIsNotNone(voting_data)
        answers = [c.answer for c in voting_data.choice_set.all()]
        self.assertIn(new_ans1, answers)
        self.assertIn(new_ans2, answers)
