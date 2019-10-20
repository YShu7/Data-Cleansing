from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import UserManager

class CustomUserManager(UserManager):
    def create_user(self, email, name, certificate, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            certificate=certificate,
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

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()
    #backend = CustomBackend()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'certificate']

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
