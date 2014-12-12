from datetime import timedelta
import random
from django.core.management.base import BaseCommand
from django.contrib.webdesign import lorem_ipsum

from devilry.apps.markup.parse_markdown import markdown_full
from devilry_developer.testhelpers.datebuilder import DateTimeBuilder
from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry_developer.testhelpers.corebuilder import NodeBuilder
# from devilry.apps.core.models import Node
# from devilry.apps.core.models import Subject
# from devilry.apps.core.models import Period
# from devilry.apps.core.models import Assignment
# from devilry.apps.core.models import AssignmentGroup
# from devilry.apps.core.models import Deadline
# from devilry.apps.core.models import Delivery
from devilry.apps.core.models import StaticFeedback
# from devilry.apps.core.models import FileMeta
from devilry.apps.core.models import RelatedStudent
from devilry.apps.core.models import RelatedExaminer




bad_students = [
    ('dewey', 'Dewey Duck'),
    ('louie', 'Louie Duck'),
    ('huey', 'Huey Duck'),
    ('june', 'June Duck'),
    ('july', 'July Duck')
]

good_students = [
    ('baldr', 'God of Beauty'),
    ('freyja', 'Goddess of Love'),
    ('freyr', 'God of Fertility'),
    ('kvasir', 'God of Inspiration'),
    ('loki', 'Trickster and god of Mischief'),
    ('odin', 'The "All Father"')
]



