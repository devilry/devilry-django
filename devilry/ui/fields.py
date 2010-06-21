from django import forms
from django.contrib.auth.models import User

class MultiSelectCharField(forms.CharField):

    def to_python(self, value):
        userlist = value.split(", ")
        qry = User.objects.filter(username__in=userlist).all()
        id_list = [user.id for user in qry]
        return id_list
