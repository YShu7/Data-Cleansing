from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager, Group


class Specialization(models.Model):
    name = models.CharField(max_length=32)


class CustomGroup(models.Model):
    name = models.CharField(max_length=10)
    main_group = models.ForeignKey(to=Specialization, null=False, on_delete=models.CASCADE)


class CustomUserManager(UserManager):
    def create_user(self, email, name, certificate, group, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            certificate=certificate,
            group=group,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, certificate, password=None):
        user = self.create_user(
            email,
            name,
            certificate,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractUser):
    email = models.CharField(max_length=40, unique=True)
    certificate = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=20)
    group = models.ForeignKey(CustomGroup, on_delete=models.SET_NULL, null=True)
    point = models.IntegerField(default=0)
    accuracy = models.FloatField(default=100)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()
    #backend = CustomBackend()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'certificate', 'group']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, pages):
        "Does the user have permissions to view the app `pages`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
