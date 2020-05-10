from django.test import TestCase, Client
from django.urls import reverse
from django.utils import translation

from .forms import CustomUserCreationForm, CustomPasswordChangeForm
from .models import CustomUser, CustomGroup, Log
from .utils import get_group_report, get_pending_users, get_approved_users, get_log_msg, log
from .templatetags import filter
from datacleansing.settings import CORRECT_POINT, INCORRECT_POINT


class ModelsTestCase(TestCase):
    def setUp(self) -> None:
        translation.activate('en')
        self.group = CustomGroup.objects.create(name="group")

    def test_group(self):
        self.group.updated()
        self.assertNotEqual(self.group.created_at, self.group.updated_at)

    def test_user(self):
        user = CustomUser.objects.create_user(email="user@gmail.com", username="user",
                                              certificate="G123456M", password="user", group=self.group)
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertIsNone(user.is_approved)

        admin = CustomUser.objects.create_admin(email="admin@gmail.com", username="admin",
                                                certificate="G123457M", password="admin", group=self.group)
        self.assertTrue(admin.is_admin)
        self.assertFalse(admin.is_superuser)
        self.assertTrue(admin.is_active)
        self.assertTrue(admin.is_approved)

        superuser = CustomUser.objects.create_superuser(email="superuser@gmail.com", username="superuser",
                                                        certificate="G123458M", password="user")
        self.assertFalse(superuser.is_admin)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_approved)

        user.approve(True)
        self.assertTrue(user.is_approved)

        user.activate(False)
        self.assertFalse(user.is_active)

        user.assign_admin(True)
        self.assertTrue(user.is_admin)
        admin.assign_admin(False)
        self.assertFalse(admin.is_admin)

    def test_accuracy(self):
        user = CustomUser.objects.create_user(email="user@gmail.com", username="user",
                                              certificate="G123456M", password="user", group=self.group)
        user.correct_num_ans = 1
        user.num_ans = 5
        self.assertEqual(user.accuracy(), user.correct_num_ans / user.num_ans)

        user = CustomUser.objects.create_user(email="user1@gmail.com", username="user",
                                              certificate="G223456M", password="user", group=self.group)
        self.assertEqual(user.accuracy(), 1)

    def test_ans_is(self):
        user = CustomUser.objects.create_user(email="user@gmail.com", username="user",
                                              certificate="G123456M", password="user", group=self.group)

        point = user.point
        num_ans = user.num_ans
        num_correct_ans = user.correct_num_ans

        user.ans_is(True)
        self.assertEqual(user.point, point + CORRECT_POINT)
        self.assertEqual(user.num_ans, num_ans + 1)
        self.assertEqual(user.correct_num_ans, num_correct_ans + 1)

        user.ans_is(False)
        self.assertEqual(user.point, point + CORRECT_POINT + INCORRECT_POINT)
        self.assertEqual(user.num_ans, num_ans + 2)
        self.assertEqual(user.correct_num_ans, num_correct_ans + 1)


