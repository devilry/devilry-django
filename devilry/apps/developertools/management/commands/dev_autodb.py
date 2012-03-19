import logging
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.core import management

from devilry.apps.core.testhelper import TestHelper
from devilry.utils.command import setup_logging, get_verbosity



logger = logging.getLogger(__name__)


def autocreate_usernames(fullnames):
    return [(name.lower().replace(' ', ''), name) for name in fullnames]
def get_usernames(users):
    return set([user[0] for user in users])

bad_students = autocreate_usernames(['John Smith', 'Joe Doe', 'Bob Smith',
                                     'Mike Smith', 'Juan Carlos', 'Jane Doe',
                                     'Mike Jones', 'David Smith', 'Sarah Doll',
                                     'James Smith'])
bad_students_usernames = get_usernames(bad_students)

medium_students = [('dewey', 'Dewey Duck'),
                   ('louie', 'Louie Duck'),
                   ('huey', 'Huey Duck'),
                   ('april', 'April Duck'),
                   ('june', 'June Duck'),
                   ('july', 'July Duck')]
medium_students_usernames = get_usernames(medium_students)

good_students = [('baldr', 'God of Beauty'),
                 ('freyja', 'Goddess of Love'),
                 ('freyr', 'God of Fertility'),
                 ('kvasir', 'God of Inspiration'),
                 ('loki', 'Trickster and god of Mischief'),
                 ('thor', 'God of thunder and Battle'),
                 ('odin', 'The "All Father"')]
good_students_usernames = get_usernames(good_students)


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
        self._setTagsFor(group, username)
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

    def _onlyNames(self, nameWithExtras):
        return [name.split(':')[0] for name in nameWithExtras]

    def _getUser(self, username):
        return getattr(self.testhelper, username)

    def _addRelatedExaminersFromList(self, period, listOfUsernames):
        for username in listOfUsernames:
            tags = ','.join(self._getTagsForExaminer(username))
            period.relatedexaminer_set.create(user=self._getUser(username),
                                              tags=tags)

    def _addRelatedExaminers(self, period):
        self._addRelatedExaminersFromList(period, self.examiners.keys())

    def _addRelatedStudentsFromList(self, period, listOfUsernames):
        for username in listOfUsernames:
            tags = ','.join(self._getTagsFor(username))
            period.relatedstudent_set.create(user=self._getUser(username),
                                              tags=tags)

    def _addRelatedStudents(self, period):
        self._addRelatedStudentsFromList(period, good_students_usernames)
        self._addRelatedStudentsFromList(period, medium_students_usernames)
        self._addRelatedStudentsFromList(period, bad_students_usernames)

    def create_duck1100(self):
        assignments = ['week{0}:pub({1})'.format(weeknum, weeknum*7) for weeknum in xrange(1, 10)]
        periods = ['year20xx:begins(-2):ends(6):ln(Year 20xx)',
                   'inthepast:begins(-14):ends(6):ln(Year 20xx minus one year)']
        self.testhelper.add(nodes="duckburgh:admin(duckburghadmin).ifi:admin(ifiadmin)",
                            subjects=["duck1100:ln(DUCK1100 - Getting started with python)"],
                            periods=periods,
                            assignments=assignments)
        anotherTryVerdict = {'grade': '5/20', 'points': 5, 'is_passing_grade': False}
        failedVerdict = {'grade': '2/20', 'points': 2, 'is_passing_grade': False}
        okVerdict = {'grade': '12/20', 'points': 12, 'is_passing_grade': True}
        goodVerdict = {'grade': '18/20', 'points': 18, 'is_passing_grade': True}

        assignmentnames = self._onlyNames(assignments)
        periodnames = self._onlyNames(periods)
        for periodname in periodnames:
            periodpath = 'duckburgh.ifi;duck1100.' + periodname
            period = self.testhelper.get_object_from_path(periodpath)
            self._addRelatedStudents(period)
            self._addRelatedExaminers(period)
            self._addBadGroups(periodpath, assignmentnames, anotherTryVerdict, failedVerdict)
            self._addMediumGroups(periodpath, assignmentnames, anotherTryVerdict, okVerdict)
            self._addGoodGroups(periodpath, assignmentnames, goodVerdict)

    def create_duck1010(self):
        assignments = ['oblig{num}:pub({pub}):ln(Obligatorisk oppgave {num})'.format(num=num, pub=num*40) for num in xrange(1, 4)]
        periods = ['year20xx:begins(-2):ends(6):ln(Year 20xx)',
                   'inthepast:begins(-14):ends(6):ln(Year 20xx minus one year)']
        self.testhelper.add(nodes="duckburgh:admin(duckburghadmin).ifi:admin(ifiadmin)",
                            subjects=["duck1010:ln(DUCK1010 - Objektorientert programmering)"],
                            periods=periods,
                            assignments=assignments)
        anotherTryVerdict = {'grade': 'Not approved', 'points': 0, 'is_passing_grade': False}
        failedVerdict = {'grade': 'Not approved', 'points': 0, 'is_passing_grade': False}
        okVerdict = {'grade': 'Approved', 'points': 1, 'is_passing_grade': True}
        goodVerdict = {'grade': 'Approved', 'points': 1, 'is_passing_grade': True}

        assignmentnames = [name.split(':')[0] for name in assignments]
        periodnames = self._onlyNames(periods)
        for periodname in periodnames:
            periodpath = 'duckburgh.ifi;duck1010.' + periodname
            period = self.testhelper.get_object_from_path(periodpath)
            self._addRelatedStudents(period)
            self._addRelatedExaminers(period)
            self._addBadGroups(periodpath, assignmentnames, anotherTryVerdict, failedVerdict)
            self._addMediumGroups(periodpath, assignmentnames, anotherTryVerdict, okVerdict)
            self._addGoodGroups(periodpath, assignmentnames, goodVerdict)

    def create_users(self, list_of_users):
        for username, fullname in list_of_users:
            self.testhelper.create_user(username, fullname)

    def _distributeStudentToExaminers(self):
        bad_all = list(bad_students_usernames)
        bad_firsthalf = set(bad_all[:-len(bad_all)/2])
        bad_secondhalf = set(bad_all[len(bad_all)/2:])
        self.examiners = {'donald': good_students_usernames.union(bad_firsthalf),
                          'scrooge': medium_students_usernames.union(bad_secondhalf)}

    def _getExaminerFor(self, username):
        for examiner, usernames in self.examiners.iteritems():
            if username in usernames:
                return examiner
        raise LookupError('No examiner defined for {0}'.format(username))

    def _getTagsFor(self, username):
        tags = []
        if self._getExaminerFor(username) == 'donald':
            tags = ['group1']
        elif self._getExaminerFor(username) == 'scrooge':
            tags = ['group2']
        if username in good_students_usernames:
            tags.append('goodstudent')
        elif username in bad_students_usernames:
            tags.append('needs_extra_help')
        return tags

    def _setTagsFor(self, group, username):
        for tag in self._getTagsFor(username):
            group.tags.create(tag=tag)

    def _getTagsForExaminer(self, username):
        if username == 'donald':
            return ['group1']
        elif username == 'scrooge':
            return ['group2']

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
