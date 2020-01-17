from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class CustomGroup(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name


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
            email=self.normalize_email(email),
            username=username,
            certificate=certificate,
            group=None,
        )
        user.is_superuser = True
        user.is_approved = True

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_admin(self, email, username, certificate, password, group):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            certificate=certificate,
            group=group,
        )
        user.is_admin = True

        user.set_password(password)
        user.save(using=self._db)
        return user


class CustomUser(AbstractUser):
    email = models.CharField(max_length=40, unique=True)
    certificate = models.CharField(max_length=20, unique=True)
    username = models.CharField(max_length=20)
    group = models.ForeignKey(CustomGroup, on_delete=models.SET_NULL, null=True)
    point = models.IntegerField(default=0)
    correct_num_ans = models.IntegerField(default=0)
    num_ans = models.IntegerField(default=0)
    is_approved = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'certificate', 'group']

    def __str__(self):
        return self.email

    def accuracy(self):
        if not self.num_ans:
            return 1
        return self.correct_num_ans / self.num_ans

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, pages):
        "Does the user have permissions to view the app `pages`?"
        # Simplest possible answer: Yes, always
        return True

    def ans_is(self, correct: bool):
        CORRECT_POINT = 3
        INCORRECT_POINT = 1
        self.num_ans += 1
        if correct:
            self.point += CORRECT_POINT
            self.correct_num_ans += 1
        else:
            self.point += INCORRECT_POINT
        self.save()

    def approve(self, approved):
        self.is_approved = approved
        self.save()

    def activate(self, active):
        self.is_active = active
        self.save()