class Command(BaseCommand):
    help = 'Create a database for demo/testing.'

    def handle(self, *args, **options):
        self.grandma = UserBuilder('grandma',
            full_name='Elvira "Grandma" Coot',
            is_superuser=True, is_staff=True).user
        self.thor = UserBuilder('thor',
            full_name='God of Thunder and Battle').user
        self.donald = UserBuilder('donald',
            full_name='Donald Duck').user
        self.scrooge = UserBuilder('scrooge',
            full_name='Scrooge McDuck').user
        self.examiners = [self.donald, self.scrooge]

        self.bad_students = {}
        for username, full_name in bad_students:
            self.bad_students[username] = UserBuilder(username, full_name=full_name).user
        self.good_students = {}
        for username, full_name in good_students:
            self.good_students[username] = UserBuilder(username, full_name=full_name).user
        self.allstudentslist = list(self.bad_students.values()) + list(list(self.good_students.values()))
        self.april = UserBuilder('april', full_name='April Duck').user

        for user in [self.thor, self.donald, self.april]:
            user.devilryuserprofile.languagecode = 'nb'
            user.devilryuserprofile.save()

        self.duckburgh = NodeBuilder('duckburgh', long_name="University of Duckburgh")
        self.add_duck1100()


    def build_random_pointassignmentdata(self,
            periodbuilder, weeks_ago, short_name, long_name, filecount,
            feedback_percent=100):
        assignmentbuilder = periodbuilder.add_assignment_x_weeks_ago(
            weeks=weeks_ago,
            short_name=short_name, long_name=long_name,
            passing_grade_min_points=1,
            grading_system_plugin_id='devilry_gradingsystemplugin_points',
            points_to_grade_mapper='raw-points',
            max_points=filecount,
            first_deadline=DateTimeBuilder.now().minus(weeks=weeks_ago-1)
        )
        def create_group(user, minpoints, maxpoints, examiner):
            groupbuilder = assignmentbuilder.add_group(
                students=[user], examiners=[examiner])
            deadlinebuilder = groupbuilder\
                .add_deadline(
                    deadline=assignmentbuilder.assignment.first_deadline)

            deliverybuilder = deadlinebuilder.add_delivery_x_hours_before_deadline(
                hours=random.randint(1, 30))
            for number in xrange(filecount):
                deliverybuilder.add_filemeta(
                    filename='{}_{}.py'.format(assignmentbuilder.assignment.short_name, number),
                    data='print "Hello world"')
            if random.randint(0, 100) <= feedback_percent:
                feedback = StaticFeedback.from_points(
                    assignment=assignmentbuilder.assignment,
                    saved_by=examiner,
                    delivery=deliverybuilder.delivery,
                    rendered_view=self._lorem_paras(random.randint(1, 5)),
                    points=random.randint(minpoints, maxpoints))
                feedback.save()
        for user in self.bad_students.itervalues():
            create_group(user, minpoints=0, maxpoints=filecount/2,
                examiner=random.choice(self.examiners))
        for user in self.good_students.itervalues():
            create_group(user, minpoints=filecount/2, maxpoints=filecount,
                examiner=random.choice(self.examiners))
        create_group(self.april, minpoints=1, maxpoints=filecount,
            examiner=self.donald)
        return assignmentbuilder

    def _as_relatedstudents(self, users, tags=''):
        return [RelatedStudent(user=user, tags=tags) for user in users]

    def add_duck1100(self):
        duck1100 = self.duckburgh.add_subject('duck1100',
            long_name='DUCK1100 - Programming for the natural sciences')
        duck1100.add_admins(self.thor)

        relatedstudents = [RelatedStudent(user=self.april, tags='group1')]
        relatedstudents.extend(self._as_relatedstudents(self.good_students.values(), 'group1'))
        relatedstudents.extend(self._as_relatedstudents(self.bad_students.values(), 'group2'))
        testsemester = duck1100.add_6month_active_period(
            short_name='testsemester', long_name='Testsemester',
            relatedstudents=relatedstudents,
            relatedexaminers=[
                RelatedExaminer(user=self.thor, tags=''),
                RelatedExaminer(user=self.donald, tags='group1'),
                RelatedExaminer(user=self.scrooge, tags='group2')
            ])

        old_relatedstudentusers = [
            self.april, self.bad_students['dewey'],
            self.bad_students['louie'], self.bad_students['june'],
            self.good_students['loki'], self.good_students['kvasir']]
        old_relatedstudents = self._as_relatedstudents(old_relatedstudentusers)
        oldtestsemester = duck1100.add_6month_lastyear_period(
            short_name='oldtestsemester', long_name='Old testsemester',
            relatedstudents=old_relatedstudents,
            relatedexaminers=[
                RelatedExaminer(user=self.thor, tags=''),
                RelatedExaminer(user=self.donald, tags='group1'),
                RelatedExaminer(user=self.scrooge, tags='group2')
            ])

        for periodbuilder, weekoffset in [
                (oldtestsemester, 52),
                (testsemester, 0)]:
            week1 = self.build_random_pointassignmentdata(
                periodbuilder=periodbuilder,
                weeks_ago=weekoffset+6, filecount=4,
                short_name='week1', long_name='Week 1')
            week2 = self.build_random_pointassignmentdata(
                periodbuilder=periodbuilder,
                weeks_ago=weekoffset+5, filecount=2,
                short_name='week2', long_name='Week 2')
            week3 = self.build_random_pointassignmentdata(
                periodbuilder=periodbuilder,
                weeks_ago=weekoffset+4, filecount=4,
                short_name='week3', long_name='Week 3')
            week4 = self.build_random_pointassignmentdata(
                periodbuilder=periodbuilder,
                weeks_ago=weekoffset+3, filecount=8,
                short_name='week4', long_name='Week 4')

            if weekoffset == 0:
                week5 = self.build_random_pointassignmentdata(
                    periodbuilder=periodbuilder,
                    weeks_ago=weekoffset+1, filecount=6,
                    short_name='week5', long_name='Week 5',
                    feedback_percent=50)

                week6 = periodbuilder.add_assignment_x_weeks_ago(
                    weeks=weekoffset, short_name='week6', long_name='Week 6',
                    passing_grade_min_points=1,
                    grading_system_plugin_id='devilry_gradingsystemplugin_points',
                    points_to_grade_mapper='raw-points',
                    max_points=6
                )
                for user in self.allstudentslist + [self.april]:
                    examiner = random.choice(self.examiners)
                    week6\
                        .add_group(students=[user], examiners=[examiner])\
                        .add_deadline(deadline=DateTimeBuilder.now().plus(days=7))
            else:
                week5 = self.build_random_pointassignmentdata(
                    periodbuilder=periodbuilder,
                    weeks_ago=weekoffset+1, filecount=1,
                    short_name='week5', long_name='Week 5')
                week6 = self.build_random_pointassignmentdata(
                    periodbuilder=periodbuilder,
                    weeks_ago=weekoffset, filecount=2,
                    short_name='week6', long_name='Week 6')


    def _lorem_paras(self, count):
        return markdown_full(u'\n\n'.join(lorem_ipsum.paragraphs(count, common=False)))
