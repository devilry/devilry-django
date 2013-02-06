from pprint import pprint
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from devilry.utils.passed_in_previous_period import MarkAsPassedInPreviousPeriod



class Command(BaseCommand):
    args = '<subject_short_name> <period_short_name> <assignment_short_name>'
    help = 'Mark any matching assignment in a previous period in the same subject as approved. Students must already be in a group ALONE on the target assignment, and the previous assignment must have the same short name as the target assignment.'

    option_list = BaseCommand.option_list + (
        make_option('--apply',
                    dest='pretend', action='store_false',
                    default=True,
                    help='Apply the changes. The default is just to print them out without making any changes.'),
    )

    def handle(self, *args, **kwargs):
        from devilry.apps.core.models import Subject, Period, Assignment

        if len(args) != 3:
            raise CommandError('Subject, period and assignment short_name is required. See --help.')
        subject_short_name = args[0]
        period_short_name = args[1]
        assignment_short_name = args[2]

        subject = self._get_or_error(Subject, short_name=subject_short_name)
        period = self._get_or_error(Period, short_name=period_short_name,
                                    parentnode=subject)
        assignment = self._get_or_error(Assignment, short_name=assignment_short_name,
                                        parentnode=period)

        marker = MarkAsPassedInPreviousPeriod(assignment)
        result = marker.mark_all(pretend=kwargs['pretend'])
        print
        print '#' * 70
        print '# Ignored groups, ordered by reason for ignoring'
        print '#' * 70
        for reason, groups in result['ignored'].iteritems():
            print
            print reason
            print '-' * 70
            pprint(groups)

        print
        print '#' * 70
        print '# Groups marked as passed in previous period'
        print '#' * 70
        marked = result['marked']
        if marked:
            for group, oldgroup in result['marked']:
                feedback = oldgroup.feedback
                if feedback.is_passing_grade:
                    status = 'Passed'
                else:
                    status = 'Failed'
                print '- {0}'.format(group)
                print '     copied from: {0}'.format(oldgroup)
                print '     feedback: {0} ({1}) (points:{2})'.format(status,
                                                                     feedback.grade,
                                                                     feedback.points)
        else:
            print 'No groups with passing grade in previous periods found'

    def _get_or_error(self, cls, **qry):
        try:
            return cls.objects.get(**qry)
        except cls.DoesNotExist:
            raise CommandError('{0} matching {1!r} does not exist.'.format(cls.__name__, qry))
