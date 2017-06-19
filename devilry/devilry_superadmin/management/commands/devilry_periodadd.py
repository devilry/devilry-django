from datetime import datetime

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
            print '"{0}" saved successfully.'.format(record.__class__.__name__, record)


class Command(RecordSaveModCommand):
    # args = '<course short name> <period short_name>'
    date_and_time_format = "%Y-%m-%dT%H:%M"
    help = 'Create a new period.'

    def add_arguments(self, parser):
        parser.add_argument(
            'subject_short_name',
            help='Short name of the subject to add the period within.'
        )
        parser.add_argument(
            'period_short_name',
            help='Short name of the period you want to create.'
        )
        parser.add_argument(
            '--long-name',
            dest='long_name',
            default=None,
            required=True,
            help='Long name of period (Required)'),
        parser.add_argument(
            '--start-time',
            dest='start_time',
            default=None,
            required=True,
            help='The start time of the period on the format specified in --datetime-format (Required)'),
        parser.add_argument(
            '--end-time',
            dest='end_time',
            default=None,
            required=True,
            help='The end time of the period on the format specified in --datetime-format (Required)'),
        parser.add_argument(
            '--datetime-format',
            dest='datetime_format',
            default=self.date_and_time_format,
            help='The date format expressed in a format according to '
                 'strftime http://docs.python.org/library/datetime.html#strftime-strptime-behavior. '
                 'Defaults to YYYY-MM-DDThh:mm')

    def handle(self, *args, **options):
        from devilry.apps.core.models import Subject, Period
        subject_short_name = options['subject_short_name']
        period_short_name = options['period_short_name']
        # Get the subject
        try:
            self.subject = Subject.objects.get(short_name=subject_short_name)
        except Subject.DoesNotExist, e:
            raise CommandError('Subject with short name %s does not exist.' % subject_short_name)
        
        verbosity = int(options.get('verbosity', '1'))
        date_and_time_format = options['datetime_format']
        start_time = datetime.strptime(options['start_time'], date_and_time_format)
        end_time = datetime.strptime(options['end_time'], date_and_time_format)

        if Period.objects.filter(parentnode=self.subject, short_name=period_short_name).count() == 0:
            period_long_name = options['long_name']
            record = Period(short_name=period_short_name, long_name=period_long_name, parentnode=self.subject, start_time=start_time, end_time=end_time)
            self.save_record(record, verbosity)
        else:
            raise CommandError('Period "{0}" already exists.'.format(period_short_name))
