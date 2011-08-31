from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from optparse import make_option

from devilry_usermod import UserModCommand
from devilry.apps.core.models import Subject, Period
import sys

from devilry_periodsetrelatedexaminers import BaseCommand

class Command(BaseCommand):
    help = 'Set related students on a period. Usernames are read from stdin, one username on each line.'
    user_type = "student"

    def handle(self, *args, **options):
        self.get_course_and_period(args)
        self.add_users(self.period.relatedstudents, args, options)
