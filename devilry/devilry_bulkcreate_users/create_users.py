import re
from django.contrib import auth
from django.db import transaction
from django.conf import settings
from django.core import exceptions

class BulkCreateUsers(object):
    """
    Allow bulk-creation of :class:`User`\s from a list of usernames or emails.
    """
    def __init__(self):
        self.__parsed_userdata = {}
        self.__conflicting_users = {}
        self.__created_users = []

    def __add_raw_data(self, raw_data, regexp_for_split=r'[\s;:,]+'):
        """
        Add raw, unparsed data to be created in bulk.
        This data can be a combination of usernames and emails.

        If a username is provided, it is assumed that <username>@<DEVILRY_DEFAULT_EMAIL_SUFFIX> is a valid email.
        If an email is provided the username will be extracted based on the same logic.

        In order to split the raw data into usernames/emails, you may provide a regex for splitting.
        The default regex will split on `whitespaces`, `;`, `:` or `,`.

        result will be stored as a `dict` in `self.__parsed_userdata` for validation and creation of users.
        This data can optionally be retrieved using :func:`self.get_userdata`

        :param raw_data: the raw text to be split into usernames and/or emails
        :param regexp_for_split: valid regex to split usernames/emails.
        """
        reg = re.compile(regexp_for_split)
        values = reg.split(raw_data)
        email_domain = settings.DEVILRY_DEFAULT_EMAIL_SUFFIX
        if not email_domain:
            raise exceptions.ImproperlyConfigured("Missing setting: DEVILRY_DEFAULT_EMAIL_SUFFIX")

        for value in values:
            value = value.strip()
            if value == '':
                continue
            split_email = value.split('@')

            if len(split_email) == 2:
                username = split_email[0]
                email = value
            else:
                username = value
                email = '{}{}'.format(value, email_domain)

            self.__parsed_userdata[username] = email

    def __validate_userdata(self):
        """
        Ensure that no users already exist with given usernames/emails, and remove those that conflict from
        `self.__parsed_userdata`

        Any/all conflicting users are added to `self.__conflicting_users`, which can be retrieved using
        :func:`self.get_conflicting_users`
        """
        print(self.__parsed_userdata)
        emails = [email for username, email in self.__parsed_userdata.items()]
        usernames = [username for username, email in self.__parsed_userdata.items()]
        user_model = auth.get_user_model()
        conflicting_users = user_model.objects.filter(email__in=emails, username__in=usernames).distinct()

        for user in conflicting_users:
            self.__conflicting_users[user.username] = user.email
            del(self.__parsed_userdata[user.username])

    def add_userdata(self, userdata, parse_data=True):
        """
        Add and validate userdata. This data can be supplied either as a separated list of userdata
        (see :func:`__add_raw_data` for details), or as an already parsed dict of users if `parse_data`
        is set to `False`.

        validation is performed either way, by :func:`self.__validate_userdata`

        :param userdata: the needed info for creating users.
        :param parse_data: if `True`(default) data will be sent to :func:`self.__add_raw_data`. If `False` the data will be stored in `self.__parsed_userdata`
        """
        if parse_data:
            self.__add_raw_data(raw_data=userdata)
        else:
            self.__parsed_userdata = userdata
        self.__validate_userdata()

    def create_users(self):
        """
        Create :class:`User`-objects for all users in `self.__parsed_userdata` in a single transaction.
        Users are created with unusable passwords.

        All created users are stored in `self.__created_users`, which can be accessed via :func:`self.get_userdata`.
        """
        user_model = auth.get_user_model()
        with transaction.atomic():
            for username, email in self.__parsed_userdata.items():
                user = user_model(username=username, email=email)
                user.set_unusable_password()
                user.full_clean()
                user.save()

                self.__created_users.append(user)

    def get_created_users(self):
        return self.__created_users

    def get_conflicting_users(self):
        return self.__conflicting_users

    def get_userdata(self):
        return self.__parsed_userdata