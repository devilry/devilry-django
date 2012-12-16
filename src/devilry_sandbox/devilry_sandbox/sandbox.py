from datetime import datetime, timedelta
from random import randint
from django.contrib.auth.models import User
from django.db import IntegrityError
from devilry.apps.core.models import Node
from devilry.apps.core.models import Subject
from devilry.apps.core.models import Period
from logging import getLogger


logger = getLogger(__name__)


class Sandbox(object):
    """
    A simple sandboxing system for providing the admins with a more or less isolated environment.
    """
    STUDENTS = (('dewey', 'Dewey Duck', 'group1'),
                ('louie', 'Louie Duck', 'group1'),
                ('huey', 'Huey Duck', 'group1'),
                ('april', 'April Duck', 'group2'),
                ('june', 'June Duck', 'group2'),
                ('july', 'July Duck', 'group2'),
                ('baldr', 'God of Beauty', 'group1'),
                ('freyja', 'Goddess of Love', 'group1'),
                ('freyr', 'God of Fertility', 'group1'),
                ('kvasir', 'God of Inspiration', 'group1'),
                ('loki', 'Trickster and god of Mischief', 'group2'),
                ('thor', 'God of thunder and Battle', 'group2'),
                ('odin', 'The "All Father"', 'group2'))

    EXAMINERS = (('donald', 'Donald Duck', 'group1'),
                 ('scrooge', 'Scrooge McDuck', 'group2'))

    def __init__(self, nodename='sandbox'):
        self.nodename = nodename
        self.subject, self.unique_number = self.create_autonamed_subject()

    def _rootnode_exists(self):
        return Node.objects.filter(short_name=self.nodename).exists()

    def _create_rootnode_if_not_exists(self):
        if not self._rootnode_exists():
            node = Node.objects.create(short_name=self.nodename,
                long_name=self.nodename)
        else:
            node = Node.objects.get(short_name=self.nodename)
        return node

    def create_user(self, username, fullname):
        username = '{0}{1}'.format(username, self.unique_number)
        user = User.objects.create(username=username,
            email='{0}@example.com'.format(username))
        user.devilryuserprofile.full_name = '{0} {1}'.format(fullname, self.unique_number)
        user.devilryuserprofile.save()
        user.set_password(username)
        user.save()
        return user

    def add_or_get_user(self, username, fullname):
        try:
            username = username
            user = self.create_user(username, fullname)
        except IntegrityError:
            return User.objects.get(username=username)
        else:
            return user

    def add_relatedstudents(self, period):
        for username, fullname, tags in self.STUDENTS:
            period.relatedstudent_set.create(user=self.add_or_get_user(username, fullname),
                candidate_id='sec-{0}'.format(randint(0, 10000000)),
                tags=tags)

    def add_relatedexaminers(self, period):
        for username, fullname, tags in self.EXAMINERS:
            period.relatedexaminer_set.create(user=self.add_or_get_user(username, fullname),
                tags=tags)

    def create_autonamed_subject(self, shortformat='testcourse{num}', longformat='Test course {num}'):
        tries = 0
        randrange = (0, 9999)
        while True:
            # We try with a relatively low range first, but in the unlikely case of that
            # not working, we use a higher max/min
            if tries > 50:
                randrange = (100000, 999999999)
            elif tries > 5:
                randrange = (10000, 99999)
            num = randint(*randrange)
            tries += 1
            short_name = shortformat.format(num=num)
            long_name = longformat.format(num=num)
            try:
                subject = self._create_subject(short_name, long_name)
            except IntegrityError:
                logger.info('Could not create subject %s. Trying again with a new name.',
                    short_name)
            else:
                logger.info('Created subject: %s', short_name)
                return subject, num

    def _create_subject(self, short_name, long_name):
        node = self._create_rootnode_if_not_exists()
        subject = node.subjects.create(short_name=short_name,
            long_name=long_name)
        return subject

    def create_period(self, short_name, long_name):
        period = self.subject.periods.create(
            short_name=short_name,
            long_name=long_name,
            start_time=datetime.now() - timedelta(days=30),
            end_time=datetime.now() + timedelta(days=150))
        self.add_relatedstudents(period)
        self.add_relatedexaminers(period)
        return period