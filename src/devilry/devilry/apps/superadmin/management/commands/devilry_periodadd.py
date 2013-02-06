from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from optparse import make_option

from datetime import datetime


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
    args = '<course short name> <period short_name>'
    date_and_time_format = "%Y-%m-%dT%H:%M"
    help = 'Create a new period.'
    option_list = BaseCommand.option_list + (
        make_option('--admins',
            dest='admins',
            default=None,
            help='Administrator usernames separated by comma (,).'),
        make_option('--long-name',
            dest='long_name',
            default=None,
            help='Long name of period (Required)'),
        make_option('--start-time',
            dest='start_time',
            default=None,
            help='The start time of the period on the ISO format %s (Required)' % date_and_time_format),
        make_option('--end-time',
            dest='end_time',
            default=None,
            help='The end time of the period on the ISO format %s (Required)' % date_and_time_format),
        make_option('--date-format',
            dest='date_format',
            default=None,
            help='The date format expressed in a format according to strftime http://docs.python.org/library/datetime.html#strftime-strptime-behavior')
    )

    def handle(self, *args, **options):
        from devilry.apps.core.models import Subject, Period

        if len(args) != 2:
            raise CommandError('Course short name and period short name is required. See --help.')
        if options['long_name'] == None:
            raise CommandError('Long name is required. See --help.')
        if options['start_time'] == None:
            raise CommandError('Start time name is required. See --help.')
        if options['end_time'] == None:
            raise CommandError('End time is required. See --help.')
        course_short_name = args[0]
        period_short_name = args[1]
        # Get the course
        try:
            self.subject = Subject.objects.get(short_name=course_short_name)
        except Subject.DoesNotExist, e:
            raise CommandError('Subject with short name %s does not exist.' % course_short_name)
        
        verbosity = int(options.get('verbosity', '1'))
                
        if options['date_format'] != None:
            self.date_and_time_format = options['date_format']

        start_time = datetime.strptime(options['start_time'], self.date_and_time_format)
        end_time = datetime.strptime(options['end_time'], self.date_and_time_format)

        if Period.objects.filter(parentnode=self.subject, short_name=period_short_name).count() == 0:
            period_long_name = options['long_name']
            record = Period(short_name=period_short_name, long_name=period_long_name, parentnode=self.subject, start_time=start_time, end_time=end_time)
            self.save_record(record, verbosity)
        else:
            raise CommandError('Period "{0}" already exists.'.format(period_short_name))
