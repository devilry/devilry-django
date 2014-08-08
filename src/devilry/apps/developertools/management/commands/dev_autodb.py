"""
This command creates a demo database for Devilry. See dev_autodb.readme.md for more info.
"""
import logging
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.core import management
from optparse import make_option

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




rendered_view_good = r"""
<p>Very good. Please keep the quality of your deliveries at this level for the rest of the assignments.</p>

<h1>This is a heading</h1>
<p>Fusce dapibus, tellus ac cursus commodo, tortor mauris condimentum nibh, ut fermentum massa justo sit amet risus. Integer posuere erat a ante venenatis dapibus posuere velit aliquet. Vestibulum id ligula porta felis euismod semper. Nullam id dolor id nibh ultricies vehicula ut id elit.</p>
<p>Cras mattis consectetur purus sit amet fermentum. Nullam quis risus eget urna mollis ornare vel eu leo. Etiam porta sem malesuada magna mollis euismod. Vestibulum id ligula porta felis euismod semper. Praesent commodo cursus magna, vel scelerisque nisl consectetur et.</p>

<h2>Subheading (heading 2)</h2>
<p>Morbi leo risus, porta ac consectetur ac, vestibulum at eros. Sed posuere consectetur est at lobortis. Curabitur blandit tempus porttitor. Donec sed odio dui. Maecenas faucibus mollis interdum.</p>
<ul>
    <li>Item one</li>
    <li>Item two</li>
</ul>


<h3>Subsubheading (heading 3)</h3>
<p>Math example:</p>

$mathblock$
\frac{d}{dx}\left( \int_{0}^{x} f(u)\,du\right)=f(x)
$/mathblock$
"""

rendered_view_ok = """
<p>I will let you pass this time. Next time I expect far better from you.</p>

<h1>This is a heading</h1>
<p>Fusce dapibus, tellus ac cursus commodo, tortor mauris condimentum nibh, ut fermentum massa justo sit amet risus. Integer posuere erat a ante venenatis dapibus posuere velit aliquet. Vestibulum id ligula porta felis euismod semper. Nullam id dolor id nibh ultricies vehicula ut id elit.</p>
<p>Cras mattis consectetur purus sit amet fermentum. Nullam quis risus eget urna mollis ornare vel eu leo. Etiam porta sem malesuada magna mollis euismod. Vestibulum id ligula porta felis euismod semper. Praesent commodo cursus magna, vel scelerisque nisl consectetur et.</p>

<h2>Math example</h2>
<p>You know that $math$2+2 = 4$/math$ right?</p>
"""

rendered_view_anothertry = """
<p>This was bad, try again.</p>

<h1>Rant about the amount of required improvements</h1>
<p>Aenean lacinia bibendum nulla sed consectetur. Morbi leo risus, porta ac consectetur ac, vestibulum at eros. Aenean lacinia bibendum nulla sed consectetur. Nullam id dolor id nibh ultricies vehicula ut id elit. Cras justo odio, dapibus ac facilisis in, egestas eget quam.</p>
<p>Maecenas faucibus mollis interdum. Maecenas sed diam eget risus varius blandit sit amet non magna. Integer posuere erat a ante venenatis dapibus posuere velit aliquet. Praesent commodo cursus magna, vel scelerisque nisl consectetur et.</p>
"""

rendered_view_evenanothertry = """
<p>This was even worst.</p>

<p>Read the last feedback and ACTUALLY FOLLOW THE INSTRUCTIONS.</p>
"""


rendered_view_failed = """
<p>This was really bad.</p>

<h1>Rant about how bad it was</h1>
<p>Aenean lacinia bibendum nulla sed consectetur. Morbi leo risus, porta ac consectetur ac, vestibulum at eros. Aenean lacinia bibendum nulla sed consectetur. Nullam id dolor id nibh ultricies vehicula ut id elit. Cras justo odio, dapibus ac facilisis in, egestas eget quam.</p>
<p>Maecenas faucibus mollis interdum. Maecenas sed diam eget risus varius blandit sit amet non magna. Integer posuere erat a ante venenatis dapibus posuere velit aliquet. Praesent commodo cursus magna, vel scelerisque nisl consectetur et.</p>
"""


