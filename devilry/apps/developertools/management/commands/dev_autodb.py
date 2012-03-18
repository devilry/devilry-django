import logging
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



class Command(BaseCommand):
    help = 'Create a database of static data for demo purposes.'

    def create_duck1100(self):
        assignments = ['week1', 'week2', 'week3', 'week4', 'week5', 'week6']
        self.testhelper.add(nodes="duckburgh:admin(duckburghadmin).ifi:admin(ifiadmin)",
                            subjects=["duck1100:ln(DUCK1100 - Getting started with python)"],
                            periods=["year20xx:begins(-4):ends(6)"],
                            assignments=assignments)

        anotherTryVerdict = {'grade': '5/20', 'points': 5, 'is_passing_grade': False}
        failedVerdict = {'grade': '2/20', 'points': 2, 'is_passing_grade': False}
        for groupnum, names in enumerate(bad_students):
            username, fullname = names
            for assignment in assignments:
                path = 'duckburgh.ifi;duck1100.year20xx.{assignment}.badgroup{groupnum}'.format(**vars())
                extras = ':candidate({username}):examiner(donald)'.format(**vars())
                to_be_added = path + extras
                self.testhelper.add_to_path(to_be_added)
                logger.debug('Created ' + to_be_added)
                self.testhelper.add_to_path(path + '.d1:ends(10)')
                self.testhelper.add_delivery(path, {'bad.py': ['print ', 'bah']})
                self.testhelper.add_delivery(path, {'superbad.py': ['print ', 'superbah']},
                                             after_last_deadline=True)
                self.testhelper.add_feedback(path, verdict=anotherTryVerdict)
                self.testhelper.add_to_path(path + '.d2:ends(20)')
                self.testhelper.add_delivery(path, {'stillbad.py': ['print ', 'bah']})
                self.testhelper.add_feedback(path, verdict=failedVerdict)
                group = self.testhelper.get_object_from_path(path)
                group.is_open = False
                group.save()

    #def create_duck1010(self):
        #self.testhelper.add(nodes="duckburgh:admin(duckburghadmin).ifi:admin(ifiadmin)",
                 #subjects=["duck1010"],
                 #periods=["old:begins(-2):ends(1)", "looong"],
                 #assignments=["assignment1", "assignment2"],
                 #assignmentgroups=["g1:candidate(student1):examiner(examiner1)",
                                   #"g2:examiner(examiner2)",
                                   #"g3:candidate(student2,student3):examiner(examiner1,examiner2)"])

    def create_users(self, list_of_users):
        for username, fullname in list_of_users:
            self.testhelper.create_user(username, fullname)


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
        self.create_duck1100()
        #self.create_duck1010()
