from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import ugettext_lazy as _


# Managers
class CustomUserManager(UserManager):
    def create_superuser(self, name, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)

        if name is None:
            raise ValueError('Superuser must have name')
        if email is None:
            raise ValueError('Superuser must have email')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(name=name, email=email, password=password, **extra_fields)

    def create_user(self, name, password=None, **extra_fields):
        if name is None:
            raise ValueError('users must have a name.')
        user = User(name=name, **extra_fields)
        user.set_password(password)
        user.save()
        return user


# Create your models here.
class User(AbstractUser):
    name = models.CharField(max_length=50)
    email = models.EmailField(_('email address'), unique=True)

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f'{self.id}: {self.email}'
