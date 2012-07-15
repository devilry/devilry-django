from django import forms
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User


class UsernameField(forms.RegexField):
    def __init__(self):
        kwargs = dict(label=_("Username"), max_length=30,
                      regex=r'^[\w.@+-]+$',
                      help_text = _("Required. 30 characters or fewer. Letters, digits and "
                                    "@/./+/-/_ only."),
                      error_messages = {'invalid': _("This value may contain only letters, numbers and "
                                                     "@/./+/-/_ characters.")})
        super(UsernameField, self).__init__(**kwargs)


class UserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username.
    """
    username = UsernameField()

    class Meta:
        model = User
        fields = ("username",)

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_unusable_password()
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    username = UsernameField()

    class Meta:
        model = User

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
