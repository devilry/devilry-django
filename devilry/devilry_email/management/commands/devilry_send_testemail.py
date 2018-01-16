from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Send email.'

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            default='',
            help='Short name for the subject. (Required)'),

    def handle(self, *args, **options):
        send_mail(subject='Devilry test', message='Test email',
                  recipient_list=[options['email']], from_email=settings.DEFAULT_FROM_EMAIL)
