import logging
from datetime import datetime
from datetime import timedelta
from devilry_developer.testhelpers.datebuilder import DateTimeBuilder
from devilry_developer.testhelpers.corebuilder import UserBuilder
from django.core.management.base import BaseCommand
from django.core.management.base import BaseCommand


from devilry.apps.core.models import Node
from devilry.apps.core.models import Subject
from devilry.apps.core.models import Period
from devilry.apps.core.models import Assignment
from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import Deadline
from devilry.apps.core.models import Delivery
from devilry.apps.core.models import StaticFeedback
from devilry.apps.core.models import FileMeta



class Command(BaseCommand):
    help = 'Create a database for demo/testing.'

    def handle(self, *args, **options):
        UserBuilder('grandma', full_name='Elvira "Grandma" Coot',
            is_superuser=True, is_staff=True)
        self.create_nodes()
        self.create_subjects()
        self.create_periods()
        self.create_assignments()


    def create_nodes(self):
        self.node_duckburgh = Node.objects.create(
            short_name='duckburgh',
            long_name='Duckburgh University')
        self.node_duckburgh_faculty_of_math = self.node_duckburgh.child_nodes.create(
            short_name='math',
            long_name='Faculty of Mathematics')
        self.node_duckburgh_faculty_of_informatics = self.node_duckburgh.child_nodes.create(
            short_name='inf',
            long_name='Faculty of Informatics')

    def create_subjects(self):
        self.subject_duck1010 = self.node_duckburgh_faculty_of_informatics.subjects.create(
            short_name='duck1010',
            long_name='DUCK1010 - Object oriented programming'
        )
        self.subject_duck1100 = self.node_duckburgh_faculty_of_informatics.subjects.create(
            short_name='duck1100',
            long_name='DUCK1100 - Getting started with Python'
        )

    def create_periods(self):
        index = 0
        for short_name, long_name in (
            ('current', 'Current Period Example'),
            ('old', 'Old Period Example'),
            ('veryold', 'Very old Period Example'),
            ('ancient', 'Ancient Period Example'),
        ):
            Period.objects.create_many(
                Subject.objects.all(),
                short_name=short_name,
                long_name=long_name,
                start_time=DateTimeBuilder.now().minus(days=index*365 + 30*3),
                end_time=DateTimeBuilder.now().minus(days=index*365 - 30*3)
            )
            index += 1



    def _setup_four_obligatory_assignments(self, subjects, assignmentconfigs):
        period_days = 30 * 6
        assignments = []
        for period in Period.objects.filter(parentnode__in=subjects):
            index = 1
            assignment_duration_days = (period_days-20)/len(assignmentconfigs)
            for short_name, long_name, include_in_active_period in assignmentconfigs:
                if not include_in_active_period and datetime.now() > period.start_time:
                    break
                publishing_time = period.start_time + timedelta(days=index*assignment_duration_days)
                assignments.append(Assignment(
                    short_name=short_name,
                    long_name=long_name,
                    publishing_time=publishing_time,
                    parentnode=period
                ))
                index += 1
        return assignments


    def create_assignments(self):
        assignments = self._setup_four_obligatory_assignments(
            subjects=[self.subject_duck1010],
            assignmentconfigs=[
                ('oblig1', 'Obligatory Assignment 1', True),
                ('oblig2', 'Obligatory Assignment 2', True),
                ('oblig3', 'Obligatory Assignment 3', True),
                ('oblig4', 'Obligatory Assignment 4', False),
            ])
        assignments += self._setup_four_obligatory_assignments(
            subjects=[self.subject_duck1100],
            assignmentconfigs=[
                ('week1', 'Week 1', True),
                ('week2', 'Week 2', True),
                ('week3', 'Week 3', True),
                ('week4', 'Week 4', True),
                ('week5', 'Week 5', True),
                ('week6', 'Week 6', True),
                ('week7', 'Week 7', True),
                ('week8', 'Week 8', True),
                ('week9', 'Week 9', False),
                ('week10', 'Week 10', False),
                ('week11', 'Week 11', False),
            ])
        Assignment.objects.bulk_create(assignments)