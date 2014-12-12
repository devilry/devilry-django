from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count
from django.contrib.auth.models import User
from optparse import make_option

from devilry.apps.core.models import Delivery
from devilry.utils.management import make_output_encoding_option



class Command(BaseCommand):
    args = '[delivery_id1] [delivery_id2] ...'
    help = 'List deliveries and edit the successful flag.'

    option_list = BaseCommand.option_list + (
        make_option('--list',
                    dest='list', action='store_true',
                    default=False,
                    help='List deliveries.'),
        make_option('--unsuccessful-with-feedback',
                    dest='unsuccessful_with_feedback', action='store_true',
                    default=False,
                    help='Show unsuccessful deliveries with feedback.'),
        make_option('--mark-all-unsuccessful-with-feedback-as-successful',
                    dest='mark_all_unsuccessful_with_feedback_as_successful', action='store_true',
                    default=False,
                    help='Mark all deliveries listed when you use "--list --unsuccessful-with-feedback" as successful. This option is probably only useful to fix groups affected by issue #362.'),
        make_option('--mark-successful',
                    dest='marksuccessful', action='store_true',
                    default=False,
                    help='Mark the listed deliveries as successful.'),
        make_option('--mark-unsuccessful',
                    dest='markunsuccessful', action='store_true',
                    default=False,
                    help='Mark the listed deliveries as unsuccessful.'),
        make_option('--user',
                    dest='username', default=None,
                    help='Show all deliveries made by this user (username).'),
        make_output_encoding_option()
    )

    def handle(self, *args, **kwargs):
        self.outputencoding = kwargs['outputencoding']
        if kwargs['list']:
            if not (kwargs['unsuccessful_with_feedback'] or kwargs['username']):
                raise CommandError('--unsuccessful-with-feedback or --user is required when using --list.')
            self.printall(unsuccessful_with_feedback=kwargs['unsuccessful_with_feedback'],
                          username=kwargs['username'])
        elif kwargs['marksuccessful']:
            self.set_successful(args, successful=True)
        elif kwargs['markunsuccessful']:
            self.set_successful(args, successful=False)
        elif kwargs['mark_all_unsuccessful_with_feedback_as_successful']:
            self.mark_all_unsuccessful_with_feedback_as_successful()
        else:
            raise CommandError('--list, --mark-unsuccessful or --mark-successful --mark-all-unsuccessful-with-feedback-as-successful is required. See --help.')

    def set_successful(self, ids, successful):
        ids = map(int, ids)
        for delivery in Delivery.objects.filter(id__in=ids):
            delivery.successful = successful
            delivery.save()
            print 'Marked {0} with successful={1}'.format(delivery, successful)
        print 'Successfully marked {0} deliveries as successful={1}'.format(len(ids), successful)


    def _qry(self, unsuccessful_with_feedback, username=None):
        qry = Delivery.objects.filter()
        qry = qry.annotate(feedback_count=Count('feedbacks'))
        if unsuccessful_with_feedback:
            qry = qry.filter(feedback_count__gt=0,
                             successful=False)
        if username:
            user = self._get_or_error(User, username=username)
            qry = qry.filter(deadline__assignment_group__candidates__student=user)

        qry = qry.select_related('deadline', 'deadline__assignment_group', 'deadline__assignment_group__parentnode',
                                 'deadline__assignment_group__parentnode__parentnode',
                                 'deadline__assignment_group__parentnode__parentnode__parentnode')
        qry = qry.prefetch_related('deadline__assignment_group__candidates',
                                   'deadline__assignment_group__candidates__student',
                                   'deadline__assignment_group__candidates__student__devilryuserprofile')
        return qry

    def mark_all_unsuccessful_with_feedback_as_successful(self):
        matches = self._qry(unsuccessful_with_feedback=True).all()
        for delivery in matches:
            delivery.successful = True
            delivery.save()
            print 'Marked {0} with successful=True'.format(delivery)
        print 'Successfully marked {0} deliveries as successful=True'.format(len(matches))


    def printall(self, unsuccessful_with_feedback, username=None):
        matches = self._qry(unsuccessful_with_feedback, username).all()
        if len(matches) == 0:
            print 'No deliveries found. See --help for listing options.'
        else:
            print 'Found {0} deliveries:'.format(len(matches))
            for delivery in matches:
                group = delivery.deadline.assignment_group
                def strcandidate(candidate):
                    return u'{fullname}({username})'.format(username=candidate.student.username,
                                                            fullname=candidate.student.devilryuserprofile.full_name)
                candidates = map(strcandidate, group.candidates.all())
                msg = (u' - [{path} deliveryID={id}]: '
                       u'students=[{candidates}], deadline={deadline}, '
                       u'has-feedback={has_feedback}, '
                       u'successful={successful}').format(path=group.parentnode.get_path(),
                                                          id=delivery.id,
                                                          candidates=', '.join(candidates),
                                                          deadline=delivery.deadline.deadline,
                                                          has_feedback=delivery.feedback_count>0,
                                                          successful=delivery.successful)
                print msg.encode(self.outputencoding)


    def _get_or_error(self, cls, **qry):
        try:
            return cls.objects.get(**qry)
        except cls.DoesNotExist:
            raise CommandError('{0} matching {1!r} does not exist.'.format(cls.__name__, qry))
