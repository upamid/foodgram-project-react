from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .managers import CustomUserManager
from .utils import generate_confirmation_code


class ConstUserRoles(models.TextChoices):
    USER = 'user', _('user')
    ADMIN = 'admin', _('admin')


class CustomUser(AbstractUser):
    email = models.EmailField(
        unique=True,
        verbose_name=_('email address'))
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name=_('user name'))
    first_name = models.CharField(
        max_length=150,
        verbose_name=_('first name'))
    last_name = models.CharField(
        max_length=150,
        verbose_name=_('last name'))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username','first_name','last_name')

    objects = CustomUserManager()

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.username

