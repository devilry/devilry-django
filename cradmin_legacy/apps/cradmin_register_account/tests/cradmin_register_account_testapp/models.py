from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class EmailUser(AbstractBaseUser):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = BaseUserManager()

    email = models.EmailField(max_length=250, blank=False, unique=True)

    def get_short_name(self):
        return self.email

    def get_full_name(self):
        return self.email
