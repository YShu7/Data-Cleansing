from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from datacleansing.settings import CORRECT_POINT, INCORRECT_POINT


class CustomGroup(models.Model):
    name = models.CharField(max_length=32, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} created at {}, updated at {}".format(self.name, self.created_at, self.updated_at)

    def updated(self):
        self.updated_at = datetime.now()
        self.save()


class CustomUserManager(UserManager):
    def create_user(self, email, username, certificate, password, group):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            certificate=certificate,
            group=group,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, certificate, password):
        user = self.create_user(
            email=email,
            username=username,
            certificate=certificate,
            password=password,
            group=None,
        )
        user.is_superuser = True
        user.is_approved = True
        user.save(using=self._db)
        return user

    def create_admin(self, email, username, certificate, password, group):
        user = self.create_user(
            email=email,
            username=username,
            certificate=certificate,
            password=password,
            group=group,
        )
        user.is_admin = True
        user.is_approved = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractUser):
    email = models.CharField(max_length=40, unique=True)
    certificate = models.CharField(max_length=20, unique=True)
    username = models.CharField(max_length=20)
    group = models.ForeignKey(CustomGroup, on_delete=models.CASCADE, null=True)
    point = models.IntegerField(default=0)
    correct_num_ans = models.IntegerField(default=0)
    num_ans = models.IntegerField(default=0)

    is_approved = models.BooleanField(default=None, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'certificate', 'group', 'password']

    def __str__(self):
        return "{}<{}>".format(self.username, self.email)

    def accuracy(self):
        if not self.num_ans:
            return 1
        return self.correct_num_ans / self.num_ans

    def ans_is(self, correct: bool):
        self.num_ans += 1
        if correct:
            self.point += CORRECT_POINT
            self.correct_num_ans += 1
        else:
            self.point += INCORRECT_POINT
        self.save()

    def approve(self, approved):
        self.is_approved = approved
        self.group.updated()
        self.save()

    def activate(self, active):
        self.is_active = active
        self.group.updated()
        self.save()

    def assign_admin(self, is_admin):
        self.is_admin = is_admin
        self.group.updated()
        self.save()


class Log(models.Model):
    class AccountAction:
        ACTIVATE = 'ACTIVATE'
        DEACTIVATE = 'DEACTIVATE'
        APPROVE = 'APPROVE'
        REJECT = 'REJECT'
        choices = [
            (ACTIVATE, _('activate')),
            (DEACTIVATE, _('deactivate')),
            (APPROVE, _('approve')),
            (REJECT, _('reject')),
        ]

    admin = models.ForeignKey(get_user_model(), models.CASCADE, related_name="account_log")
    action = models.CharField(max_length=32, choices=AccountAction.choices)
    account = models.ForeignKey(get_user_model(), models.CASCADE, related_name="account_history", null=True)
    extra_msg = models.TextField(max_length=200, blank=True, null=True)
    timestamp = models.DateTimeField()