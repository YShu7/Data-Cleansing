import csv
import io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from django.utils import translation

from assign.models import Assignment
from authentication.forms import CreateGroupForm
from authentication.models import CustomGroup, CustomUser
from datacleansing.settings import VOT, VAL, INCORRECT_POINT, CORRECT_POINT, MSG_FAIL_DATA_NONEXIST, \
    MSG_FAIL_CHOICE, MSG_FAIL_LABEL_NONEXIST
from pages.models.image import ImageData, ImageLabel, FinalizedImageData
from pages.models.models import FinalizedData, Log
from pages.models.validate import ValidatingData
from pages.models.vote import VotingData, Choice
from pages.views.utils import get_assigned_tasks_context, get_finalized_data, get_controversial_voting_data, \
    get_num_per_group_dict, get_group_info_context, get_group_report_context


class UserViewTestCase(TestCase):
    def setUp_client(self):
        self.client = Client()
        self.group, _ = CustomGroup.objects.update_or_create(name="KKH")
        self.user = CustomUser.objects.create_user(
            username='alice', email='alice@gmail.com', certificate="G123456M",
            group=self.group, password='top_secret')
        self.user.approve(True)
        self.client.login(username="alice@gmail.com", password="top_secret")

        for i in range(5):
            CustomUser.objects.create_user(
                username='user{}'.format(i), email='user{}@gmail.com'.format(i), certificate="G123456{}M".format(i),
                group=self.group, password='top_secret'
            )

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
        translation.activate('en-us')
        self.setUp_client()
        self.setUp_validating()
        self.setUp_voting()
        self.setUp_keywords()
        self.setUp_image()

    def test_get(self):
        response = self.client.get(reverse('tasks/validate'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('tasks/vote'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('tasks/contro'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('tasks/keywords'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('tasks/image'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

    def test_post_validate_new_data(self):
        assignments = []
        for val in self.validating[:10]:
            assignment = Assignment.objects.create(tasker=self.user, task=val)
            assignments.append(assignment)

        new_id = self.validating[5].id
        data = {"validate_ids": new_id,
                "approve_value_{}".format(new_id): 'false',
                "new_ans_{}".format(new_id): 'New Answer'}
        response = self.client.post(path=reverse('tasks/validate'),
                                    data=data,
                                    follow=True, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.client.session)
        self.assertIn('validate_ids', response.client.session['data'])
        data = response.client.session['data']['validate_ids']
        expected_data = str(new_id)
        self.assertEqual(data, expected_data)

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
        response = self.client.post(path=reverse('tasks/validate'),
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
        response = self.client.post(path=reverse('tasks/validate'),
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
        response = self.client.post(path=reverse('tasks/validate'),
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

        response = self.client.post(path=reverse('tasks/validate'),
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

    def test_post_validate_fail(self):
        session = self.client.session
        ids = [103, 459, 380]
        session['data'] = {"validate_ids": ids}
        for id in ids:
            session['data']['approve_value_{}'.format(id)] = 'true'
        session.save()

        data = {"submit": 'Submit'}
        data['validate_ids'] = ids
        response = self.client.post(path=reverse('tasks/validate'),
                                    data=data,
                                    follow=True, format='json')
        self.assertEqual(response.status_code, 200)
        messages = [str(msg) for msg in get_messages(response.wsgi_request)]
        for id in ids:
            self.assertIn(MSG_FAIL_DATA_NONEXIST.format(id), messages)

    def test_post_vote(self):
        vote = self.active_voting[0]
        choice = vote.choice_set.all()[1]
        assignment = Assignment.objects.create(tasker=self.user, task=vote)
        self.assertEqual(choice.num_votes, 0)
        self.assertFalse(assignment.done)
        response = self.client.post(path=reverse('vote_post', args=(vote.id,)),
                                    data={"choice": [choice.id]}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Choice.objects.get(pk=choice.id).num_votes, 1)
        self.assertTrue(Assignment.objects.get(pk=assignment.pk).done)

    def test_post_vote_fail(self):
        response = self.client.post(path=reverse('vote_post', args=(100,)),
                                    data={"choice": [0]}, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = [str(msg) for msg in get_messages(response.wsgi_request)]
        self.assertEqual(MSG_FAIL_DATA_NONEXIST.format(100), messages[0])

        vote = self.active_voting[0]
        response = self.client.post(path=reverse('vote_post', args=(vote.id,)),
                                   data={"choice": [999]}, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = [str(msg) for msg in get_messages(response.wsgi_request)]
        self.assertEqual(MSG_FAIL_CHOICE, messages[0])

    def test_post_final_vote(self):
        vote = self.active_voting[1]
        vote.num_votes = 4
        vote.save()
        choice = vote.choice_set.all()[2]
        choice.num_votes = 4
        choice.save()
        self.assertEqual(choice.num_votes, 4)

        response = self.client.post(path=reverse('vote_post', args=(vote.id,)),
                                    data={"choice": [choice.id]}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(FinalizedData.objects.get(pk=vote.pk))
        self.assertIsNone(VotingData.objects.filter(pk=vote.pk).first())
        self.assertIsNone(Choice.objects.filter(data=vote.id).first())

    def test_post_final_vote_2(self):
        vote = self.active_voting[2]
        vote.num_votes = 4
        vote.save()
        first_choice = vote.choice_set.all()[0]
        first_choice.num_votes = 2
        first_choice.save()
        second_choice = vote.choice_set.all()[1]
        second_choice.num_votes = 2
        second_choice.save()

        response = self.client.post(path=reverse('vote_post', args=(vote.id,)),
                                    data={"choice": [first_choice.id]}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(FinalizedData.objects.get(pk=vote.pk))
        self.assertEqual(FinalizedData.objects.get(pk=vote.pk).answer_text, first_choice.answer)
        self.assertIsNone(VotingData.objects.filter(pk=vote.pk).first())
        self.assertIsNone(Choice.objects.filter(data=vote.id).first())

    def test_post_final_vote_tie(self):
        vote = self.active_voting[3]
        vote.num_votes = 4
        vote.save()
        first_choice = vote.choice_set.all()[0]
        first_choice.num_votes = 2
        first_choice.save()
        second_choice = vote.choice_set.all()[1]
        second_choice.num_votes = 2
        second_choice.save()

        response = self.client.post(path=reverse('vote_post', args=(vote.id,)),
                                    data={"choice": [vote.choice_set.all()[2].id]}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(FinalizedData.objects.filter(pk=vote.pk).first())
        self.assertIsNotNone(VotingData.objects.filter(pk=vote.pk).first())
        self.assertEqual(Assignment.objects.filter(task=vote, done=False).count(), 2)

    def test_post_vote_err(self):
        vote = self.active_voting[3]
        response = self.client.post(path=reverse('vote_post', args=(vote.id,)),
                                    data={"choice": [""]}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(FinalizedData.objects.filter(pk=vote.pk).first())
        self.assertIsNotNone(VotingData.objects.filter(pk=vote.pk).first())

        response = self.client.post(path=reverse('vote_post', args=(vote.id,)),
                                    data={"choice": [10081]}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(FinalizedData.objects.filter(pk=vote.pk).first())
        self.assertIsNotNone(VotingData.objects.filter(pk=vote.pk).first())

    def test_post_keywords(self):
        keywords = self.finalized[0]
        keywords.title = "This is a question."
        keywords.answer_text = "This is an answer ."
        keywords.save()
        assignment = Assignment.objects.create(tasker=self.user, task=keywords)
        self.assertEqual(keywords.qns_keywords, "")
        self.assertEqual(keywords.ans_keywords, "")

        response = self.client.post(path=reverse('keywords', args=(keywords.id,)),
                                    data={
                                        "qns_keywords": 'This,a,',
                                        "ans_keywords": 'This,answer,.,',
                                    }, follow=True)
        self.assertEqual(response.status_code, 200)
        keywords = FinalizedData.objects.get(pk=keywords.pk)
        self.assertEqual(keywords.qns_keywords, 'This,a,')
        self.assertEqual(keywords.ans_keywords, 'This,answer,.,')
        self.assertTrue(Assignment.objects.get(pk=assignment.pk).is_done)

        response = self.client.post(path=reverse('keywords', args=(keywords.id,)),
                                    data={
                                        "qns_keywords": 'question.,',
                                        "ans_keywords": 'is,',
                                    }, follow=True)
        self.assertEqual(response.status_code, 200)
        keywords = FinalizedData.objects.get(pk=keywords.pk)
        self.assertEqual(keywords.qns_keywords, 'This,a,question.,')
        self.assertEqual(keywords.ans_keywords, 'This,answer,.,is,')
        self.assertTrue(Assignment.objects.get(pk=assignment.pk).is_done)

    def test_post_keywords_invalid(self):
        response = self.client.post(path=reverse('keywords', args=(999,)),
                                    data={
                                        "qns_keywords": 'This,a,',
                                        "ans_keywords": 'This,answer,.,',
                                    }, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(MSG_FAIL_DATA_NONEXIST.format(999), str(messages[0]))

    def test_post_image(self):
        img = self.images[0]
        label = img.imagelabel_set.all()[1]
        assignment = Assignment.objects.create(tasker=self.user, task=img)
        self.assertEqual(label.num_votes, 0)
        self.assertFalse(assignment.done)

        response = self.client.post(path=reverse('image', args=(img.id,)), data={"select_label": [label.id]}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ImageLabel.objects.get(pk=label.id).num_votes, 1)
        self.assertTrue(Assignment.objects.get(pk=assignment.pk).done)

    def test_post_final_image(self):
        img = self.images[1]
        img.num_votes = 4
        img.save()
        label = img.imagelabel_set.all()[2]
        label.num_votes = 4
        label.save()
        self.assertEqual(label.num_votes, 4)
        response = self.client.post(path=reverse('image', args=(img.id,)), data={"select_label": [label.id]}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(FinalizedImageData.objects.get(pk=img.pk))
        self.assertEqual(FinalizedImageData.objects.get(pk=img.pk).label, label.label)
        self.assertIsNone(ImageData.objects.filter(pk=img.pk).first())
        self.assertIsNone(ImageLabel.objects.filter(pk=label.id).first())

    def test_post_final_image_2(self):
        img = self.images[2]
        img.num_votes = 4
        img.save()
        first_abel = img.imagelabel_set.all()[0]
        first_abel.num_votes = 2
        first_abel.save()
        second_label = img.imagelabel_set.all()[1]
        second_label.num_votes = 2
        second_label.save()

        response = self.client.post(path=reverse('image', args=(img.id,)), data={"select_label": [first_abel.id]}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(FinalizedImageData.objects.get(pk=img.pk))
        self.assertEqual(FinalizedImageData.objects.get(pk=img.pk).label, first_abel.label)
        self.assertIsNone(ImageData.objects.filter(pk=img.pk).first())
        self.assertIsNone(ImageLabel.objects.filter(image=img).first())

    def test_post_final_image_tie(self):
        img = self.images[3]
        img.num_votes = 4
        img.save()
        first_abel = img.imagelabel_set.all()[0]
        first_abel.num_votes = 2
        first_abel.save()
        second_label = img.imagelabel_set.all()[1]
        second_label.num_votes = 2
        second_label.save()

        label = img.imagelabel_set.all()[2]
        response = self.client.post(path=reverse('image', args=(img.id,)), data={"select_label": [label.id]}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(FinalizedImageData.objects.filter(pk=img.pk).first())
        self.assertIsNotNone(ImageData.objects.filter(pk=img.pk).first())
        self.assertEqual(Assignment.objects.filter(task=img, done=False).count(), 2)

    def test_post_image_invalid(self):
        img = self.images[0]
        label = img.imagelabel_set.all()[0]

        response = self.client.post(path=reverse('image', args=(999,)), data={"select_label": [label.id]}, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn(MSG_FAIL_DATA_NONEXIST.format(999), str(messages[0]))

        response = self.client.post(path=reverse('image', args=(img.id,)), data={"select_label": [999]}, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn(MSG_FAIL_LABEL_NONEXIST.format(999), str(messages[0]))

    def test_retry_sign_up(self):
        rejected_client = Client()
        rejected_user = CustomUser.objects.create_admin(
            username='rejected', email='rejected@gmail.com', certificate="G11111M",
            group=self.group, password='top_secret')
        rejected_user.approve(False)
        rejected_client.login(username=rejected_user.email, password='top_secret')

        rejected_client.post(path=reverse('retry_sign_up'), follow=True)
        self.assertIsNone(CustomUser.objects.get(pk=rejected_user.pk).is_approved)


class AdminViewTestCase(TestCase):
    def setUp_client(self):
        self.admin_client = Client()
        self.group, _ = CustomGroup.objects.update_or_create(name="KKH")
        self.groups = [self.group]
        for i in range(5):
            group = CustomGroup.objects.create(name="Group{}".format(i))
            self.groups.append(group)
        self.admin = CustomUser.objects.create_admin(
            username='admin', email='admin@gmail.com', certificate="G11111M",
            group=self.group, password='top_secret')
        self.admin_client.login(username=self.admin.email, password='top_secret')

        self.super_client = Client()
        self.superuser = CustomUser.objects.create_superuser(
            username="superuser", email="superuser@gmail.com", certificate="G00000M", password="superuser"
        )
        self.super_client.login(username=self.superuser.email, password='superuser')

    def setUp_users(self):
        self.users = []
        for i, group in enumerate(self.groups):
            for j in range(10):
                user = CustomUser.objects.create_user(
                    username='G{}_User{}'.format(i, j), email='G{}_User{}@gmail.com'.format(i, j),
                    certificate="G12345{}{}M".format(i, j), group=group, password='top_secret'
                )
                user.approve(True)
                self.users.append(user)

    def setUp_data(self):
        self.data = []
        for i, group in enumerate(self.groups):
            for j in range(10):
                data, _ = FinalizedData.objects.update_or_create(title=j, answer_text=j, group=group)
                self.data.append(data)

    def setUp(self) -> None:
        translation.activate('en-us')
        self.setUp_client()

    def get_csv(self, response):
        content = b''.join(response.streaming_content).decode("utf-8")
        csv_reader = csv.reader(io.StringIO(content))
        body = list(csv_reader)
        headers = body.pop(0)

        return headers, body

    def test_admin_get(self):
        response = self.admin_client.get(reverse('modify_users'))
        self.assertEqual(response.status_code, 200)

        response = self.admin_client.get(reverse('dataset'))
        self.assertEqual(response.status_code, 200)

        response = self.super_client.get(reverse('dataset'))
        self.assertEqual(response.status_code, 200)

        response = self.admin_client.get(reverse('update'))
        self.assertEqual(response.status_code, 200)

        response = self.admin_client.get(reverse('update'), data={'search': 'keyword'})
        self.assertEqual(response.status_code, 200)

        response = self.admin_client.get(reverse('report'))
        self.assertEqual(response.status_code, 200)

        response = self.super_client.get(reverse('report'))
        self.assertEqual(response.status_code, 200)

        response = self.admin_client.get(reverse('log'))
        self.assertEqual(response.status_code, 200)

        response = self.super_client.get(reverse('group'))
        self.assertEqual(response.status_code, 200)

        response = self.super_client.get(reverse('group_details', args=(self.group.name,)))
        self.assertEqual(response.status_code, 200)

    def test_post_modify_users(self):
        self.setUp_users()
        user = CustomUser.objects.create_user(
            username="random", email="random@gmail.com",
            certificate="G123446M", password="randompwd", group=self.group)
        self.assertIsNone(user.is_approved)

        # approve
        print(reverse('modify_users'))
        response = self.admin_client.post(path=reverse('modify_users'),
                                          data={"approve": "1", "id": user.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(CustomUser.objects.get(pk=user.pk).is_approved)

        # deactivate
        response = self.admin_client.post(path=reverse('modify_users'),
                                          data={"deactivate": "1", "id": user.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CustomUser.objects.get(pk=user.pk).is_active)

        # activate
        response = self.admin_client.post(path=reverse('modify_users'),
                                          data={"activate": "1", "id": user.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(CustomUser.objects.get(pk=user.pk).is_active)

        # reject
        user2 = CustomUser.objects.create_user(
            username="random2", email="random2@gmail.com",
            certificate="G123456M", password="randompwd", group=self.group)
        self.assertIsNone(user2.is_approved)

        response = self.admin_client.post(path=reverse('modify_users'),
                                          data={"reject": "1", "id": user2.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CustomUser.objects.get(pk=user2.pk).is_approved)

        # is admin
        response = self.super_client.post(path=reverse('modify_users'),
                                          data={"is_admin": "1", "id": user.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(CustomUser.objects.get(pk=user.pk).is_admin)

        # is not admin
        response = self.super_client.post(path=reverse('modify_users'),
                                          data={"id": user.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CustomUser.objects.get(pk=user.pk).is_admin)

    def test_update(self):
        vote = VotingData.objects.create(title="vote", group=self.group)
        choices = []
        for i in range(3):
            choice = Choice.objects.create(data=vote, answer="ans{}".format(i))
            choices.append(choice)

        selected_choice = choices[0]
        response = self.admin_client.post(path=reverse("update", args=(vote.id, )),
                                          data={"choice": str(selected_choice.id)}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(FinalizedData.objects.filter(title=vote.title, answer_text=selected_choice.answer,
                                                          group=vote.group).first())
        self.assertIsNone(VotingData.objects.filter(title=vote.title, group=self.group).first())

        vote = VotingData.objects.create(title="vote2", group=self.group)
        choices = []
        for i in range(3):
            choice = Choice.objects.create(data=vote, answer="ans{}".format(i))
            choices.append(choice)
        response = self.admin_client.post(path=reverse("update", args=(vote.id,)),
                                          data={"choice": ""}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(FinalizedData.objects.filter(title=vote.title, group=vote.group).first())
        self.assertIsNotNone(VotingData.objects.filter(title=vote.title, group=vote.group).first())

    def test_assign_contro(self):
        self.setUp_users()
        vote = VotingData.objects.create(title="vote", group=self.group)
        choices = []
        for i in range(3):
            choice = Choice.objects.create(data=vote, answer="ans{}".format(i), num_votes=6)
            choices.append(choice)
        vote.num_votes = 3 * 6
        vote.save()
        for user in self.users:
            Assignment.objects.create(tasker=user, task=vote, done=True)
        tasker = self.users[0]

        response = self.admin_client.post(path=reverse("assign_contro"),
                                          data={"select_list": vote.id, 'assign_tasker': tasker.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(VotingData.objects.get(id=vote.id).is_active)
        self.assertEqual(Assignment.objects.filter(task=vote).exclude(tasker=tasker).count(), 0)
        self.assertEqual(Assignment.objects.filter(task=vote, tasker=tasker, done=False).count(), 1)

    def test_download_dataset(self):
        self.setUp_data()

        # super_admin
        response = self.super_client.post(path=reverse("download_dataset"))
        self.assertEqual(response.status_code, 200)
        headers, body = self.get_csv(response)
        self.assertEqual(headers, ["id", "question", "qns_keywords", "answer", "ans_keywords"])
        expected_body = [[str(u.id), str(u.title), str(u.qns_keywords.split(',')),
                          str(u.answer_text), str(u.ans_keywords.split(','))] for u in self.data]
        self.assertEqual(len(body), len(expected_body))
        for b in body:
            self.assertIn(b, expected_body)

        # admin
        response = self.admin_client.post(path=reverse("download_dataset"))
        self.assertEqual(response.status_code, 200)
        headers, body = self.get_csv(response)
        self.assertEqual(headers, ["id", "question", "qns_keywords", "answer", "ans_keywords"])
        expected_body = [[str(u.id), str(u.title), str(u.qns_keywords.split(',')),
                          str(u.answer_text), str(u.ans_keywords.split(','))] for u in self.data
                         if u.group == self.admin.group]
        self.assertEqual(len(body), len(expected_body))
        for b in body:
            self.assertIn(b, expected_body)

    def test_download_report(self):
        self.setUp_users()

        # super_admin
        response = self.super_client.post(path=reverse("download_report"))
        self.assertEqual(response.status_code, 200)
        headers, body = self.get_csv(response)
        self.assertEqual(headers, ['id', 'username', 'certificate', 'point', 'accuracy'])
        expected_body = [[str(u.id), str(u.username), str(u.certificate), str(u.point), str(u.accuracy())]
                         for u in self.users if u.is_approved]
        expected_body.append([str(self.admin.id), self.admin.username, self.admin.certificate,
                              str(self.admin.point), str(self.admin.accuracy())])
        self.assertEqual(len(body), len(expected_body))
        for b in body:
            self.assertIn(b, expected_body)

        # admin
        response = self.admin_client.post(path=reverse("download_report"))
        self.assertEqual(response.status_code, 200)
        headers, body = self.get_csv(response)
        self.assertEqual(headers, ['id', 'username', 'certificate', 'point', 'accuracy'])
        expected_body = [[str(u.id), str(u.username), str(u.certificate), str(u.point), str(u.accuracy())] for u in self.users
                         if u.is_approved and u.group == self.admin.group]
        self.assertEqual(len(body), len(expected_body))
        for b in body:
            self.assertIn(b, expected_body)

    def test_import_dataset(self):
        str = "qns,ans\r\n"
        data_len = 3
        expected_data = []
        for i in range(data_len):
            str += "Q{}, A{}\r\n".format(i, i)
            expected_data.append(
                ValidatingData.create(title="Q{}".format(i), ans="A{}".format(i), group=self.admin.group))
        csv_file = SimpleUploadedFile("file.csv", str.encode('UTF-8'), content_type="text/csv")
        self.admin_client.post(path=reverse("import_dataset"), data={'file': csv_file, 'qns_col': 0, 'ans_col': 1})
        data = [data for data in ValidatingData.objects.all()]
        self.assertEqual(expected_data, data)

    def test_import_dataset_fail(self):
        response = self.admin_client.post(path=reverse("import_dataset"), data={'qns_col': 0, 'ans_col': 1})
        messages = list(get_messages(response.wsgi_request))
        self.assertNotEqual(len(messages), 0)

        str = "qns,ans\r\n"
        data_len = 3
        expected_data = []
        for i in range(data_len):
            str += "Q{}, A{}\r\n".format(i, i)
            expected_data.append(
                ValidatingData.create(title="Q{}".format(i), ans="A{}".format(i), group=self.admin.group))
        csv_file = SimpleUploadedFile("file.csv", str.encode('UTF-8'), content_type="text/csv")
        response = self.admin_client.post(path=reverse("import_dataset"), data={'file': csv_file, 'ans_col': 1})
        messages = list(get_messages(response.wsgi_request))
        self.assertNotEqual(len(messages), 0)

        str = "qns,ans\r\n"
        data_len = 3
        expected_data = []
        for i in range(data_len):
            str += "Q{}, A{}\r\n".format(i, i)
            expected_data.append(
                ValidatingData.create(title="Q{}".format(i), ans="A{}".format(i), group=self.admin.group))
        txt = SimpleUploadedFile("file.txt", str.encode('UTF-8'), content_type="text/csv")
        response = self.admin_client.post(path=reverse("import_dataset"), data={'file': txt, 'qns_col': 0, 'ans_col': 1})
        messages = list(get_messages(response.wsgi_request))
        self.assertNotEqual(len(messages), 0)

    def test_assign_tasks(self):
        validating = []
        for i in range(20):
            data = ValidatingData.create(group=self.group, title="Title{}".format(i), ans="Answer{}".format(i))
            validating.append(data)

        new_group, _ = CustomGroup.objects.update_or_create(name="others")
        for i in range(20):
            data = ValidatingData.create(group=new_group, title="Title{}".format(i), ans="Answer{}".format(i))
            validating.append(data)

        for i in range(10):
            user = CustomUser.objects.create_user(
                username='User{}'.format(i), email='User{}@gmail.com'.format(i),
                certificate="G12345{}M".format(i), group=self.group, password='top_secret'
            )
            user.approve(True)

        response = self.admin_client.post(path=reverse("assign_tasks"), HTTP_REFERER='/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Assignment.objects.all().count(), Assignment.objects.distinct('tasker_id', 'task_id').count())

    def test_summarize(self):
        self.setUp_users()
        self.setUp_data()

        expected = {}
        for i, user in enumerate(self.users):
            if (user.group != self.admin.group):
                continue
            tasks = [task for task in self.data if task.group == user.group]
            num_ans = 0
            point = 0
            correct_num_ans = 0
            timestamp = "2000-01-01 23:59"
            for j, task in enumerate(tasks):
                num_ans += 1
                if j % 2 == 0:
                    Log.objects.create(user=user, task=task, action=VOT, response="Random", timestamp=timestamp)
                    point += INCORRECT_POINT
                else:
                    Log.objects.create(user=user, task=task, action=VOT, response=task.answer_text, timestamp=timestamp)
                    correct_num_ans += 1
                    point += CORRECT_POINT
            expected[user.id] = {'num_ans': num_ans, 'point': point, 'correct_num_ans': correct_num_ans}

        response = self.admin_client.post(path=reverse("summarize"), HTTP_REFERER='/', follow=True)
        self.assertEqual(response.status_code, 200)
        for user in self.users:
            if (user.group != self.admin.group):
                continue
            self.assertEqual(CustomUser.objects.get(id=user.id).num_ans, expected[user.id]['num_ans'])
            self.assertEqual(CustomUser.objects.get(id=user.id).correct_num_ans, expected[user.id]['correct_num_ans'])
            self.assertEqual(CustomUser.objects.get(id=user.id).point, expected[user.id]['point'])

    def test_create_group(self):
        form_data = {'name': 'new group'}
        form = CreateGroupForm(data=form_data)
        self.assertTrue(form.is_valid())

        response = self.super_client.post(path=reverse('create_group'), data=form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(CustomGroup.objects.filter(name='new group').first())

    def test_create_group_invalid(self):
        form_data = {'name': self.group.name}
        form = CreateGroupForm(data=form_data)
        self.assertFalse(form.is_valid())
        response = self.super_client.post(path=reverse('create_group'), data=form_data, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_delete_group(self):
        name = 'group_deleted'
        group = CustomGroup.objects.create(name=name)
        response = self.super_client.post(path=reverse('delete_group'),
                                          data={'input': name, 'confirm_input': name},
                                          follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(CustomGroup.objects.filter(name=name).first())

        name = 'group_undeleted'
        group = CustomGroup.objects.create(name=name)
        response = self.super_client.post(path=reverse('delete_group'),
                                          data={'input': name, 'confirm_input': name + "wrong"},
                                          follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(CustomGroup.objects.filter(name=name).first())


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
        self.inactive_voting_data = []
        self.assigned_voting_data = []
        self.unassigned_voting_data = []
        self.controversial_data = []
        # active voting data
        for q in range(20):
            voting_data = VotingData.create(title=q, group=self.group, is_active=True)
            self.active_voting_data.append(voting_data)
            for a in range(3):
                choice, _ = Choice.objects.update_or_create(data=voting_data, answer=a, num_votes=0)
            if q % 3 == 0:
                voting_data.num_votes = q * 5
                voting_data.save()
                if q * 5 > 15:
                    voting_data.is_contro = True
                    voting_data.save()
                    self.controversial_data.append(voting_data)
        # inactive voting data
        for q in range(20, 30):
            voting_data = VotingData.create(title=q, group=self.group, is_active=False)
            for a in range(3):
                choice, _ = Choice.objects.update_or_create(data=voting_data, answer=a, num_votes=0)
            self.inactive_voting_data.append(voting_data)
        self.num_vote_kkh = 30

        # active other group data
        for q in range(5):
            voting_data = VotingData.create(title=q, group=self.other_group, is_active=True)
            for a in range(3):
                choice, _ = Choice.objects.update_or_create(data=voting_data, answer=a, num_votes=0)
            self.unassigned_voting_data.append(voting_data)
            voting_data.num_votes = q * 7
            voting_data.save()
            if q * 7 > 15:
                voting_data.is_contro = True
                voting_data.save()
                self.controversial_data.append(voting_data)

        self.num_vote_other = 5

        self.num_todo = 0
        self.num_done = 0
        for i, data in enumerate(self.active_voting_data):
            if i > 10:
                if i % 2 == 0:
                    Assignment.objects.update_or_create(tasker=self.user, task=data, done=False)
                    self.assigned_voting_data.append(data)
                    self.num_todo += 1
                else:
                    Assignment.objects.update_or_create(tasker=self.user, task=data, done=True)
                    self.assigned_voting_data.append(data)
                    self.num_done += 1
            elif i < 5:
                Assignment.objects.update_or_create(tasker=self.other_user, task=data, done=False)
            else:
                self.unassigned_voting_data.append(data)
        for i, data in enumerate(self.inactive_voting_data):
            if i % 2 == 0:
                Assignment.objects.update_or_create(tasker=self.user, task=data, done=False)
            else:
                Assignment.objects.update_or_create(tasker=self.other_user, task=data, done=False)

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
        translation.activate('en-us')
        self.factory = RequestFactory()
        self.setUp_auth()
        self.setUp_vote()
        self.setUp_finalized()

    def test_get_assigned_tasks_context(self):
        data, task_num = get_assigned_tasks_context(self.user, VotingData, condition=(lambda x: x.is_active))
        expected_data = self.assigned_voting_data
        expected_task_num = {
            'todo': self.num_todo,
            'done': self.num_done,
            'total': self.num_todo + self.num_done,
        }

        self.assertEqual(len(data), len(expected_data))
        self.assertEqual(set(data), set(expected_data))
        self.assertEqual(task_num, expected_task_num)

    def test_get_group_report_context(self):
        data = get_group_report_context()
        expected_data = {
            'names': [self.group.name, self.other_group.name],
            'points': [0, 0],
            'num_ans': [0, 0],
            'accuracy': [1, 1],
        }
        self.assertEqual(data, expected_data)

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

    def test_get_controversial_voting_data(self):
        data = get_controversial_voting_data(self.group)
        expected_data = []
        for d in self.controversial_data:
            if d.group == self.group:
                expected_data.append(d)
        self.assertEqual(len(data), len(expected_data))
        self.assertEqual(set(data), set(expected_data))

        data = get_controversial_voting_data()
        self.assertEqual(len(data), len(self.controversial_data))
        self.assertEqual(set(data), set(self.controversial_data))

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
                "created_at": self.group.created_at,
                "updated_at": self.group.updated_at,
                "user": self.num_kkh,
                "data": self.num_vote_kkh,
            },
            {
                "name": self.other_group.name,
                "created_at": self.other_group.created_at,
                "updated_at": self.other_group.updated_at,
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


class ViewsTestCase(TestCase):
    def setUp(self) -> None:
        translation.activate('en-us')
        self.group, _ = CustomGroup.objects.update_or_create(name="KKH")

        self.admin_client = Client()
        self.admin = CustomUser.objects.create_admin(
            username='admin', email='admin@gmail.com', certificate="G11111M",
            group=self.group, password='top_secret')
        self.admin_client.login(username=self.admin.email, password='top_secret')

        self.super_client = Client()
        self.superuser = CustomUser.objects.create_superuser(
            username="superuser", email="superuser@gmail.com", certificate="G00000M", password="superuser"
        )
        self.super_client.login(username=self.superuser.email, password='superuser')

        self.user_client = Client()
        self.user = CustomUser.objects.create_user(
            username="user", email='user@gmail.com', certificate="G12355M", password="user", group=self.group
        )
        self.user_client.login(username=self.user.email, password="user")

    def test_help(self):
        response = self.admin_client.get(reverse('help'))
        self.assertEqual(response.status_code, 200)

        response = self.super_client.get(reverse('help'))
        self.assertEqual(response.status_code, 200)

        response = self.user_client.get(reverse('help'))
        self.assertEqual(response.status_code, 200)