# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import CharField
from django.db.models.functions import Concat

from devilry.devilry_account.models import UserEmail, UserName
from devilry.devilry_comment.models import Comment, CommentEditHistory, CommentFile

lorem_ipsum = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
Sed malesuada sagittis ipsum, quis malesuada sem placerat non. 
Donec metus urna, consectetur a laoreet vitae, dapibus sit amet odio. 
Morbi facilisis, nisl ut pellentesque consectetur, ipsum ante varius lectus, sed commodo felis metus 
sagittis neque. Donec vitae tortor magna. 
Nullam in massa quis sapien dignissim ullamcorper et quis urna. 
Aenean facilisis quis mauris a porttitor. 
Integer accumsan dolor sagittis sem sagittis sollicitudin quis bibendum diam. 
Suspendisse malesuada, neque quis condimentum elementum, odio arcu pulvinar erat, 
vitae imperdiet mauris turpis eu magna."""


class AnonymizeDatabaseException(Exception):
    def __init__(self, message, *args, **kwargs):
        self.message = message
        super(AnonymizeDatabaseException, self).__init__(*args, **kwargs)


class AnonymizeDatabase(object):
    """
    Anonymizes:
        - User
        - UserEmail
        - UserNames
        - Comments (comment text)
        - CommentFiles (filename)


    Generate a anonymized name based on the unanonymized name
    and keeps the same length.

    Replaces:
        - Digits
        - lower- and uppercase letters.

    Does not replace:
        - spaces
        - hyphens and underscores
        - special characters

    Args:
        unanonymized_string: The string to anonymize.
    """
    FALLBACK = 'empty'
    LETTERS = 'abcdefghijklmnopqrstuvwxyz'
    DIGITS = '0123456789'
    NOOP_CHARACTERS = [' ', '_', '@', '-', '"']

    def __init__(self, fast=True):
        self.fast = fast

    def is_uppercase(self, character):
        """
        Check if character is uppercase.
        """
        return character.isupper()

    def get_random_character(self, exclude_character):
        """
        Randomize the character.
        """
        if exclude_character.isdigit():
            character_list = list(self.DIGITS)
        else:
            character_list = list(self.LETTERS)
        character_list.remove(exclude_character.lower())
        random_choice = random.choice(character_list)
        if exclude_character.isupper():
            return random_choice.upper()
        return random_choice.lower()

    def randomize_string(self, unanonymized_string):
        """
        Start randomizing the string.

        Returns:
            str: Randomized string.
        """
        if len(unanonymized_string) == 0 or unanonymized_string is None:
            return self.FALLBACK
        anonymized_string = ''
        for character in list(unanonymized_string):
            if character in self.NOOP_CHARACTERS:
                anonymized_string += character
            else:
                anonymized_string += self.get_random_character(
                    exclude_character=character)
        return anonymized_string

    def __anonymize_user_data_fast(self):
        """
        Simply sets usernames to the ID of the user.
        """
        if settings.DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND:
            get_user_model().objects.update(
                fullname='Full Name',
                lastname='Lastname',
                shortname=Concat(models.F('id'), models.Value('@example.com'), output_field=CharField()))
        else:
            get_user_model().objects.update(
                fullname='Full Name',
                lastname='Lastname',
                shortname=Concat(models.F('id'), models.Value(''), output_field=CharField()))
        UserEmail.objects.update(
            email=Concat(models.F('user_id'), models.Value('_'), models.F('id'),
                         models.Value('@example.com'), output_field=CharField()))
        UserName.objects.update(
            username=Concat(models.F('user_id'), models.Value('_'),
                            models.F('id'), output_field=CharField()))

    def __anonymize_user_emails(self, user):
        for user_email in UserEmail.objects.filter(user_id=user.id):
            email_prefix = user_email.email.split('@')[0]
            anonymized_email_prefix = self.randomize_string(unanonymized_string=email_prefix)
            user_email.email = '{}@example.com'.format(anonymized_email_prefix)
            user_email.save()

    def __anonymize_user_names(self, user):
        for user_name in UserName.objects.filter(user_id=user.id):
            anonymized_user_name = self.randomize_string(unanonymized_string=user_name.username)
            user_name.username = anonymized_user_name
            user_name.save()

    def __anonymize_user_data(self):
        for user in get_user_model().objects.all():
            shortname = user.shortname
            if '@' in shortname:
                shortname = shortname.split('@')[0]
            anonymized_shortname = self.randomize_string(unanonymized_string=shortname)
            if settings.DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND:
                anonymized_shortname += '@example.com'
            user.shortname = anonymized_shortname
            user.fullname = self.randomize_string(unanonymized_string=user.fullname)
            user.lastname = self.randomize_string(unanonymized_string=user.lastname)
            user.save()

            self.__anonymize_user_emails(user=user)
            self.__anonymize_user_names(user=user)

    def anonymize_user(self):
        if self.fast:
            self.__anonymize_user_data_fast()
        else:
            self.__anonymize_user_data()

    def __anonymize_comments_fast(self):
        """
        Anonymize Comment text and CommentFile filenames.
        """
        Comment.objects.update(text=lorem_ipsum)
        CommentEditHistory.objects.update(post_edit_text=lorem_ipsum, pre_edit_text=lorem_ipsum)
        CommentFile.objects.update(filename=Concat(models.F('id'), models.Value(''), output_field=CharField()))

    def anonymize_comments(self):
        self.__anonymize_comments_fast()
