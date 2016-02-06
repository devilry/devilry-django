import re

from crispy_forms import layout
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy
from django_cradmin.crispylayouts import PrimarySubmit
from django_cradmin.viewhelpers import formbase


class AbstractTypeInUsersView(formbase.FormView):
    users_blob_split_pattern = re.compile(r'[,;\s]+')
    create_button_label = ugettext_lazy('Save')
    template_name = 'devilry_admin/common/abstract-type-in-users.django.html'

    def get_backlink_url(self):
        raise NotImplementedError()

    def get_backlink_label(self):
        raise NotImplementedError()

    @classmethod
    def split_users_blob(cls, users_blob):
        """
        Split the given string of users by ``,`` and whitespace.

        Returns a set.
        """
        users_blob_split = cls.users_blob_split_pattern.split(users_blob)
        if len(users_blob_split) == 0:
            return []
        if users_blob_split[0] == '':
            del users_blob_split[0]
        if len(users_blob_split) > 0 and users_blob_split[-1] == '':
            del users_blob_split[-1]
        return set(users_blob_split)

    def __get_users_blob_help_text(self):
        if settings.DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND:
            return ugettext_lazy('Type or paste in email addresses separated '
                     'by comma (","), space or one user on each line.')
        else:
            return ugettext_lazy('Type or paste in usernames separated '
                     'by comma (","), space or one user on each line.')

    def __get_users_blob_placeholder(self):
        if settings.DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND:
            return ugettext_lazy('jane@example.com\njohn@example.com')
        else:
            return ugettext_lazy('jane\njohn')

    def get_form_class(self):
        users_blob_help_text = self.__get_users_blob_help_text()

        class UserImportForm(forms.Form):
            users_blob = forms.CharField(
                widget=forms.Textarea,
                required=True,
                help_text=users_blob_help_text
            )

            def __validate_users_blob_emails(self, emails):
                invalid_emails = []
                for email in emails:
                    try:
                        validate_email(email)
                    except ValidationError:
                        invalid_emails.append(email)
                if invalid_emails:
                    self.add_error(
                        'users_blob',
                        ugettext_lazy('Invalid email addresses: %(emails)s') % {
                            'emails': ', '.join(sorted(invalid_emails))
                        }
                    )

            def __validate_users_blob_usernames(self, usernames):
                valid_username_pattern = re.compile(
                    getattr(settings, 'DEVILRY_VALID_USERNAME_PATTERN', r'^[a-z0-9]+$'))
                invalid_usernames = []
                for username in usernames:
                    if not valid_username_pattern.match(username):
                        invalid_usernames.append(username)
                if invalid_usernames:
                    self.add_error(
                        'users_blob',
                        ugettext_lazy('Invalid usernames: %(usernames)s') % {
                            'usernames': ', '.join(sorted(invalid_usernames))
                        }
                    )

            def clean(self):
                cleaned_data = super(UserImportForm, self).clean()
                users_blob = cleaned_data.get('users_blob', None)
                if users_blob:
                    users = AbstractTypeInUsersView.split_users_blob(users_blob)
                    if settings.DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND:
                        self.__validate_users_blob_emails(emails=users)
                    else:
                        self.__validate_users_blob_usernames(usernames=users)
                    self.cleaned_users_set = users

        return UserImportForm

    def get_field_layout(self):
        return [
            layout.Div(
                layout.Field('users_blob', placeholder=self.__get_users_blob_placeholder()),
                css_class='cradmin-globalfields django-cradmin-formfield-label-sr-only')
        ]

    def get_buttons(self):
        return [
            PrimarySubmit('save', self.create_button_label),
        ]

    def get_success_url(self):
        return self.request.cradmin_app.reverse_appindexurl()

    def import_users_from_emails(self, emails):
        raise NotImplementedError()

    def import_users_from_usernames(self, usernames):
        raise NotImplementedError()

    def form_valid(self, form):
        if settings.DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND:
            self.import_users_from_emails(emails=form.cleaned_users_set)
        else:
            self.import_users_from_usernames(usernames=form.cleaned_users_set)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(AbstractTypeInUsersView, self).get_context_data(**kwargs)
        context['backlink_url'] = self.get_backlink_url()
        context['backlink_label'] = self.get_backlink_label()
        return context
