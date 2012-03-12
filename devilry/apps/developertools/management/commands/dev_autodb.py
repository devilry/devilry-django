from django.core.management.base import BaseCommand
from django.core import management
from devilry.apps.core.testhelper import TestHelper


class Command(BaseCommand):
    help = 'Create a databse of static data for the selenium tests.'


    def create_duck1100(self):
        self.testhelper.add(nodes="duckburgh:admin(duckburghadmin).ifi:admin(ifiadmin)",
                 subjects=["duck1100"],
                 periods=["old:begins(-2):ends(1)", "looong"],
                 assignments=["assignment1", "assignment2"],
                 assignmentgroups=["g1:candidate(student1):examiner(examiner1)",
                                   "g2:examiner(examiner2)",
                                   "g3:candidate(student2,student3):examiner(examiner1,examiner2)"])
        self.testhelper.set_attributes_from_path('duck1100',
                                                 long_name='DUCK1100 - Getting started with python')

    def create_duck1010(self):
        self.testhelper.add(nodes="duckburgh:admin(duckburghadmin).ifi:admin(ifiadmin)",
                 subjects=["duck1010"],
                 periods=["old:begins(-2):ends(1)", "looong"],
                 assignments=["assignment1", "assignment2"],
                 assignmentgroups=["g1:candidate(student1):examiner(examiner1)",
                                   "g2:examiner(examiner2)",
                                   "g3:candidate(student2,student3):examiner(examiner1,examiner2)"])


    def handle(self, *args, **options):
        management.call_command('flush', verbosity=0, interactive=False)
        management.call_command('loaddata', 'dev_grandma', verbosity=0, interactive=False)
        #management.call_command('loaddata', 'dev_duckburghusers', verbosity=0, interactive=False)

        self.testhelper = TestHelper()
        self.create_duck1100()
        self.create_duck1010()