class ViewTestCase(TestCase):
    def setUp(self) -> None:
        translation.activate('en')
        self.group = CustomGroup.objects.create(name="group")
        self.client = Client()

    def test_signup(self):
        form_data = {'email': 'user@gmail.com',
                     'username': 'user',
                     'certificate': 'G1234567M',
                     'password1': 'dsajkflsi&)(3',
                     'password2': 'dsajkflsi&)(3',
                     'group': self.group.pk}

        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        response = self.client.post(path=reverse('signup'), data=form_data, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_signup_invalid(self):
        form_data = {'email': 'user@gmail.com',
                     'username': 'user',
                     'certificate': 'G1234567M',
                     'password1': 'dsajkflsi&)(312',
                     'password2': 'dsajkflsi&)(3',
                     'group': self.group.pk}

        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        response = self.client.post(path=reverse('signup'), data=form_data, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_signup_get(self):
        response = self.client.get(path=reverse('signup'))
        self.assertEqual(response.status_code, 200)

    def test_password_change(self):
        old_pwd = 'dsajkflsi&)(3'
        new_pwd = 'jiiefa9790213*^&('
        user = CustomUser.objects.create_user(
            username='User', email='User@gmail.com',
            certificate="G123456M", group=self.group, password=old_pwd
        )
        self.client.login(username='User@gmail.com', password=old_pwd)
        form_data = {'old_password': old_pwd,
                     'new_password1': new_pwd,
                     'new_password2': new_pwd}

        form = CustomPasswordChangeForm(data=form_data, user=user)
        self.assertTrue(form.is_valid())

        response = self.client.post(path=reverse('password_change'), data=form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(CustomUser.objects.get(pk=user.pk).check_password(new_pwd))

    def test_password_change_invalid(self):
        old_pwd = 'dsajkflsi&)(3'
        new_pwd = 'jiiefa9790213*^&('
        user = CustomUser.objects.create_user(
            username='User', email='User@gmail.com',
            certificate="G123456M", group=self.group, password=old_pwd
        )
        self.client.login(username='User@gmail.com', password=old_pwd)
        form_data = {'old_password': old_pwd + "wrong",
                     'new_password1': new_pwd,
                     'new_password2': new_pwd}

        form = CustomPasswordChangeForm(data=form_data, user=user)
        self.assertFalse(form.is_valid())

        response = self.client.post(path=reverse('password_change'), data=form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CustomUser.objects.get(pk=user.pk).check_password(new_pwd))
        self.assertTrue(CustomUser.objects.get(pk=user.pk).check_password(old_pwd))

    def test_password_change_get(self):
        response = self.client.get(path=reverse('password_change'), follow=True)
        self.assertEqual(response.status_code, 200)


class UtilsTestCase(TestCase):
    def setUp(self) -> None:
        translation.activate('en')
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
        self.admin = CustomUser.objects.create_admin(
            username='Admin', email='admin@gmail.com',
            certificate="G00000M", group=self.groups[0], password='admin'
        )
        self.all_approved_user.append(self.admin)

    def test_get_group_report(self):
        report = get_group_report(self.groups[0])
        expected_report = {
            "num_ans": self.num_ans_0,
            "point": self.point_0,
            "accuracy": self.correct_num_ans_0 / self.num_ans_0
        }
        self.assertEqual(report, expected_report)

        group = CustomGroup.objects.create(name="Empty")
        report = get_group_report(group)
        expected_report = {
            "num_ans": 0,
            "point": 0,
            "accuracy": 1
        }
        self.assertEqual(report, expected_report)

    def test_get_pending_users(self):
        users = get_pending_users(group=self.groups[0])
        self.assertEqual(list(users), [u for u in self.all_pending_user if u.group == self.groups[0]])

        users = get_pending_users(group=None)
        self.assertEqual(list(users), self.all_pending_user)

    def test_get_approved_users(self):
        users = get_approved_users(group=self.groups[0])
        self.assertEqual(list(users), [u for u in self.all_approved_user if u.group == self.groups[0] and not u.is_superuser and not u.is_admin])

        users = get_approved_users(group=None)
        self.assertEqual(len(users), len(self.all_approved_user))
        self.assertEqual(set(users), set(self.all_approved_user))

    def test_get_log_msg(self):
        timestamp = "2000-01-01 23:59"
        log = Log.objects.create(admin=self.admin, action=Log.AccountAction.ACTIVATE, account=self.all_approved_user[0], timestamp=timestamp)
        expected = {
            "logger": "{}({})".format(self.admin.username, self.admin.certificate),
            "timestamp": timestamp,
            "msg": "{} {}({})".format("activate", self.all_approved_user[0].username, self.all_approved_user[0].certificate),
            "extra": log.extra_msg,
        }
        self.assertEqual(get_log_msg(log), expected)

    def test_log(self):
        log(self.admin, Log.AccountAction.REJECT, self.all_pending_user[0])
        self.assertIsNotNone(Log.objects.filter(admin=self.admin, action=Log.AccountAction.REJECT, account=self.all_pending_user[0]).first())

class FilterTestCase(TestCase):
    def test_get_item(self):
        self.assertEqual(filter.get_item("{'a': 1, 'b': 2}", 'a'), "")
        self.assertEqual(filter.get_item({'a': 1, 'b': 2}, 'a'), 1)
        self.assertEqual(filter.get_item({'a': 1, 'b': 2}, 'c'), "")