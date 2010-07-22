import re

from django import forms
from django.contrib.auth.models import User


class MultiSelectCharField(forms.CharField):

    splitpatt = re.compile(r',\s*')

    @classmethod
    def from_string(cls, usernames):
        userlist = cls.splitpatt.split(usernames)
        qry = User.objects.filter(username__in=userlist).all()
        id_list = [user.id for user in qry]
        return id_list

    def to_python(self, value):
        return self.__class__.from_string(value)
