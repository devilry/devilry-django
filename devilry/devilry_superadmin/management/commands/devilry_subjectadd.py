from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError


class RecordSaveModCommand(BaseCommand):
    def save_record(self, record, verbosity):
        try:
            record.full_clean()
        except ValidationError, e:
            errmsg = []
            for key, messages in e.message_dict.iteritems():
                errmsg.append('{0}: {1}'.format(key, ' '.join(messages)))
            raise CommandError('\n'.join(errmsg))
        record.save()
        if verbosity > 0:
            print '{} "{}" saved successfully.'.format(
                record.__class__.__name__, str(record).encode('utf-8'))


class Command(RecordSaveModCommand):
    help = 'Create new subject.'

    def add_arguments(self, parser):
        parser.add_argument(
            'short_name',
            default='',
            help='Short name for the subject. (Required)'),
        parser.add_argument(
            '--long-name',
            dest='long_name',
            default=None,
            required=True,
            help='Long name (Required)')

    def handle(self, *args, **options):
        from devilry.apps.core.models import Subject
        verbosity = int(options.get('verbosity', '1'))
        short_name = options['short_name']
        long_name = options['long_name']
        if Subject.objects.filter(short_name=short_name).exists():
            raise CommandError('Subject "{0}" already exists.'.format(short_name))
        else:
            subject = Subject(short_name=short_name, long_name=long_name)
            self.save_record(subject, verbosity)