def days_in_future(days):
    return datetime.now() + timedelta(days=days)

class Command(BaseCommand):
    help = 'Create a database of static data for demo purposes.'
    option_list = BaseCommand.option_list + (
       make_option('--no-groups',
           action='store_true',
           dest='no_groups',
           default=False,
           help='Do not add groups (or deliveries). This really speeds up autodb, and is useful when generating data some other way.'),
   )


    def _createGroup(self, periodpath, assignment, groupname, groupnum, username):
        if self.no_groups:
            return
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

    def _addFirstDeadline(self, group):
        from devilry.apps.core.models import Deadline
        deadline = Deadline(assignment_group=group, deadline=group.parentnode.first_deadline)
        deadline.full_clean()
        deadline.save()

    def _addBadGroups(self, periodpath, assignments, anotherTryVerdict, failedVerdict):
        if self.no_groups:
            return
        for groupnum, names in enumerate(bad_students):
            username, fullname = names
            for assignment in assignments:
                path, group = self._createGroup(periodpath, assignment, 'badgroup', groupnum, username)
                self._addFirstDeadline(group)
                since_pubishingtime = datetime.now() - group.parentnode.publishing_time
                if since_pubishingtime.days >= 8:
                    self.testhelper.add_delivery(path, {'bad.py': ['print ', 'bah']},
                                                 time_of_delivery=-1)
                    self.testhelper.add_delivery(path, {'superbad.py': ['print ', 'superbah']},
                                                 time_of_delivery=1)
                    self.testhelper.add_feedback(path,
                                                 verdict=anotherTryVerdict,
                                                 rendered_view=rendered_view_anothertry)
                    self.testhelper.add_to_path(path + '.d2:ends(14)')
                if since_pubishingtime.days >= 13:
                    self.testhelper.add_delivery(path,
                        {
                            u'stillbad.py': ['print ', 'bah'],
                            u'notes.txt': ['Some notes here.'],
                            u'Noen ganger er det \u00C5lr\u00E6it.txt': ['Testfile for long filename with unicode characters in the filename.']
                        },
                        time_of_delivery=-1)
                    self.testhelper.add_feedback(path, verdict=failedVerdict,
                                                 rendered_view=rendered_view_failed)

    def _addMediumGroups(self, periodpath, assignments, anotherTryVerdict, okVerdict, do_not_finish=[]):
        if self.no_groups:
            return
        for groupnum, names in enumerate(medium_students):
            username, fullname = names
            for assignment in assignments:
                path, group = self._createGroup(periodpath, assignment, 'mediumgroup', groupnum, username)
                self._addFirstDeadline(group)

                since_pubishingtime = datetime.now() - group.parentnode.publishing_time
                if since_pubishingtime.days >= 8:
                    self.testhelper.add_delivery(path, {'bad.py': ['print ', 'bah']},
                                                 time_of_delivery=-1)
                    self.testhelper.add_delivery(path, {'superbad.py': ['print ', 'superbah']},
                                                 time_of_delivery=1)
                    self.testhelper.add_feedback(path,
                                                 verdict=anotherTryVerdict,
                                                 rendered_view=rendered_view_anothertry)
                    self.testhelper.add_to_path(path + '.d2:ends(14)')
                if since_pubishingtime.days >= 15:
                    self.testhelper.add_delivery(path, {'stillbad.py': ['print ', 'bah']}, time_of_delivery=-1)
                    self.testhelper.add_feedback(path,
                                                 verdict=anotherTryVerdict,
                                                 rendered_view=rendered_view_anothertry)
                    self.testhelper.add_to_path(path + '.d3:ends(21)')
                if since_pubishingtime.days >= 22:
                    self.testhelper.add_delivery(path, {'ok.py': ['print ', 'ok']}, time_of_delivery=-1)
                    if assignment in do_not_finish:
                        self.testhelper.add_feedback(path, verdict=okVerdict,
                                                     rendered_view=rendered_view_ok)


    def _addGoodGroups(self, periodpath, assignments, goodVerdict,
            ensure_has_uncorrected_deliveries=True):
        if self.no_groups:
            return
        for groupnum, names in enumerate(good_students):
            username, fullname = names
            for assignment in assignments:
                path, group = self._createGroup(periodpath, assignment, 'goodgroup', groupnum, username)
                self._addFirstDeadline(group)

                since_pubishingtime = datetime.now() - group.parentnode.publishing_time
                if since_pubishingtime.days >= 8:
                    self.testhelper.add_delivery(path, {'good.py': ['print ', 'almostperfect']},
                                                 time_of_delivery=-1)
                    if since_pubishingtime.days < 15 and ensure_has_uncorrected_deliveries:
                        pass
                    else:
                      self.testhelper.add_feedback(path,
                        verdict=goodVerdict, rendered_view=rendered_view_good)


    def _addNonElectronicFeedbacks(self, periodpath, assignments, students, group_prefix, feedbacks):
        if self.no_groups:
            return
        for groupnum, names in enumerate(students):
            username, fullname = names
            for assignmentnum, assignment in enumerate(assignments):
                path, group = self._createGroup(periodpath, assignment, group_prefix, groupnum, username)
                if assignmentnum < 1:
                    for offset, verdict, rendered_view in feedbacks:
                        delivery = self.testhelper.add_delivery(path, {}, time_of_delivery=offset)
                        self.testhelper.add_feedback(delivery,
                            verdict=verdict,
                            rendered_view=rendered_view)


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

    def _create_numbered_students(self, count):
        usernames = ['student{}'.format(i) for i in xrange(count)]
        usernamesAndFullnames = [(username, username.capitalize()) for username in usernames]
        self.create_users(usernamesAndFullnames)
        return usernames

    def _set_first_deadlines(self, period, days_after_pubtime=2):
        for assignment in period.assignments.all():
            logging.info('Setting first_deadline on %s', assignment)
            assignment.first_deadline = assignment.publishing_time + timedelta(days=days_after_pubtime)
            assignment.first_deadline = assignment.first_deadline.replace(hour=15, minute=0, second=0)
            assignment.save()

    def create_duck1100(self):
        """
        Weekly assignments with points.

        Thor is admin on the ``springcur`` period.
        """
        assignments = ['week{0}:pub({1})'.format(weeknum, weeknum*7) for weeknum in xrange(1, 10)]
        periods = ['springcur:begins(-2):ends(6):ln(Spring Current)',
                   'springold:begins(-14):ends(6):ln(Spring Old)',
                   'springveryold:begins(-24):ends(6):ln(Spring VeryOld)']
        self.testhelper.add(nodes="duckburgh:admin(duckburghadmin).ifi:admin(ifiadmin)",
                            subjects=["duck1100:ln(DUCK1100 - Getting started with python)"],
                            periods=periods,
                            assignments=assignments)
        self.testhelper.duck1100_springcur.admins.add(self.testhelper.thor)
        anotherTryVerdict = {'grade': '5/20', 'points': 5, 'is_passing_grade': False}
        failedVerdict = {'grade': '2/20', 'points': 2, 'is_passing_grade': False}
        okVerdict = {'grade': '12/20', 'points': 12, 'is_passing_grade': True}
        goodVerdict = {'grade': '18/20', 'points': 18, 'is_passing_grade': True}

        assignmentnames = self._onlyNames(assignments)
        periodnames = self._onlyNames(periods)
        for periodname in periodnames:
            periodpath = 'duckburgh.ifi;duck1100.' + periodname
            logging.info('Creating %s', periodpath)
            period = self.testhelper.get_object_from_path(periodpath)
            self._set_first_deadlines(period, days_after_pubtime=7)
            self._addRelatedStudents(period)
            self._addRelatedExaminers(period)
            self._addBadGroups(periodpath, assignmentnames, anotherTryVerdict, failedVerdict)
            self._addMediumGroups(periodpath, assignmentnames, anotherTryVerdict, okVerdict,
                                  do_not_finish=['week4', 'week5'])
            self._addGoodGroups(periodpath, assignmentnames, goodVerdict)

    def create_duck1010(self):
        """
        3 obligatory assignments with approved/not approved.

        Thor is admin on the subject.
        """
        assignments = ['oblig{num}:pub({pub}):ln(Obligatorisk oppgave {num})'.format(num=num, pub=num*40) for num in xrange(1, 4)]
        periods = ['springcur:begins(-2):ends(6):ln(Spring Current)',
                   'springold:begins(-14):ends(6):ln(Spring Old)']
        self.testhelper.add(nodes="duckburgh:admin(duckburghadmin).ifi:admin(ifiadmin)",
                            subjects=["duck1010:ln(DUCK1010 - Objektorientert programmering)"],
                            periods=periods,
                            assignments=assignments)
        self.testhelper.duck1010.admins.add(self.testhelper.thor)

        for year in range(2000, 2011): # Add some extra old semesters just to make it easier to test layouts with many semesters
            logging.info('Creating duck1010 spring%s', year)
            self.testhelper.duck1010.periods.create(
                short_name='spring{0}'.format(year),
                long_name='Spring {0}'.format(year),
                start_time=datetime(year, 8, 1),
                end_time=datetime(year, 12, 30)
            )

        anotherTryVerdict = {'grade': 'Not approved', 'points': 0, 'is_passing_grade': False}
        failedVerdict = {'grade': 'Not approved', 'points': 0, 'is_passing_grade': False}
        okVerdict = {'grade': 'Approved', 'points': 1, 'is_passing_grade': True}
        goodVerdict = {'grade': 'Approved', 'points': 1, 'is_passing_grade': True}

        assignmentnames = [name.split(':')[0] for name in assignments]
        periodnames = self._onlyNames(periods)
        # extra_numbered_students = self._create_numbered_students(2000)
        for periodname in periodnames[:1]:
            periodpath = 'duckburgh.ifi;duck1010.' + periodname
            logging.info('Creating %s', periodpath)
            period = self.testhelper.get_object_from_path(periodpath)
            self._set_first_deadlines(period)
            self._addRelatedStudents(period)
            # self._addRelatedStudentsFromList(period, extra_numbered_students)
            self._addRelatedExaminers(period)
            self._addBadGroups(periodpath, assignmentnames, anotherTryVerdict, failedVerdict)
            self._addMediumGroups(periodpath, assignmentnames, anotherTryVerdict, okVerdict)
            self._addGoodGroups(periodpath, assignmentnames, goodVerdict)


    def create_duck6000(self):
        """
        Created with a single period, and no assignments, where thor is admin.
        """
        periods = ['springcur:begins(-2):ends(6):ln(Spring Cur)']
        self.testhelper.add(nodes="duckburgh:admin(duckburghadmin).ifi:admin(ifiadmin)",
                            subjects=["duck6000:ln(DUCK6000 - Make robots dance)"],
                            periods=periods)
        self.testhelper.duck6000_springcur.admins.add(self.testhelper.thor)
        periodnames = self._onlyNames(periods)
        for periodname in periodnames:
            periodpath = 'duckburgh.ifi;duck6000.' + periodname
            logging.info('Creating %s', periodpath)
            period = self.testhelper.get_object_from_path(periodpath)
            self._set_first_deadlines(period)
            self._addRelatedStudents(period)
            self._addRelatedExaminers(period)

    def create_duck4000(self):
        """
        Created with a single period and a single assignment, where thor is admin.
        """
        assignments = ['oblig1:pub(40):ln(Obligatorisk oppgave 1)']
        periods = ['springcur:begins(-2):ends(6):ln(Spring Cur)']
        self.testhelper.add(nodes="duckburgh:admin(duckburghadmin).ifi:admin(ifiadmin)",
                            subjects=["duck4000:ln(DUCK4000 - Make robots walk)"],
                            periods=periods,
                            assignments=assignments)
        self.testhelper.duck4000_springcur_oblig1.admins.add(self.testhelper.thor)
        periodnames = self._onlyNames(periods)
        for periodname in periodnames:
            periodpath = 'duckburgh.ifi;duck4000.' + periodname
            logging.info('Creating %s', periodpath)
            period = self.testhelper.get_object_from_path(periodpath)
            self._set_first_deadlines(period)
            self._addRelatedStudents(period)
            self._addRelatedExaminers(period)

    def create_duck2500p(self):
        """
        Created with paper assignments where thor is admin.
        """
        from devilry.apps.core.models.deliverytypes import NON_ELECTRONIC
        assignments = ['paper{num}:pub({pub}):ln(Paper delivery {num})'.format(num=num, pub=num*40) for num in xrange(1, 4)]
        periods = ['springcur:begins(-2):ends(6):ln(Spring Current)',
                   'springold:begins(-14):ends(6):ln(Spring Old)']
        self.testhelper.add(nodes="duckburgh:admin(duckburghadmin).ifi:admin(ifiadmin)",
            subjects=["duck2500p:ln(DUCK2500p - Objektorientert programmering)"],
            periods=periods,
            assignments=assignments)
        self.testhelper.duck2500p.admins.add(self.testhelper.thor)

        anotherTryVerdict = {'grade': 'Not approved', 'points': 0, 'is_passing_grade': False}
        failedVerdict = {'grade': 'Not approved', 'points': 0, 'is_passing_grade': False}
        okVerdict = {'grade': 'Approved', 'points': 1, 'is_passing_grade': True}
        goodVerdict = {'grade': 'Approved', 'points': 1, 'is_passing_grade': True}

        assignmentnames = [name.split(':')[0] for name in assignments]
        periodnames = self._onlyNames(periods)
        for periodname in periodnames:
            periodpath = 'duckburgh.ifi;duck2500p.' + periodname
            logging.info('Creating %s', periodpath)
            period = self.testhelper.get_object_from_path(periodpath)
            for assignment in period.assignments.all():
                assignment.delivery_types = NON_ELECTRONIC
                assignment.save()
            self._addRelatedStudents(period)
            self._addRelatedExaminers(period)
            self._addNonElectronicFeedbacks(periodpath, assignmentnames, bad_students, 'badgroup', [
                (7, anotherTryVerdict, rendered_view_anothertry),
                (13, anotherTryVerdict, rendered_view_evenanothertry),
                (19, failedVerdict, rendered_view_failed),
            ])
            self._addNonElectronicFeedbacks(periodpath, assignmentnames, medium_students, 'mediumgroup', [
                (7, anotherTryVerdict, rendered_view_anothertry),
                (13, okVerdict, rendered_view_ok),
            ])
            self._addNonElectronicFeedbacks(periodpath, assignmentnames, good_students, 'goodgroup', [
                (7, goodVerdict, rendered_view_good),
            ])

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
                if examiner == 'scrooge':
                    return examiner + ',' + 'thor' # Make thor examiner on all of the same groups as scrooge
                else:
                    return examiner
        return None
        #raise LookupError('No examiner defined for {0}'.format(username))

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

    def _unset_groupnames(self):
        from devilry.apps.core.models import AssignmentGroup
        for group in AssignmentGroup.objects.all():
            group.name = None
            group.save()

    def handle(self, *args, **options):
        from devilry.apps.core.testhelper import TestHelper
        verbosity = get_verbosity(options)
        self.no_groups = options['no_groups']
        setup_logging(verbosity)

        # NOTE: Not running flush - it messes up migrations
        #logging.info('Running manage.py flush')
        #management.call_command('flush', verbosity=0, interactive=False)

        self.testhelper = TestHelper()
#        from django.db import transaction
#        with transaction.commit_on_success():
        self.testhelper.create_superuser('grandma')
        self.testhelper.grandma.is_staff = True
        self.testhelper.grandma.save()
        logging.info('Creating users')
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
        logging.info('Generating data (nodes, periods, subjects, deliveries...). Run with -v3 for more details.')
        self.create_duck1010()
        self.create_duck2500p()
        self.create_duck4000()
        self.create_duck6000()
        self.create_duck1100()
        self._unset_groupnames()
