from django.conf import settings
from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User



class CustomUserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username.
    """
    username = forms.RegexField(label=_("Username"), max_length=30,
        regex=r'^[\w.@+-]+$',
        help_text = _("Required. 30 characters or fewer. Letters, digits and "
                      "@/./+/-/_ only."),
        error_messages = {
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})

    class Meta:
        model = User
        fields = ('username',)

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM.
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(_("A user with that username already exists."))

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.set_unusable_password()
        if commit:
            user.save()
        return user



default_password_helptext = _("Raw passwords are not stored, so there is no way to see "
                              "this user's password, but you can change the password "
                              "using <a href=\"password/\">this form</a>.")
password_helptext = getattr(settings, 'DEVILRY_USERADMIN_PASSWORD_HELPMESSAGE', default_password_helptext)

class CustomUserChangeForm(UserChangeForm):
    """
    Adds the ability to customize the password help message in setting.py, and
    the ability to disable username editing.
    """
    password = ReadOnlyPasswordHashField(label=_("Password"),
                                         help_text=password_helptext)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if not getattr(settings, 'DEVILRY_USERADMIN_USERNAME_EDITABLE', False):
            saved_user = User.objects.get(id=self.instance.id)
            if saved_user.username != username:
                error = getattr(settings, 'DEVILRY_USERADMIN_USERNAME_NOT_EDITABLE_MESSAGE',
                                _('The system administrator has configured Devilry to not allow changing usernames. If this is wrong, you can ask them to set DEVILRY_USERADMIN_USERNAME_EDITABLE=True in settings.py.'))
                raise forms.ValidationError(_(error))
        return username
