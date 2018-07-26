import sys

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.db import transaction
from django.utils import timezone
from django.core.management.base import BaseCommand
from model_mommy import mommy

from devilry.apps.core.models import Subject, Period, RelatedStudent, RelatedExaminer, AssignmentGroup, Candidate, \
    Examiner, Assignment
from devilry.devilry_comment.models import CommentFile
from devilry.devilry_group.models import FeedbackSet, GroupComment


class ProgressDots(object):
    def __init__(self, interval=100, messageformat='One dot per {interval}: '):
        self._count = 0
        self._interval = interval
        self._messageformat = messageformat
        self._enabled = True

    def reset(self):
        self._count = 0

    def increment_progress(self, increment=1):
        self._count += increment
        if self._enabled:
            if self._count % self._interval == 0:
                sys.stdout.write('.')
                sys.stdout.flush()

    def __enter__(self):
        self._count = 0
        if self._enabled:
            sys.stdout.write(self._messageformat.format(interval=self._interval))
            sys.stdout.flush()
        return self

    def __exit__(self, ttype, value, traceback):
        if self._enabled:
            sys.stdout.write('\n')


class DatabaseBuilder(object):
    def __init__(self, num_subjects, num_periods, num_assignments, num_students, num_comments, project_groups):
        self.num_subjects = num_subjects
        self.num_periods = num_periods
        self.num_assignments = num_assignments
        self.num_students = num_students
        self.num_comments = num_comments
        self.project_groups = project_groups
        self.progressdots = ProgressDots()

    def __create_student_users(self):
        """
        Generate users to be used as candidates.
        """
        sys.stdout.write('Creating student users:')
        for num in range(self.num_students):
            name = 'studentuser#{}'.format(num)
            user = get_user_model()(shortname=name)
            user.set_password("test")
            user.full_clean()
            user.save()
            user.username_set.create(username=name)
            user.useremail_set.create(email=name.strip() + '@example.com')
            self.progressdots.increment_progress()
        self.progressdots.reset()
        sys.stdout.write('\n')

    def __create_examiner_users(self):
        """
        Generate users to be used as examiners.
        """
        sys.stdout.write('Creating examiner users:')
        for num in range(self.num_students):
            name = 'examineruser#{}'.format(num)
            user = get_user_model()(shortname=name)
            user.set_password("test")
            user.full_clean()
            user.save()
            user.username_set.create(username=name)
            user.useremail_set.create(email=name.strip() + '@example.com')
            self.progressdots.increment_progress()
        self.progressdots.reset()
        sys.stdout.write('\n')

    def __create_commentfiles_for_groupcomment(self, groupcomment):
        """
        Generate CommentFiles for GroupComment.
        """
        commentfile = mommy.make('devilry_comment.CommentFile', comment=groupcomment)
        commentfile.file.save('testfile.txt', ContentFile('test'))

    def __create_groupcomments_for_feedbackset(self, feedbackset):
        """
        Generate GroupComments for each user in the FeedbackSet's AssignmentGroup.
        """
        publish_aggregate_minutes = 1
        for candidate in feedbackset.group.candidates.all():
            for num in range(self.num_comments):
                mommy.make(
                    'devilry_group.GroupComment',
                    user=candidate.relatedstudent.user,
                    user_role=GroupComment.USER_ROLE_STUDENT,
                    published_datetime=feedbackset.deadline_datetime + timezone.timedelta(
                        minutes=publish_aggregate_minutes),
                    feedback_set=feedbackset,
                    text='This is a comment')
                publish_aggregate_minutes += 1

        publish_aggregate_minutes = 2
        for examiner in feedbackset.group.examiners.all():
            for num in range(self.num_comments):
                mommy.make(
                    'devilry_group.GroupComment',
                    user=examiner.relatedexaminer.user,
                    user_role=GroupComment.USER_ROLE_EXAMINER,
                    published_datetime=feedbackset.deadline_datetime + timezone.timedelta(
                        minutes=publish_aggregate_minutes),
                    feedback_set=feedbackset,
                    text='This is a comment.')
                publish_aggregate_minutes += 2

    def __create_examiners_for_assignmentgroup(self, assignmentgroup):
        """
        Generate Examiners for each RelatedExaminer on the semester and
        add them to the AssignmentGroup.
        """
        sys.stdout.write('Creating examiners:')
        for relatedexaminer in RelatedExaminer.objects.filter(period_id=assignmentgroup.parentnode.parentnode.id):
            mommy.make('core.Examiner', relatedexaminer=relatedexaminer, assignmentgroup=assignmentgroup)
            self.progressdots.increment_progress()
        self.progressdots.reset()
        sys.stdout.write('\n')

    def __create_candidates_for_assignmentgroup(self, assignmentgroup):
        """
        Generate Candidates for each RelatedStudent on the semester and
        add them to the AssignmentGroup.
        """
        sys.stdout.write('Creating candidates:')
        for relatedstudent in RelatedStudent.objects.filter(period_id=assignmentgroup.parentnode.parentnode.id):
            mommy.make('core.Candidate', relatedstudent=relatedstudent, assignment_group=assignmentgroup)
            self.progressdots.increment_progress()
        self.progressdots.reset()
        sys.stdout.write('\n')

    def __create_assignmentgroups_for_assignment(self, assignment):
        """
        Generate AssignmentGroups for Assignment and
        GroupComments for FeedbackSet
        """
        groups = []
        for num in range(RelatedStudent.objects.filter(period=assignment.parentnode).count()):
            assignmentgroup = mommy.prepare('core.AssignmentGroup', parentnode=assignment)
            groups.append(assignmentgroup)
        AssignmentGroup.objects.bulk_create(groups)

        relatedstudents = [relatedstudent for relatedstudent
                           in RelatedStudent.objects.filter(period=assignment.parentnode)]
        relatedexaminers = [relatedexaminer for relatedexaminer
                           in RelatedExaminer.objects.filter(period=assignment.parentnode)]
        assignmentgroups = [assignmentgroup for assignmentgroup
                            in AssignmentGroup.objects.filter(parentnode=assignment)]

        candidates = []
        list_index = 0
        for relatedstudent in relatedstudents:
            candidate = mommy.prepare(
                'core.Candidate',
                relatedstudent=relatedstudent,
                assignment_group=assignmentgroups[list_index])
            candidates.append(candidate)
            list_index += 1
        Candidate.objects.bulk_create(candidates)

        examiners = []
        list_index = 0
        for relatedexaminer in relatedexaminers:
            examiner = mommy.prepare(
                'core.Examiner',
                relatedexaminer=relatedexaminer,
                assignmentgroup=assignmentgroups[list_index])
            examiners.append(examiner)
            list_index += 1
        Examiner.objects.bulk_create(examiners)

        sys.stdout.write('Creating comments:')
        for feedbackset in FeedbackSet.objects.filter(group__parentnode_id=assignment.id):
            self.__create_groupcomments_for_feedbackset(feedbackset=feedbackset)
            self.progressdots.increment_progress()
        self.progressdots.reset()
        sys.stdout.write('\n')

    def __create_assignments_for_period(self, period):
        """
        Generate Assignments for a Period.
        """
        publishing_time_from_period_start = 0
        first_deadline_from_period_start = 7
        created_assignments = []
        sys.stdout.write('Creating assignments:')
        for num in range(self.num_assignments):
            assignment = mommy.prepare(
                'core.Assignment',
                parentnode=period,
                long_name='Assignment#{}'.format(num),
                short_name='assignment#{}'.format(num),
                publishing_time=period.start_time + timezone.timedelta(days=publishing_time_from_period_start),
                first_deadline=period.start_time + timezone.timedelta(days=first_deadline_from_period_start))
            created_assignments.append(assignment)
            publishing_time_from_period_start += 7
            first_deadline_from_period_start += 7
            self.progressdots.increment_progress()
        self.progressdots.reset()
        sys.stdout.write('\n')
        Assignment.objects.bulk_create(created_assignments)
        for assignment in Assignment.objects.filter(parentnode=period):
            self.__create_assignmentgroups_for_assignment(assignment=assignment)

    def __create_relatedstudents_for_period(self, period):
        """
        Generate RelatedStudents for period.
        """
        sys.stdout.write('Adding students to {}:'.format(period))
        for user in get_user_model().objects.filter(shortname__istartswith='student'):
            mommy.make('core.RelatedStudent', user=user, period=period)
            self.progressdots.increment_progress()
        self.progressdots.reset()
        sys.stdout.write('\n')

    def __create_relatedexaminers_for_period(self, period):
        """
        Generate RelatedExaminers for period.
        """
        sys.stdout.write('Adding examiners to {}:'.format(period))
        for user in get_user_model().objects.filter(shortname__istartswith='examiner'):
            mommy.make('core.RelatedExaminer', user=user, period=period)
            self.progressdots.increment_progress()
        self.progressdots.reset()
        sys.stdout.write('\n')

    def __create_periods(self, subject):
        """
        Generate periods on subject.
        """
        for num in range(self.num_periods):
            sys.stdout.write('Create period Period#{}:\n'.format(num))
            period = mommy.make('core.Period',
                                parentnode=subject,
                                long_name='Period#{}'.format(num),
                                short_name='period#{}'.format(num),
                                start_time=timezone.now() - timezone.timedelta(days=90),
                                end_time=timezone.now() + timezone.timedelta(days=90))
            self.__create_relatedstudents_for_period(period=period)
            self.__create_relatedexaminers_for_period(period=period)
            self.__create_assignments_for_period(period=period)

    def __create_subjects(self):
        """
        Generate Subjects.
        """
        for num in range(self.num_subjects):
            subject = mommy.make('core.Subject',
                                 long_name='Subject#{}'.format(num),
                                 short_name='subject#{}'.format(num))
            self.__create_periods(subject=subject)

    def build_db(self):
        self.__create_student_users()
        self.__create_examiner_users()
        self.__create_subjects()


