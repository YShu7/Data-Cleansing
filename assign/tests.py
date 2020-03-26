from django.contrib.auth import get_user_model
from django.test import TestCase

from .views import assign
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
        return

    def test_assign(self):
        assign(self.all_users, Assignment, self.all_tasks)
        self.assertEqual(len(self.all_tasks), self.num_data)
        self.assertEqual(len(self.all_users), self.num_user)
        self.assertEqual(Assignment.objects.count(), 10*3)