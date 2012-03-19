import logging
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.core import management

from devilry.apps.core.testhelper import TestHelper
from devilry.utils.command import setup_logging, get_verbosity



logger = logging.getLogger(__name__)


def autocreate_usernames(fullnames):
    return [(name.lower().replace(' ', ''), name) for name in fullnames]

bad_students = autocreate_usernames(['John Smith', 'Joe Doe', 'Bob Smith',
                                     'Mike Smith', 'Juan Carlos', 'Jane Doe',
                                     'Mike Jones', 'David Smith', 'Sarah Doll',
                                     'James Smith'])
medium_students = [('dewey', 'Dewey Duck'),
                   ('louie', 'Louie Duck'),
                   ('huey', 'Huey Duck'),
                   ('april', 'April Duck'),
                   ('june', 'June Duck'),
                   ('july', 'July Duck')]
good_students = [('baldr', 'God of beauty'),
                 ('freyja', 'Goddess of love'),
                 ('freyr', 'God of fertility'),
                 ('kvasir', 'God of inspiration'),
                 ('loki', 'Trickster and god of mischief'),
                 ('thor', 'God of thunder and battle'),
                 ('odin', 'The "All Father"')]


def days_in_future(days):
    return datetime.now() + timedelta(days=days)

class Command(BaseCommand):
    help = 'Create a database of static data for demo purposes.'

    def _createGroup(self, periodpath, assignment, groupname, groupnum, username):
        examiner = self._getExaminerFor(username)
        path = '{periodpath}.{assignment}.{groupname}{groupnum}'.format(**vars())
        extras = ':candidate({username}):examiner({examiner})'.format(**vars())
        to_be_added = path + extras
        logger.debug('Creating ' + to_be_added)
        self.testhelper.add_to_path(to_be_added)
        group = self.testhelper.get_object_from_path(path)
        logger.debug('Created group id:{id}, path:{path}'.format(id=group.id, path=group))
        return path, group

    def _addBadGroups(self, periodpath, assignments, anotherTryVerdict, failedVerdict):
        for groupnum, names in enumerate(bad_students):
            username, fullname = names
            for assignment in assignments:
                path, group = self._createGroup(periodpath, assignment, 'badgroup', groupnum, username)
                self.testhelper.add_to_path(path + '.d1:ends(7)')
                since_pubishingtime = datetime.now() - group.parentnode.publishing_time
                if since_pubishingtime.days >= 8:
                    self.testhelper.add_delivery(path, {'bad.py': ['print ', 'bah']},
                                                 time_of_delivery=-1)
                    self.testhelper.add_delivery(path, {'superbad.py': ['print ', 'superbah']},
                                                 time_of_delivery=1)
                    self.testhelper.add_feedback(path, verdict=anotherTryVerdict)
                    self.testhelper.add_to_path(path + '.d2:ends(14)')
                if since_pubishingtime.days >= 13:
                    self.testhelper.add_delivery(path, {'stillbad.py': ['print ', 'bah']}, time_of_delivery=-1)
                    self.testhelper.add_feedback(path, verdict=failedVerdict)

    def _addMediumGroups(self, periodpath, assignments, anotherTryVerdict, okVerdict):
        for groupnum, names in enumerate(medium_students):
            username, fullname = names
            for assignment in assignments:
                path, group = self._createGroup(periodpath, assignment, 'mediumgroup', groupnum, username)
                self.testhelper.add_to_path(path + '.d1:ends(7)')

                since_pubishingtime = datetime.now() - group.parentnode.publishing_time
                if since_pubishingtime.days >= 8:
                    self.testhelper.add_delivery(path, {'bad.py': ['print ', 'bah']},
                                                 time_of_delivery=-1)
                    self.testhelper.add_delivery(path, {'superbad.py': ['print ', 'superbah']},
                                                 time_of_delivery=1)
                    self.testhelper.add_feedback(path, verdict=anotherTryVerdict)
                    self.testhelper.add_to_path(path + '.d2:ends(14)')
                if since_pubishingtime.days >= 15:
                    self.testhelper.add_delivery(path, {'stillbad.py': ['print ', 'bah']}, time_of_delivery=-1)
                    self.testhelper.add_feedback(path, verdict=anotherTryVerdict)
                    self.testhelper.add_to_path(path + '.d2:ends(21)')
                if since_pubishingtime.days >= 22:
                    self.testhelper.add_delivery(path, {'ok.py': ['print ', 'ok']}, time_of_delivery=-1)
                    self.testhelper.add_feedback(path, verdict=okVerdict)

    def _addGoodGroups(self, periodpath, assignments, goodVerdict):
        for groupnum, names in enumerate(good_students):
            username, fullname = names
            for assignment in assignments:
                path, group = self._createGroup(periodpath, assignment, 'goodgroup', groupnum, username)
                self.testhelper.add_to_path(path + '.d1:ends(7)')

                since_pubishingtime = datetime.now() - group.parentnode.publishing_time
                if since_pubishingtime.days >= 8:
                    self.testhelper.add_delivery(path, {'good.py': ['print ', 'almostperfect']},
                                                 time_of_delivery=-1)
                    self.testhelper.add_feedback(path, verdict=goodVerdict)


    def create_duck1100(self):
        assignments = ['week{0}:pub({1})'.format(weeknum, weeknum*7) for weeknum in xrange(1, 10)]
        self.testhelper.add(nodes="duckburgh:admin(duckburghadmin).ifi:admin(ifiadmin)",
                            subjects=["duck1100:ln(DUCK1100 - Getting started with python)"],
                            periods=["year20xx:begins(-2):ends(6):ln(Year 20xx)", 'inthepast:begins(-14):ends(6):ln(Year 20xx minus one)'],
                            assignments=assignments)
        anotherTryVerdict = {'grade': '5/20', 'points': 5, 'is_passing_grade': False}
        failedVerdict = {'grade': '2/20', 'points': 2, 'is_passing_grade': False}
        okVerdict = {'grade': '12/20', 'points': 12, 'is_passing_grade': True}
        goodVerdict = {'grade': '18/20', 'points': 18, 'is_passing_grade': True}

        assignmentnames = [name.split(':')[0] for name in assignments]
        periodpath = 'duckburgh.ifi;duck1100.year20xx'
        self._addBadGroups(periodpath, assignmentnames, anotherTryVerdict, failedVerdict)
        self._addMediumGroups(periodpath, assignmentnames, anotherTryVerdict, okVerdict)
        self._addGoodGroups(periodpath, assignmentnames, goodVerdict)

    def create_duck1010(self):
        assignments = ['oblig{num}:pub({pub}):ln(Obligatorisk oppgave {num})'.format(num=num, pub=num*40) for num in xrange(1, 4)]
        self.testhelper.add(nodes="duckburgh:admin(duckburghadmin).ifi:admin(ifiadmin)",
                            subjects=["duck1010:ln(DUCK1010 - Objektorientert programmering)"],
                            periods=["year20xx:begins(-2):ends(6):ln(Year 20xx)", 'inthepast:begins(-14):ends(6):ln(Year 20xx minus one)'],
                            assignments=assignments)
        anotherTryVerdict = {'grade': 'approved', 'points': 0, 'is_passing_grade': False}
        failedVerdict = {'grade': 'not approved', 'points': 0, 'is_passing_grade': False}
        okVerdict = {'grade': 'approved', 'points': 1, 'is_passing_grade': True}
        goodVerdict = {'grade': 'not approved', 'points': 1, 'is_passing_grade': True}

        assignmentnames = [name.split(':')[0] for name in assignments]
        periodpath = 'duckburgh.ifi;duck1010.year20xx'
        self._addBadGroups(periodpath, assignmentnames, anotherTryVerdict, failedVerdict)
        self._addMediumGroups(periodpath, assignmentnames, anotherTryVerdict, okVerdict)
        self._addGoodGroups(periodpath, assignmentnames, goodVerdict)

    def create_users(self, list_of_users):
        for username, fullname in list_of_users:
            self.testhelper.create_user(username, fullname)

    def _distributeStudentToExaminers(self):
        bad_firsthalf = bad_students[:-len(bad_students)/2]
        bad_secondhalf = bad_students[len(bad_students)/2:]
        def get_usernames(users):
            return set([user[0] for user in users])
        self.examiners = {'donald': get_usernames(good_students + bad_firsthalf),
                          'scrooge': get_usernames(medium_students + bad_secondhalf)}

    def _getExaminerFor(self, username):
        for examiner, usernames in self.examiners.iteritems():
            if username in usernames:
                return examiner
        raise LookupError('No examiner defined for {0}'.format(username))

    def handle(self, *args, **options):
        verbosity = get_verbosity(options)
        setup_logging(verbosity)
        management.call_command('flush', verbosity=verbosity, interactive=False)

        self.testhelper = TestHelper()
        self.testhelper.create_superuser('grandma')
        self.create_users(bad_students)
        self.create_users(medium_students)
        self.create_users(good_students)
        self.create_users([('donald', 'Donald Duck'),
                           ('daisy', 'Daisy Duck'),
                           ('clarabelle', 'Clarabelle Duck'),
                           ('scrooge', 'Scrooge McDuck'),
                           ('della', 'Duck'),
                           ('gladstone', 'Gladstone Gander'),
                           ('fethry', 'Fethry Duck')])
        self._distributeStudentToExaminers()
        self.create_duck1100()
        self.create_duck1010()