class Command(BaseCommand):
    help = """
    (WORK-IN-PROGRESS) But can be used for making a simple large database.
    
    Generate a large database with complex couplings in groups. Used for view performance testing.
    
    For each assignment, a minimum of 10 students will be created for each assignment. An AssignmentGroup will be 
    created for each student, unless the argument --project-groups is given, then two and two students will be grouped 
    together.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--num-subjects',
            dest='num_subjects',
            type=int,
            default=1,
            help='How many subjects to create.')
        parser.add_argument(
            '--num-periods',
            dest='num_periods',
            type=int,
            default=1,
            help='How many periods to create for each subject.')
        parser.add_argument(
            '--num-assignments',
            dest='num_assignments',
            type=int,
            default=1,
            help='How many assignments to create for each period.')
        parser.add_argument(
            '--num-students',
            dest='num_students',
            type=int,
            default=10,
            help='Minimum number of students to create for each assignment.')
        parser.add_argument(
            '--num-comments',
            dest='num_comments',
            type=int,
            default=5,
            help='Number of comments that is added for each user in a group(examiners and students)')

        parser.add_argument(
            '--project-groups',
            action='store_true',
            dest='project_groups',
            default=False,
            help='Add students two and two students to project groups')

    def __clean_and_migrate(self):
        call_command('dbdev_reinit')
        call_command('migrate')
        call_command('ievvtasks_customsql', '-i', '-r')

    def __create_superuser(self):
        get_user_model().objects.create_superuser(
            shortname='grandma@example.com',
            password='test')

    def handle(self, *args, **options):
        self.__clean_and_migrate()
        self.__create_superuser()
        num_subjects = options.get('num_subjects')
        num_periods = options.get('num_periods')
        num_assignments = options.get('num_assignments')
        num_students = options.get('num_students')
        num_comments = options.get('num_comments')
        project_groups = options.get('project_groups')

        with transaction.atomic():
            DatabaseBuilder(
                num_subjects=num_subjects,
                num_periods=num_periods,
                num_assignments=num_assignments,
                num_students=num_students,
                num_comments=num_comments,
                project_groups=project_groups,
            ).build_db()

            print 'User count: {}'.format(get_user_model().objects.count())
            print 'Subject count: {}'.format(Subject.objects.count())
            print 'Period count: {}'.format(Period.objects.count())
            print 'Assignment count: {}'.format(Assignment.objects.count())
            print 'RelatedStudent count: {}'.format(RelatedStudent.objects.count())
            print 'RelatedExaminer count: {}'.format(RelatedExaminer.objects.count())
            print 'AssignmentGroup count: {}'.format(AssignmentGroup.objects.count())
            print 'Candidate count: {}'.format(Candidate.objects.count())
            print 'Examiner count: {}'.format(Examiner.objects.count())
            print 'FeedbackSet count: {}'.format(FeedbackSet.objects.count())
            print 'GroupComment count: {}'.format(GroupComment.objects.count())
            print 'CommentFile count: {}'.format(CommentFile.objects.count())


