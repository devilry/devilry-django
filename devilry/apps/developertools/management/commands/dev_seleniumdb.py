from django.core.management.base import BaseCommand
from django.core import management
from devilry.apps.core.testhelper import TestHelper


class Command(BaseCommand):
    help = 'Create a databse of static data for the selenium tests.'

    def handle(self, *args, **options):
        management.call_command('flush', verbosity=0, interactive=False)
        management.call_command('loaddata', 'dev_grandma', verbosity=0, interactive=False)
        #management.call_command('loaddata', 'dev_duckburghusers', verbosity=0, interactive=False)

        testhelper = TestHelper()
        testhelper.add(nodes="uio:admin(uioadmin).ifi:admin(ifiadmin)",
                 subjects=["inf1100"],
                 periods=["old:begins(-2):ends(1)", "looong"],
                 assignments=["assignment1", "assignment2"],
                 assignmentgroups=["g1:candidate(student1):examiner(examiner1)", "g2:examiner(examiner2)",
                                   "g3:candidate(student2,student3):examiner(examiner1,examiner2)"])
        testhelper.add_to_path('uio.ifi;inf1100.looong.assignment3.group1:examiner(examiner1)')
        testhelper.add_to_path('uio.ifi;inf1100.old.oldassignment.group1:examiner(examiner3)')
