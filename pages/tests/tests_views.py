from django.core.paginator import Paginator
from django.test import TestCase, RequestFactory
from pages.models.image import ImageData, ImageLabel, FinalizedImageData
from pages.models.vote import VotingData, Choice
from pages.models.models import FinalizedData
from authentication.models import CustomGroup, CustomUser
from assign.models import Assignment

from pages.views.user import image
from pages.views.utils import get_assigned_tasks_context, get_finalized_data, get_unassigned_voting_data, \
    get_num_per_group_dict, get_group_info_context


class ImageDataTestCase(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.group, _ = CustomGroup.objects.update_or_create(name="KKH")
        self.user = CustomUser.objects.create_user(
            username='alice', email='alice@gmail.com', certificate="G123456M", group=self.group, password='top_secret')

    def test_details(self):
        request = self.factory.get('/tasks/image')
        request.user = self.user

        response = image(request)

        self.assertEqual(response.status_code, 200)
        print(request)


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
        for q in range(10):
            voting_data = VotingData.create(title=q, group=self.group, is_active=False)
            for a in range(3):
                choice, _ = Choice.objects.update_or_create(data=voting_data, answer=a, num_votes=0)
        self.num_vote_kkh = 20 + 10

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
        expected_data = self.unassigned_voting_data[5:]
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