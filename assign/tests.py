from django.test import TestCase
from math import floor

from .views import assign, NUM_USER_PER_TASK, PREDEFINED_MAX
from .models import Assignment
from pages.models.validate import ValidatingData
from authentication.models import CustomGroup, CustomUser


class UserViewTestCase(TestCase):
    def setUp(self) -> None:
        self.num_user = 3
        self.num_data = 10
        self.all_users = []
        self.all_tasks = []
        group = CustomGroup.objects.create(name="group")
        for i in range(self.num_user):
            user = CustomUser.objects.create_user(
                username='user{}'.format(i), email='alice{}@gmail.com'.format(i), certificate="G12345{}M".format(i),
                group=group, password='top_secret')
            self.all_users.append(user)
        for i in range(self.num_data):
            data = ValidatingData.create("title{}".format(i), group, "ans")
            self.all_tasks.append(data)

    def test_assign(self):
        assign(self.all_users, Assignment, self.all_tasks)
        self.assertEqual(Assignment.objects.count(), Assignment.objects.distinct('task_id', 'tasker_id').count())

    def test_assign_task(self):
        assign(self.all_users, Assignment, self.all_tasks, num_task_per_user=2)
        self.assertEqual(Assignment.objects.count(), Assignment.objects.distinct('task_id', 'tasker_id').count())

    def test_assign_user(self):
        assign(self.all_users, Assignment, self.all_tasks, num_user_per_task=2)
        self.assertEqual(Assignment.objects.count(), Assignment.objects.distinct('task_id', 'tasker_id').count())

    def test_assign_fail(self):
        assign([], Assignment, self.all_tasks)
        self.assertEqual(Assignment.objects.count(), 0)

    def test_reassign(self):
        task = self.all_tasks[0]
        Assignment.objects.create(task=task, tasker=self.all_users[0])
        num = Assignment.objects.filter(task=task).count()
        self.assertTrue(Assignment.reassign(task, all_users=self.all_users))
        self.assertEqual(Assignment.objects.filter(task=task).count(), num + 2)

    def test_reassign_fail(self):
        task = self.all_tasks[0]
        for user in self.all_users:
            Assignment.objects.create(task=task, tasker=user)
        num = Assignment.objects.filter(task=task).count()
        self.assertFalse(Assignment.reassign(task, all_users=self.all_users))
        self.assertEqual(Assignment.objects.filter(task=task).count(), num)

    def test_is_done(self):
        assignment = Assignment.objects.create(task=self.all_tasks[0], tasker=self.all_users[0])
        self.assertFalse(assignment.done)
        assignment.is_done()
        self.assertTrue(assignment.done)