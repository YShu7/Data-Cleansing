from django.test import TestCase, Client
from django.urls import reverse
from django.utils import translation

from .models import CustomUser, CustomGroup
from .utils import get_group_report, get_pending_users, get_approved_users
from .forms import CustomUserCreationForm, CustomPasswordChangeForm


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
        self.assertEqual(user.correct_num_ans / user.num_ans, 0.2)


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

    def test_password_change(self):
        old_pwd = 'dsajkflsi&)(3'
        new_pwd = 'jiiefa9790213*^&('
        user = CustomUser.objects.create_user(
            username='User', email='User@gmail.com',
            certificate="G123456M", group=self.group, password= old_pwd
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