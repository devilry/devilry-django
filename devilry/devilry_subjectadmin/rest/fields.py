from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

# Import these to avoid breaking existing code after they where moved
from devilry.devilry_rest.formfields import ListOfDictField
from devilry.devilry_rest.formfields import ListOfTypedField
from devilry.devilry_rest.formfields import DictField


class DevilryUserMultipleChoiceField(forms.ModelMultipleChoiceField):
    def _get_user_from_userdict(self, userdict):
        if 'id' in userdict:
            return userdict['id']
        elif 'username' in userdict:
            username = userdict['username']
            try:
                return User.objects.get(username=username).id
            except User.DoesNotExist, e:
                raise ValidationError('User does not exist: "{0}"'.format(username))
        else:
            raise ValidationError('If you use a map/dict to identify users, the dict must contain "id" or "username".')

    def _clean_single_user(self, user):
        if isinstance(user, dict):
            return self._get_user_from_userdict(user)
        else:
            return user

    def clean(self, users):
        users = [self._clean_single_user(user) for user in users]
        return super(DevilryUserMultipleChoiceField, self).clean(users)
