from django.test import TestCase

from .models import CustomUser, CustomGroup
from .utils import get_group_report, get_pending_users, get_approved_users


class UtilsTestCase(TestCase):
    def setUp(self) -> None:
        self.num_ans_0 = 0
        self.correct_num_ans_0 = 0
        self.point_0 = 0
        self.groups = []
        self.all_pending_user = []
        self.all_approved_user = []
        for i in range(5):
            group, _ = CustomGroup.objects.update_or_create(name="Group{}".format(i))
            self.groups.append(group)
            for j in range(3):
                user = CustomUser.objects.create_user(
                    username='User{}{}'.format(i, j), email='User{}{}@gmail.com'.format(i, j),
                    certificate="G1234{}{}M".format(i, j), group=group, password='top_secret'
                )
                if j % 2 == 0:
                    user.approve(True)
                    self.all_approved_user.append(user)
                    if j == 0:
                        user.activate(False)
                else:
                    self.all_pending_user.append(user)
                if i == 0:
                    user.num_ans = j * 2 + 10
                    user.correct_num_ans = j
                    user.point = j * 3 + 5
                    user.save()
                    if user.is_approved and user.is_active:
                        self.num_ans_0 += user.num_ans
                        self.correct_num_ans_0 += user.correct_num_ans
                        self.point_0 += user.point

    def test_get_group_report(self):
        report = get_group_report(self.groups[0])
        expected_report = {
            "num_ans": self.num_ans_0,
            "point": self.point_0,
            "accuracy": self.correct_num_ans_0 / self.num_ans_0
        }
        self.assertEqual(report, expected_report)

    def test_get_pending_users(self):
        users = get_pending_users(group=self.groups[0])
        self.assertEqual(list(users), [u for u in self.all_pending_user if u.group == self.groups[0]])

        users = get_pending_users(group=None)
        self.assertEqual(list(users), self.all_pending_user)

    def test_get_approved_users(self):
        users = get_approved_users(group=self.groups[0])
        self.assertEqual(list(users), [u for u in self.all_approved_user if u.group == self.groups[0]])

        users = get_approved_users(group=None)
        self.assertEqual(list(users), self.all_approved_user)