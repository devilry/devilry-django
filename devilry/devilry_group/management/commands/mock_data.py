import sys, random, string

from django.core.management.base import BaseCommand, CommandParser
from model_bakery import baker
from django.utils import timezone
from django.core.files.base import ContentFile
from itertools import cycle

from devilry.devilry_group import models as groupmodels
from devilry.devilry_comment.models import Comment, CommentFile
from devilry.apps.core.models import Subject, Period, Assignment, RelatedStudent, AssignmentGroup
from devilry.devilry_account.models import User
TEST_DATA_NAME = 't_d__'


def progressBar(count_value, total, suffix=''):
    bar_length = 100
    filled_up_Length = int(round(bar_length * count_value / float(total)))
    percentage = round(100.0 * count_value / float(total), 1)
    bar = '=' * filled_up_Length + '-' * (bar_length - filled_up_Length)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percentage, '%', suffix))
    sys.stdout.flush()


def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


class Command(BaseCommand):
    help = "Generate data for bulk file download testing"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("-s", type=int, default=10, help='Number of students to generate')
        parser.add_argument("-a", type=int, default=1, help='Number of assignments to generate')
        parser.add_argument("-f", type=int, default=1, help='Number of files per student to generate')
        parser.add_argument("-fs", type=int, default=50, help='size of file in bytes to generate')
        parser.add_argument("--clean", action="store_true", default=False)

    def handle(self, *args, **options):
        if options["clean"]:
            AssignmentGroup.objects.filter(parentnode__short_name__startswith=TEST_DATA_NAME).delete()
            aq = Assignment.objects.filter(short_name__startswith=TEST_DATA_NAME)
            if aq.exists():
                aq.delete()
            sq = Subject.objects.filter(short_name__startswith=TEST_DATA_NAME)
            if sq.exists():
                sq.delete()
            pq = Period.objects.filter(short_name__startswith=TEST_DATA_NAME)
            if pq.exists():
                pq.delete()
            rsq = RelatedStudent.objects.filter(user__shortname__startswith=TEST_DATA_NAME)
            if rsq.exists():
                rsq.delete()
            cfq = CommentFile.objects.filter(filename__startswith=TEST_DATA_NAME)
            if cfq.exists():
                cfq.delete()
            uq = User.objects.filter(shortname__startswith=TEST_DATA_NAME)
            if uq.exists():
                uq.delete()

        else:
            today = timezone.now()
            tomorrow = today + timezone.timedelta(days=1)
            tdn = f'{TEST_DATA_NAME}{today.strftime("%H%M%S")}__'
            n = 0
            n_files = options["f"]
            n_students = options["s"]
            n_file_size = options['fs']
            n_assignments = options["a"]
            n_comment_files = n_files * n_students
            file_content = randomword(n_file_size)

            bar_total = (((n_students * 4) + n_comment_files + n_comment_files) *
                         n_assignments) + 1 + 1 + n_assignments + n_students
            progressBar(n, bar_total)

            subject_name = tdn + "2100"
            subject = baker.make('core.Subject',
                                 short_name=subject_name)
            n += 1
            progressBar(n, bar_total)

            period_name = tdn + "20xx"
            period = baker.make('core.Period',
                                short_name=period_name,
                                parentnode=subject)
            n += 1
            progressBar(n, bar_total)

            assignment_prefix = tdn + "oblig_"
            assignments = baker.make(
                'core.Assignment',
                short_name=baker.seq(assignment_prefix),
                parentnode=period,
                _quantity=n_assignments,
                _bulk_create=True
            )
            n += n_assignments
            progressBar(n, bar_total)

            students = baker.make(
                'core.RelatedStudent',
                user__shortname=baker.seq(tdn + "user_"),
                period=period,
                _quantity=n_students,
                _bulk_create=True
            )
            n += n_students
            progressBar(n, bar_total)

            for ass in assignments:
                assignment_groups = baker.make(
                    'core.AssignmentGroup',
                    parentnode=ass,
                    _quantity=n_students,
                    _bulk_create=True
                )
                n += n_students
                progressBar(n, bar_total)

                baker.make(
                    'core.Candidate',
                    assignment_group=iter(assignment_groups),
                    relatedstudent=iter(students),
                    _quantity=n_students,
                    _bulk_create=True
                )
                n += n_students
                progressBar(n, bar_total)

                feedbacksets = baker.make(
                    'devilry_group.FeedbackSet',
                    group=iter(assignment_groups),
                    feedbackset_type=groupmodels.FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT,
                    deadline_datetime=tomorrow,
                    _quantity=n_students,
                    _bulk_create=True
                )
                n += n_students
                progressBar(n, bar_total)

                comments = baker.make(
                    'devilry_group.GroupComment',
                    feedback_set=iter(feedbacksets),
                    user_role=Comment.USER_ROLE_STUDENT,
                    _quantity=n_students
                )
                n += n_students
                progressBar(n, bar_total)

                comment_files = baker.make(
                    'devilry_comment.CommentFile',
                    comment=cycle(comments),
                    filename=baker.seq(TEST_DATA_NAME + 'testfile'),
                    _quantity=n_comment_files,
                    _create_files=True,
                    _bulk_create=True
                )
                n += n_comment_files
                progressBar(n, bar_total)

                for cf in comment_files:
                    cf.file.save(cf.filename, ContentFile(file_content))
                    n += 1
                    progressBar(n, bar_total)
