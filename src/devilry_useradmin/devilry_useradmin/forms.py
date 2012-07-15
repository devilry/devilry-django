from django import forms
from django.contrib.auth.forms import UserChangeForm
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
        fields = ('username', 'email')

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



class CustomUserChangeForm(UserChangeForm):
    """ """
