from django.test import client
from django.test import TestCase, RequestFactory, Client
from pages.models.image import ImageData, ImageLabel, FinalizedImageData
from pages.models.validate import ValidatingData
from pages.models.vote import VotingData, Choice
from pages.models.models import FinalizedData
from authentication.models import CustomGroup, CustomUser
from assign.models import Assignment
import json
from django.utils.http import urlencode

from pages.views.utils import get_assigned_tasks_context, get_finalized_data, get_unassigned_voting_data, \
    get_num_per_group_dict, get_group_info_context


class UserViewTestCase(TestCase):
    def setUp_client(self):
        self.client = Client()
        self.group, _ = CustomGroup.objects.update_or_create(name="KKH")
        self.user = CustomUser.objects.create_user(
            username='alice', email='alice@gmail.com', certificate="G123456M",
            group=self.group, password='top_secret')
        self.user.approve(True)
        self.client.login(username="alice@gmail.com", password="top_secret")

    def setUp_validating(self):
        self.validating = []
        for i in range(20):
            data = ValidatingData.create(group=self.group, title="Title{}".format(i), ans="Answer{}".format(i))
            self.validating.append(data)

    def setUp_voting(self):
        self.active_voting = []
        self.inactive_voting = []
        for i in range(20):
            data = VotingData.create(group=self.group, title="A_Title{}".format(i), is_active=True)
            self.active_voting.append(data)
            for j in range(5):
                Choice.objects.update_or_create(data=data, answer="Choice{}".format(j))

        for i in range(10):
            data = VotingData.create(group=self.group, title="I_Title{}".format(i))
            self.inactive_voting.append(data)
            for j in range(5):
                Choice.objects.update_or_create(data=data, answer="Choice{}".format(j))

    def setUp_keywords(self):
        self.finalized = []
        for i in range(10):
            data = FinalizedData.create(title="Title{}".format(i), group=self.group, ans="Answer{}".format(i))
            self.finalized.append(data)

    def setUp_image(self):
        self.images = []
        for i in range(6):
            data = ImageData.create(group=self.group, url="www.google.com/{}.jpg".format(i))
            self.images.append(data)
            for j in range(5):
                ImageLabel.objects.update_or_create(image=data, label="food{}".format(j))

    def setUp(self) -> None:
        self.setUp_client()
        self.setUp_validating()
        self.setUp_voting()
        self.setUp_keywords()
        self.setUp_image()

    def test_get(self):
        response = self.client.get('/tasks/validate')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/tasks/vote')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/tasks/keywords')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/tasks/image')
        self.assertEqual(response.status_code, 200)

    def test_post_validate_add_data(self):
        session = self.client.session
        session['data'] = {"validate_ids": [str(val.id) for val in self.validating[:5]]}
        for val in self.validating[:5]:
            session['data']['approve_value_{}'.format(val.id)] = 'true'
        session.save()

        assignments = []
        for val in self.validating[:10]:
            assignment = Assignment.objects.create(tasker=self.user, task=val)
            assignments.append(assignment)

        new_id = self.validating[5].id
        data = {"validate_ids": new_id,
                "approve_value_{}".format(new_id): 'false',
                "new_ans_{}".format(new_id): 'New Answer'}
        response = self.client.post(path='/tasks/validate',
                                    data=data,
                                    follow=True, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.client.session)
        self.assertIn('validate_ids', response.client.session['data'])
        data = response.client.session['data']['validate_ids']
        expected_data = [str(val.id) for val in self.validating[:6]]
        data.sort()
        expected_data.sort()
        self.assertEqual(data, expected_data)

        for assignment in assignments:
            self.assertFalse(Assignment.objects.get(pk=assignment.pk).done)

    def test_post_validate_update_data(self):
        session = self.client.session
        session['data'] = {"validate_ids": [str(val.id) for val in self.validating[:5]]}
        for val in self.validating[:5]:
            session['data']['approve_value_{}'.format(val.id)] = 'true'
        session.save()

        assignments = []
        for val in self.validating[:10]:
            assignment = Assignment.objects.create(tasker=self.user, task=val)
            assignments.append(assignment)

        new_id = self.validating[1].id
        data = {"validate_ids": new_id,
                "approve_value_{}".format(new_id): 'false',
                "new_ans_{}".format(new_id): 'New Answer'}
        response = self.client.post(path='/tasks/validate',
                                    data=data,
                                    follow=True, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.client.session)
        self.assertIn('validate_ids', response.client.session['data'])
        data = response.client.session['data']['validate_ids']
        expected_data = [str(val.id) for val in self.validating[:5]]
        data.sort()
        expected_data.sort()
        self.assertEqual(data, expected_data)
        self.assertIn('approve_value_{}'.format(new_id), response.client.session['data'])
        self.assertEqual(response.client.session['data']['approve_value_{}'.format(new_id)], 'false')
        self.assertIn('new_ans_{}'.format(new_id), response.client.session['data'])
        self.assertEqual(response.client.session['data']['new_ans_{}'.format(new_id)], 'New Answer')

        for assignment in assignments:
            self.assertFalse(Assignment.objects.get(pk=assignment.pk).done)

    def test_post_validate_submit(self):
        session = self.client.session
        session['data'] = {"validate_ids": [val.id for val in self.validating[:5]]}
        for val in self.validating[:5]:
            session['data']['approve_value_{}'.format(val.id)] = 'true'
        session.save()

        assignments = []
        for val in self.validating[:10]:
            assignment = Assignment.objects.create(tasker=self.user, task=val)
            assignments.append(assignment)

        val_ids = ""
        data = {"submit": 'Submit'}
        for val in self.validating[5:10]:
            val_ids += "{},".format(val.id)
            data["approve_value_{}".format(val.id)] = 'false'
            data["new_ans_{}".format(val.id)] = 'New Answer {}'.format(val.id)
        data['validate_ids'] = val_ids
        response = self.client.post(path='/tasks/validate',
                                    data=data,
                                    follow=True, format='json')
        self.assertEqual(response.status_code, 200)
        for assignment in assignments:
            self.assertTrue(Assignment.objects.get(pk=assignment.pk).done)
        for val in self.validating[:5]:
            self.assertEqual(ValidatingData.objects.get(pk=val.id).num_approved, 1)
        for val in self.validating[5:10]:
            self.assertEqual(ValidatingData.objects.get(pk=val.id).num_disapproved, 1)
            self.assertIsNotNone(VotingData.objects.get(pk=val.id))
            data = VotingData.objects.get(pk=val.id)
            self.assertIsNotNone(data.choice_set.all().first())
            self.assertEqual(data.choice_set.all()[0].answer, 'New Answer {}'.format(val.id))
            self.assertFalse(data.is_active)

    def test_post_validate_final(self):
        session = self.client.session
        session['data'] = {"validate_ids": [val.id for val in self.validating[:5]]}
        for val in self.validating[:5]:
            session['data']['approve_value_{}'.format(val.id)] = 'true'
        session.save()

        val_ids = ""
        data = {"submit": 'Submit'}
        val = self.validating[6]
        val_ids += "{},".format(val.id)
        data["approve_value_{}".format(val.id)] = 'false'
        data["new_ans_{}".format(val.id)] = 'New Answer {}'.format(val.id)
        data['validate_ids'] = val_ids
        val.num_approved = 1
        val.num_disapproved = 1
        val.save()
        data_id = val.id

        response = self.client.post(path='/tasks/validate',
                                    data=data,
                                    follow=True, format='json')
        self.assertEqual(response.status_code, 200)

        for val in self.validating[:5]:
            self.assertEqual(ValidatingData.objects.get(pk=val.id).num_approved, 1)

        self.assertIsNone(ValidatingData.objects.filter(pk=data_id).first())
        self.assertIsNotNone(VotingData.objects.get(pk=data_id))
        data = VotingData.objects.get(pk=data_id)
        self.assertIsNotNone(data.choice_set.all().first())
        self.assertEqual(data.choice_set.all().count(), 1)
        self.assertEqual(data.choice_set.all()[0].answer, 'New Answer {}'.format(data_id))
        self.assertTrue(data.is_active)

    def test_post_vote(self):
        vote = self.active_voting[0]
        choice = vote.choice_set.all()[1]
        assignment = Assignment.objects.create(tasker=self.user, task=vote)
        self.assertEqual(choice.num_votes, 0)
        self.assertFalse(assignment.done)

        response = self.client.post(path='/{}/vote'.format(vote.id), data={"choice": [choice.id]}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Choice.objects.get(pk=choice.id).num_votes, 1)
        self.assertTrue(Assignment.objects.get(pk=assignment.pk).done)

    def test_post_final_vote(self):
        vote = self.active_voting[1]
        choice = vote.choice_set.all()[2]
        choice.num_votes = 4
        choice.save()
        self.assertEqual(choice.num_votes, 4)

        response = self.client.post(path='/{}/vote'.format(vote.id), data={"choice": [choice.id]}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(FinalizedData.objects.get(pk=vote.pk))
        self.assertIsNone(VotingData.objects.filter(pk=vote.pk).first())
        self.assertIsNone(Choice.objects.filter(data=vote.id).first())

    def test_post_final_vote_2(self):
        vote = self.active_voting[2]
        first_choice = vote.choice_set.all()[0]
        first_choice.num_votes = 2
        first_choice.save()
        second_choice = vote.choice_set.all()[1]
        second_choice.num_votes = 2
        second_choice.save()

        response = self.client.post(path='/{}/vote'.format(vote.id), data={"choice": [first_choice.id]}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(FinalizedData.objects.get(pk=vote.pk))
        self.assertEqual(FinalizedData.objects.get(pk=vote.pk).answer_text, first_choice.answer)
        self.assertIsNone(VotingData.objects.filter(pk=vote.pk).first())
        self.assertIsNone(Choice.objects.filter(data=vote.id).first())

    def test_post_final_vote_tie(self):
        vote = self.active_voting[3]
        first_choice = vote.choice_set.all()[0]
        first_choice.num_votes = 2
        first_choice.save()
        second_choice = vote.choice_set.all()[1]
        second_choice.num_votes = 2
        second_choice.save()

        response = self.client.post(path='/{}/vote'.format(vote.id),
                                    data={"choice": [vote.choice_set.all()[2].id]}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(FinalizedData.objects.get(pk=vote.pk))
        self.assertIn(FinalizedData.objects.get(pk=vote.pk).answer_text, [first_choice.answer, second_choice.answer])
        self.assertIsNone(VotingData.objects.filter(pk=vote.pk).first())
        self.assertIsNone(Choice.objects.filter(data=vote.id).first())

    def test_post_keywords(self):
        keywords = self.finalized[0]
        keywords.title = "This is a question."
        keywords.answer_text = "This is an answer ."
        keywords.save()
        assignment = Assignment.objects.create(tasker=self.user, task=keywords)
        self.assertEqual(keywords.qns_keywords, "")
        self.assertEqual(keywords.ans_keywords, "")

        response = self.client.post(path='/{}/keywords'.format(keywords.id),
                                    data={
                                        "qns_keywords": 'This,a,',
                                        "ans_keywords": 'This,answer,.,',
                                    }, follow=True)
        self.assertEqual(response.status_code, 200)
        keywords = FinalizedData.objects.get(pk=keywords.pk)
        self.assertEqual(keywords.qns_keywords, 'This,a,')
        self.assertEqual(keywords.ans_keywords, 'This,answer,.,')
        self.assertTrue(Assignment.objects.get(pk=assignment.pk).is_done)

        response = self.client.post(path='/{}/keywords'.format(keywords.id),
                                    data={
                                        "qns_keywords": 'question.,',
                                        "ans_keywords": 'is,',
                                    }, follow=True)
        self.assertEqual(response.status_code, 200)
        keywords = FinalizedData.objects.get(pk=keywords.pk)
        self.assertEqual(keywords.qns_keywords, 'This,a,question.,')
        self.assertEqual(keywords.ans_keywords, 'This,answer,.,is,')
        self.assertTrue(Assignment.objects.get(pk=assignment.pk).is_done)

    def test_post_image(self):
        img = self.images[0]
        label = img.imagelabel_set.all()[1]
        assignment = Assignment.objects.create(tasker=self.user, task=img)
        self.assertEqual(label.num_votes, 0)
        self.assertFalse(assignment.done)

        response = self.client.post(path='/{}/image'.format(img.id), data={"label": [label.id]}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ImageLabel.objects.get(pk=label.id).num_votes, 1)
        self.assertTrue(Assignment.objects.get(pk=assignment.pk).done)

    def test_post_final_image(self):
        img = self.images[1]
        label = img.imagelabel_set.all()[2]
        label.num_votes = 4
        label.save()
        self.assertEqual(label.num_votes, 4)

        response = self.client.post(path='/{}/image'.format(img.id), data={"label": [label.id]}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(FinalizedImageData.objects.get(pk=img.pk))
        self.assertEqual(FinalizedImageData.objects.get(pk=img.pk).label, label.label)
        self.assertIsNone(ImageData.objects.filter(pk=img.pk).first())
        self.assertIsNone(ImageLabel.objects.filter(pk=label.id).first())

    def test_post_final_image_2(self):
        img = self.images[2]
        first_abel = img.imagelabel_set.all()[0]
        first_abel.num_votes = 2
        first_abel.save()
        second_label = img.imagelabel_set.all()[1]
        second_label.num_votes = 2
        second_label.save()

        response = self.client.post(path='/{}/image'.format(img.id), data={"label": [first_abel.id]}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(FinalizedImageData.objects.get(pk=img.pk))
        self.assertEqual(FinalizedImageData.objects.get(pk=img.pk).label, first_abel.label)
        self.assertIsNone(ImageData.objects.filter(pk=img.pk).first())
        self.assertIsNone(ImageLabel.objects.filter(image=img).first())

    def test_post_final_image_tie(self):
        img = self.images[3]
        first_abel = img.imagelabel_set.all()[0]
        first_abel.num_votes = 2
        first_abel.save()
        second_label = img.imagelabel_set.all()[1]
        second_label.num_votes = 2
        second_label.save()

        label = img.imagelabel_set.all()[2]
        response = self.client.post(path='/{}/image'.format(img.id), data={"label": [label.id]}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(FinalizedImageData.objects.get(pk=img.pk))
        self.assertIn(FinalizedImageData.objects.get(pk=img.pk).label, [first_abel.label, second_label.label])
        self.assertIsNone(ImageData.objects.filter(pk=img.pk).first())
        self.assertIsNone(ImageLabel.objects.filter(image=img).first())


class UtilsTestCase(TestCase):
    def setUp_auth(self):
        self.group, _ = CustomGroup.objects.update_or_create(name="KKH")
        self.other_group, _ = CustomGroup.objects.update_or_create(name="Other")
        self.user = CustomUser.objects.create_user(
            username='alice', email='alice@gmail.com', certificate="G123456M", group=self.group, password='top_secret'
        )
        self.other_user = CustomUser.objects.create_user(
            username='other', email='other@gmail.com', certificate="G111111M", group=self.group, password="low_secret"
        )
        self.num_kkh = 10
        self.num_other = 8
        for i in range(self.num_kkh - 2):
            _ = CustomUser.objects.create_user(
                username='KKH{}'.format(i), email='KKH{}@gmail.com'.format(i),
                certificate="K123456{}M".format(i), group=self.group, password='top_secret'
            )
        for i in range(self.num_other):
            _ = CustomUser.objects.create_user(
                username='Other{}'.format(i), email='Other{}@gmail.com'.format(i),
                certificate="O123456{}M".format(i), group=self.other_group, password='top_secret'
            )

    def setUp_vote(self):
        self.active_voting_data = []
        self.unassigned_voting_data = []
        # active voting data
        for q in range(20):
            voting_data = VotingData.create(title=q, group=self.group, is_active=True)
            self.active_voting_data.append(voting_data)
            for a in range(3):
                choice, _ = Choice.objects.update_or_create(data=voting_data, answer=a, num_votes=0)
        # inactive voting data
        for q in range(20, 30):
            voting_data = VotingData.create(title=q, group=self.group, is_active=False)
            for a in range(3):
                choice, _ = Choice.objects.update_or_create(data=voting_data, answer=a, num_votes=0)
            self.unassigned_voting_data.append(voting_data)
        self.num_vote_kkh = 30

        # active other group data
        for q in range(5):
            voting_data = VotingData.create(title=q, group=self.other_group, is_active=False)
            for a in range(3):
                choice, _ = Choice.objects.update_or_create(data=voting_data, answer=a, num_votes=0)
            self.unassigned_voting_data.append(voting_data)
        self.num_vote_other = 5

        self.num_todo = 0
        self.num_done = 0
        for i, data in enumerate(self.active_voting_data):
            if i > 10:
                if i % 2 == 0:
                    Assignment.objects.update_or_create(tasker=self.user, task=data, done=False)
                    self.num_todo += 1
                else:
                    Assignment.objects.update_or_create(tasker=self.user, task=data, done=True)
                    self.num_done += 1
            elif i < 5:
                Assignment.objects.update_or_create(tasker=self.other_user, task=data, done=False)
            else:
                self.unassigned_voting_data.append(data)

    def setUp_finalized(self):
        self.finalized_data_group = []
        self.finalized_data = []
        for i in range(20):
            data = FinalizedData.create(title="Title{}".format(i), group=self.group, ans="Ans{}".format(i))
            self.finalized_data_group.append(data)
            self.finalized_data.append(data)

        for i in range(10):
            data = FinalizedData.create(title="Title{}".format(i), group=self.other_group, ans="Ans{}".format(i))
            self.finalized_data.append(data)

    def setUp(self):
        self.factory = RequestFactory()
        self.setUp_auth()
        self.setUp_vote()
        self.setUp_finalized()

    def test_get_assigned_tasks_context(self):
        data, task_num = get_assigned_tasks_context(self.user, VotingData, condition=(lambda x: x.is_active))
        expected_data = self.active_voting_data[11:]
        expected_task_num = {
            'todo': self.num_todo,
            'done': self.num_done,
            'total': self.num_todo + self.num_done,
        }

        self.assertEqual(len(data), len(expected_data))
        self.assertEqual(set(data), set(expected_data))
        self.assertEqual(task_num, expected_task_num)

    def test_get_finalized_data(self):
        data = get_finalized_data(self.group.name)
        expected_data = self.finalized_data_group
        self.assertEqual(len(data), len(expected_data))
        self.assertEqual(set(data), set(expected_data))

        data = get_finalized_data()
        expected_data = self.finalized_data
        self.assertEqual(len(data), len(expected_data))
        self.assertEqual(set(data), set(expected_data))

        data = get_finalized_data("all")
        expected_data = self.finalized_data
        self.assertEqual(len(data), len(expected_data))
        self.assertEqual(set(data), set(expected_data))

    def test_get_unassigned_voting_data(self):
        data = get_unassigned_voting_data()
        expected_data = self.unassigned_voting_data
        self.assertEqual(len(data), len(expected_data))
        self.assertEqual(set(data), set(expected_data))

        data = get_unassigned_voting_data(group=self.group)
        expected_data = [data for data in self.unassigned_voting_data if data.group == self.group]
        self.assertEqual(len(data), len(expected_data))
        self.assertEqual(set(data), set(expected_data))

    def test_get_admin_logs(self):
        return

    def test_get_num_per_group_dict(self):
        num_dict = get_num_per_group_dict(CustomUser)
        expected_dict = {
            self.group.id: self.num_kkh,
            self.other_group.id: self.num_other
        }
        self.assertEqual(num_dict, expected_dict)

        num_dict = get_num_per_group_dict(VotingData)
        expected_dict = {
            self.group.id: self.num_vote_kkh,
            self.other_group.id: self.num_vote_other
        }
        self.assertEqual(num_dict, expected_dict)

    def test_get_group_info_context(self):
        user_num_dict = {
            self.group.id: self.num_kkh,
            self.other_group.id: self.num_other
        }
        data_num_dict = {
            self.group.id: self.num_vote_kkh,
            self.other_group.id: self.num_vote_other
        }

        groups_info = get_group_info_context([self.group, self.other_group],
                                             {
                                                "user": user_num_dict,
                                                "data": data_num_dict,
                                             })
        expected_groups_info = [
            {
                "name": self.group.name,
                "user": self.num_kkh,
                "data": self.num_vote_kkh,
            },
            {
                "name": self.other_group.name,
                "user": self.num_other,
                "data": self.num_vote_other,
            }
        ]

        self.assertEqual(groups_info, expected_groups_info)

    def test_merge_validate_context(self):
        return

    def test_get_ids(self):
        return

    def test_done_assignment(self):
        return

    def test_compute_progress(self):
        return