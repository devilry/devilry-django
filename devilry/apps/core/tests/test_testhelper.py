from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from ..models import Node, Subject, Period, Assignment, AssignmentGroup, Deadline, Delivery, StaticFeedback
from ..testhelper import TestHelper

from datetime import datetime, timedelta


class TestTestHelper(TestCase):

    def setUp(self):
        self.ti = TestHelper()

    def test_nodes(self):
        self.ti.add(nodes='uio.ifi')
        self.assertEquals(Node.objects.all().count(), 2)

        # check relations between them
        self.assertEquals(self.ti.uio.parentnode, None)
        self.assertEquals(self.ti.uio_ifi.parentnode, self.ti.uio)
        self.assertTrue(self.ti.uio_ifi in self.ti.uio.child_nodes.all())

    def test_many_root_nodes(self):
        self.ti.add(nodes='uio.ifi')
        self.assertEquals(Node.objects.all().count(), 2)

        # check relations between them
        self.assertEquals(self.ti.uio.parentnode, None)
        self.assertEquals(self.ti.uio_ifi.parentnode, self.ti.uio)
        self.assertTrue(self.ti.uio_ifi in self.ti.uio.child_nodes.all())

    def test_single_nodes(self):
        self.ti.add(nodes='uio')
        self.ti.add(nodes='ifi')

        self.assertEquals(Node.objects.all().count(), 2)
        # uio = Node.objects.get(short_name='uio')
        # ifi = Node.objects.get(short_name='ifi')

        # check relations between them
        self.assertEquals(self.ti.uio.parentnode, None)
        self.assertEquals(self.ti.ifi.parentnode, None)
        self.assertTrue(self.ti.ifi not in self.ti.uio.child_nodes.all())

    def test_nodes_and_admins(self):
        self.ti.add(nodes='uio:admin(rektor).ifi:admin(mortend)')

        # Assert that all nodes and admins are created
        self.assertEquals(Node.objects.filter(short_name='uio').count(), 1)
        self.assertEquals(Node.objects.filter(short_name='ifi').count(), 1)
        self.assertEquals(User.objects.filter(username='rektor').count(), 1)
        self.assertEquals(User.objects.filter(username='mortend').count(), 1)

        # assert that they are both admins
        self.assertTrue(self.ti.rektor in self.ti.uio.admins.all())
        self.assertTrue(self.ti.mortend in self.ti.uio_ifi.admins.all())

        # assert that uio has ifi as a child node and ifi has uio as parent
        self.assertTrue(self.ti.uio_ifi in self.ti.uio.child_nodes.all())
        self.assertEquals(self.ti.uio_ifi.parentnode, self.ti.uio)
        self.assertEquals(self.ti.uio.parentnode, None)

    def test_nodes_and_one_admin(self):
        self.ti.add(nodes='uio.ifi:admin(mortend)')

        self.assertEquals(Node.objects.filter(short_name='uio').count(), 1)
        self.assertEquals(Node.objects.filter(short_name='ifi').count(), 1)

        # mortend = User.objects.get(username='mortend')
        # ifi = Node.objects.get(short_name='ifi')
        self.assertTrue(self.ti.mortend in self.ti.uio_ifi.admins.all())

    def test_subject(self):
        self.ti.add(nodes='ifi:admin(mortend)',
                    subjects=['inf1000', 'inf1010'])

        # assert that the subjects are there
        self.assertEquals(Subject.objects.filter(short_name='inf1000').count(), 1)
        self.assertEquals(Subject.objects.filter(short_name='inf1010').count(), 1)

        # assert that the parentnode is ifi
        self.assertEquals(self.ti.ifi, self.ti.inf1000.parentnode)
        self.assertEquals(self.ti.ifi, self.ti.inf1010.parentnode)

    def test_subject_with_admins(self):
        self.ti.add(nodes='uio:admin(rektor).ifi:admin(mortend)',
                    subjects=['inf1000:admin(arnem)', 'inf1010:admin(steinm,steingj)'])

        # assert that the subject admin users where created
        self.assertEquals(User.objects.filter(username='arnem').count(), 1)
        self.assertEquals(User.objects.filter(username='steinm').count(), 1)
        self.assertEquals(User.objects.filter(username='steingj').count(), 1)

        # inf1000 = Subject.objects.get(short_name='inf1000')
        # inf1010 = Subject.objects.get(short_name='inf1010')

        # arnem = User.objects.get(username='arnem')
        # steinm = User.objects.get(username='steinm')
        # steingj = User.objects.get(username='steingj')

        # assert that they are all admins in their subjects
        self.assertTrue(self.ti.arnem in self.ti.inf1000.admins.all())
        self.assertTrue(self.ti.steinm in self.ti.inf1010.admins.all())
        self.assertTrue(self.ti.steingj in self.ti.inf1010.admins.all())

    def test_period(self):
        self.ti.add(nodes='ifi:admin(mortend)',
                    subjects=['inf1000', 'inf1010'],
                    periods=['fall01', 'spring01'])

        # assert that the periods are there. There should be 2 of
        # each, since there are (should!) 2 subjects.
        self.assertEquals(Period.objects.filter(short_name='spring01').count(), 2)
        self.assertEquals(Period.objects.filter(short_name='fall01').count(), 2)

        # assert that the parentnodes are correct
        self.assertEquals(self.ti.inf1010_fall01.parentnode, self.ti.inf1010)
        self.assertEquals(self.ti.inf1010_spring01.parentnode, self.ti.inf1010)

    def test_period_with_admins(self):
        self.ti.add(nodes='uio:admin(rektor).ifi:admin(mortend)',
                    subjects=['inf1000', 'inf1010'],
                    periods=['fall01:admin(steingj)', 'spring01:admin(steinm)'])

        # assert that the users are created
        self.assertEquals(User.objects.filter(username='steingj').count(), 1)
        self.assertEquals(User.objects.filter(username='steinm').count(), 1)

        # assert that they are admins for the periods
        self.assertTrue(self.ti.steingj in self.ti.inf1000_fall01.admins.all())
        self.assertTrue(self.ti.steinm in self.ti.inf1000_spring01.admins.all())

    def test_assignment(self):
        self.ti.add(nodes='ifi:admin(mortend)',
                    subjects=['inf1000', 'inf1010'],
                    periods=['fall01', 'spring01'],
                    assignments=['oblig1', 'oblig2'])

        # assert that the assignments are there. There should be 4 of
        # each, since there are (should!) 2 periods.
        self.assertEquals(Assignment.objects.filter(short_name='oblig1').count(), 4)
        self.assertEquals(Assignment.objects.filter(short_name='oblig2').count(), 4)

        # assert that the parentnodes are correct
        self.assertEquals(self.ti.inf1010_fall01.parentnode, self.ti.inf1010)
        self.assertEquals(self.ti.inf1010_spring01.parentnode, self.ti.inf1010)

    def test_assignment_with_admin(self):
        self.ti.add(nodes='ifi',
                    subjects=['inf1000:admin(arnem)'],
                    periods=['fall01'],
                    assignments=['oblig1:admin(jose)', 'oblig2:admin(jose)'])

        # Assert that the admins are created
        self.assertEquals(User.objects.filter(username='arnem').count(), 1)
        self.assertEquals(User.objects.filter(username='jose').count(), 1)

        # check that jose is an admin for the assignment
        self.assertTrue(self.ti.jose in self.ti.inf1000_fall01_oblig1.admins.all())
        self.assertTrue(self.ti.jose in self.ti.inf1000_fall01_oblig2.admins.all())

        # check that arnem also has admin rights in the assignments
        self.assertTrue(self.ti.inf1000_fall01_oblig1 in Assignment.where_is_admin(self.ti.arnem).all())
        self.assertTrue(self.ti.inf1000_fall01_oblig2 in Assignment.where_is_admin(self.ti.arnem).all())

    def test_assignmentgroups(self):
        self.ti.add(nodes="ifi",
                    subjects=["inf1000", "inf1100"],
                    periods=["fall01", "spring01"],
                    assignments=["oblig1", "oblig2"],
                    assignmentgroups=['g1:candidate(zakia):examiner(cotryti)',
                                      'g2:candidate(nataliib):examiner(jose)'])

        # assert that the assignmentgroups are there. There should be 8 of
        # each, since there are (should!) 2 assignments.
        self.assertEquals(AssignmentGroup.objects.filter(name='g1').count(), 8)
        self.assertEquals(AssignmentGroup.objects.filter(name='g2').count(), 8)

        # assert that the parentnodes are correct
        self.assertEquals(self.ti.inf1100_fall01_oblig1_g1.parentnode, self.ti.inf1100_fall01_oblig1)
        self.assertEquals(self.ti.inf1100_spring01_oblig1_g2.parentnode, self.ti.inf1100_spring01_oblig1)

        # assert that the candidates are candidates in the assignment
        self.assertTrue(self.ti.inf1100_fall01_oblig1 in Assignment.where_is_candidate(self.ti.zakia))
        self.assertTrue(self.ti.inf1100_fall01_oblig1 in Assignment.where_is_candidate(self.ti.nataliib))

        # assert that the examiners are examiners in the assignment
        self.assertTrue(self.ti.inf1100_fall01_oblig1_g1 in AssignmentGroup.where_is_examiner(self.ti.cotryti))
        self.assertTrue(self.ti.inf1100_fall01_oblig1_g2 in AssignmentGroup.where_is_examiner(self.ti.jose))

    def test_updating_paths(self):
        self.ti.add(nodes='uio.ifi',
                    subjects=['inf1000'],
                    periods=['fall01', 'spring01'],
                    assignments=['oblig1'])

        self.ti.add(nodes='uio.ifi',
                    subjects=['inf1000', 'inf1010'],
                    periods=['spring01'],
                    assignments=['oblig2'])

        # assert that spring01 has oblig2
        self.assertEquals(self.ti.inf1000_spring01.assignments.filter(short_name='oblig2').count(), 1)
        # assert that fall01 doesn't have oblig2
        self.assertEquals(self.ti.inf1000_fall01.assignments.filter(short_name='oblig2').count(), 0)
        # assert that uio doesn't have any subjects and stuff
        self.assertEquals(self.ti.uio.subjects.all().count(), 0)

        self.ti.add(nodes='uio.ifi', subjects=['inf2220'], periods=['fall01', 'spring01'], assignments=['oblig1', 'oblig2'])

        # assert that inf2220 has 2 assignments
        self.assertEquals(self.ti.inf2220_fall01.assignments.all().count(), 2)
        # and that inf1010 is the same as before
        self.assertEquals(self.ti.inf1000_spring01.assignments.filter(short_name='oblig2').count(), 1)
        self.assertEquals(self.ti.inf1000_fall01.assignments.filter(short_name='oblig2').count(), 0)

    def test_deadlines(self):
        self.ti.add(nodes="uio.ifi",
                    subjects=["inf1000", "inf1100"],
                    periods=["fall01", "spring01"],
                    assignments=["oblig1", "oblig2"],
                    assignmentgroups=['g1:candidate(zakia):examiner(cotryti)',
                                      'g2:candidate(nataliib):examiner(jose)'],
                    deadlines=[])

    def test_period_times(self):

        self.ti.add(nodes='uio.ifi',
                    subjects=['inf1000'],
                    periods=['first:begins(0)', 'second:begins(6):ends(1)'],
                    assignments=['oblig1', 'oblig2'])

        today = datetime.today().date()
        sixIshMonthsFromToday = (datetime.today() + timedelta(days=6 * 30)).date()

        # assert that first period starts today
        self.assertEquals(self.ti.inf1000_first.start_time.date(), today)

        # assert that the second semester begins in about 6 months
        # and that it ends about 1 month from then
        self.assertEquals(self.ti.inf1000_second.start_time.date(), sixIshMonthsFromToday)
        self.assertEquals(self.ti.inf1000_second.end_time.date(), sixIshMonthsFromToday + timedelta(days=30))

        # assert that first is active, while the second isnt
        self.assertTrue(self.ti.inf1000_first.is_active())
        self.assertFalse(self.ti.inf1000_second.is_active())

        # add an old period
        self.ti.add(nodes='uio.ifi', subjects=['inf1000'], periods=['old:begins(-2):ends(1)'])

        # assert that old began 2 months ago, and that it ended 1 month ago.
        self.assertEquals(self.ti.inf1000_old.start_time.date(), today + timedelta(days=-60))
        # And that it isnt active
        self.assertEquals(self.ti.inf1000_old.end_time.date(), today + timedelta(days=-30))
        self.assertFalse(self.ti.inf1000_old.is_active())

    def test_assignments_times(self):
        self.ti.add(nodes='uio.ifi',
                    subjects=['inf1000'],
                    periods=['first:begins(0)', 'second:begins(6):ends(1)'],
                    assignments=['oblig1', 'oblig2:pub(10)', 'oblig3:pub(20)'])

        today = datetime.today().date()
        self.assertEquals(self.ti.inf1000_first_oblig1.publishing_time.date(), today)
        self.assertEquals(self.ti.inf1000_first_oblig2.publishing_time.date(), today + timedelta(days=10))
        self.assertEquals(self.ti.inf1000_first_oblig3.publishing_time.date(), today + timedelta(days=20))

    def test_add_as_path(self):
        self.ti.add_to_path('uio:admin(rektor).ifi:admin(mortend);inf1000:admin(stein,steing).fall01')

        # assert that all the expected nodes are created
        self.assertTrue(self.ti.rektor in self.ti.uio.admins.all())
        self.assertTrue(self.ti.mortend in self.ti.uio_ifi.admins.all())
        self.assertTrue(self.ti.stein in self.ti.inf1000.admins.all())
        self.assertTrue(self.ti.steing in self.ti.inf1000.admins.all())
        self.assertEquals(self.ti.uio, Node.objects.get(short_name='uio'))
        self.assertEquals(self.ti.uio_ifi, Node.objects.get(short_name='ifi'))
        self.assertEquals(self.ti.inf1000, Subject.objects.get(short_name='inf1000'))
        self.assertEquals(self.ti.inf1000_fall01, Period.objects.get(short_name='fall01'))

    def test_deadliness(self):
        self.ti.add(nodes='uio.ifi',
                    subjects=['inf1000'],
                    periods=['first:begins(0)', 'second:begins(6):ends(1)'],
                    assignments=['oblig1', 'oblig2:pub(10)'],
                    assignmentgroups=['g1:candidate(zakia):examiner(cotryti)',
                                      'g2:candidate(nataliib):examiner(jose)'],
                    deadlines=['d1:ends(10):text(First deadline)'])

        today = datetime.today().date()

        # assert that the deadlines are created correctly
        self.assertEquals(self.ti.inf1000_first_oblig1_g1_d1.deadline.date(), today + timedelta(days=10))
        self.assertEquals(self.ti.inf1000_first_oblig1_g1_d1.text, 'First deadline')

        # and that there as many deadlines as there are groups. There
        # should be 8 assignment groups created by having 1 subject, 2
        # periods, 2 assignments and 2 groups in each, and we create 8
        # more deadlines that end in 10 days
        self.assertEquals(Deadline.objects.all().count(), 8)

        # add a new deadline for g1. This should overwrite the
        # previous d1 deadline
        self.ti.add_to_path('uio.ifi;inf1000.first.oblig1.g1.d1:ends(20):text(Third deadline)')
        # assert that the texts are set correctly
        self.assertEquals(self.ti.inf1000_first_oblig1_g1_d1.text, 'Third deadline')
        self.assertEquals(Deadline.objects.all().count(), 9)

        # check the deadlines list of g1
        self.assertEquals(len(self.ti.inf1000_first_oblig1_g1_deadlines), 2)
        # and that the last element in that list is the same as d1
        self.assertEquals(self.ti.inf1000_first_oblig1_g1_d1, self.ti.inf1000_first_oblig1_g1_deadlines[-1])

    def test_get_object_from_path(self):

        self.ti.add(nodes='uio.ifi',
                    subjects=['inf1000'],
                    periods=['first:begins(0)', 'second:begins(6):ends(1)'],
                    assignments=['oblig1', 'oblig2:pub(10)'],
                    assignmentgroups=['g1:candidate(zakia):examiner(cotryti)',
                                      'g2:candidate(nataliib):examiner(jose)'],
                    deadlines=['d1:ends(10):text(First deadline)'])

        # assert that you get the correct type from different paths
        self.assertEquals(type(self.ti.get_object_from_path('uio.ifi;inf1000')), Subject)
        self.assertEquals(type(self.ti.get_object_from_path('uio.ifi;inf1000.first')), Period)
        self.assertEquals(type(self.ti.get_object_from_path('uio.ifi;inf1000.second')), Period)
        self.assertEquals(type(self.ti.get_object_from_path('uio.ifi;inf1000.first.oblig1')), Assignment)
        self.assertEquals(type(self.ti.get_object_from_path('uio.ifi;inf1000.first.oblig1.g1')), AssignmentGroup)

        # assert that excluding the top nodes still gives the correct
        # type. This should be possible because subjects are unique
        self.assertEquals(type(self.ti.get_object_from_path('inf1000')), Subject)
        self.assertEquals(type(self.ti.get_object_from_path('inf1000.first')), Period)

        # assert that wrong paths gives a keyerror
        with self.assertRaises(KeyError):
            self.ti.get_object_from_path('lskdfj;lskjdf.lksjdf')

    def test_deliveries(self):
        self.ti.add(nodes='uio.ifi',
                    subjects=['inf1000'],
                    periods=['first:begins(0)', 'second:begins(6):ends(1)'],
                    assignments=['oblig1', 'oblig2:pub(10)'],
                    assignmentgroups=['g1:candidate(zakia):examiner(cotryti)',
                                      'g2:candidate(nataliib):examiner(jose)'],
                    deadlines=['d1:ends(10):text(First deadline)'])

        file1 = {'test.py': ['print', 'hello world']}
        file2 = {'test2.py': ['print "hi"']}
        files = {'test.py': ['print', 'hello world'],
                 'test2.py': ['print "hi"'] }

        # deliver with path
        d1 = self.ti.add_delivery('inf1000.first.oblig1.g1', file1)
        d2 = self.ti.add_delivery('inf1000.first.oblig1.g2', file2)
        d3 = self.ti.add_delivery('inf1000.first.oblig2.g1', files)

        # assert that the deliveries are deliveries are correct
        self.assertEquals(Delivery.objects.all().count(), 3)
        self.assertEquals(d1.time_of_delivery.date(), datetime.today().date())
        self.assertEquals(d1.number, 1)
        self.assertEquals(d1.delivered_by, self.ti.inf1000_first_oblig1_g1.candidates.all()[0])
        self.assertFalse(d1.after_deadline)

        self.assertEquals(d2.filemetas.all().count(), 1)
        self.assertEquals(d3.filemetas.all().count(), 2)

        # test the variable creation by testinitializer
        self.assertEquals(self.ti.inf1000_first_oblig1_g1_deliveries[0], d1)
        with self.assertRaises(IndexError):
            self.ti.inf1000_first_oblig1_g1_deliveries[1]
        # add a delivery to g1, and check that there are now 2
        # deliveries in the list
        d4 = self.ti.add_delivery('inf1000.first.oblig1.g1', file1)
        self.assertEquals(self.ti.inf1000_first_oblig1_g1_deliveries[1], d4)

        # add a late delivery
        d5 = self.ti.add_delivery(self.ti.inf1000_second_oblig1_g2, files=file2, after_last_deadline=True)
        # and assert that it's really delivered after the deadline
        self.assertGreater(d5.time_of_delivery.date(), d5.deadline.deadline.date())   # self.ti.inf1000_second_oblig1.publishing_time)
        self.assertTrue(d5.after_deadline)

    def test_feedback(self):
        self.ti.add(nodes='uio.ifi',
                    subjects=['inf1000'],
                    periods=['first:begins(0)', 'second:begins(6):ends(1)'],
                    assignments=['oblig1', 'oblig2:pub(10)'],
                    assignmentgroups=['g1:candidate(zakia):examiner(cotryti)',
                                      'g2:candidate(nataliib):examiner(jose)'],
                    deadlines=['d1:ends(10):text(First deadline)'])

        file1 = {'test.py': ['print', 'hello world']}
        file2 = {'test2.py': ['print "hi"']}

        # deliver with path
        d1 = self.ti.add_delivery('inf1000.first.oblig1.g1', file1)
        # test a feedback with default values
        fb1 = self.ti.add_feedback(d1)

        # assert that a feedback exists in core, and that its the same
        # we just created
        self.assertEquals(StaticFeedback.objects.all().count(), 1)
        self.assertEquals(fb1, StaticFeedback.objects.all()[0])

        # check its values
        self.assertEquals(fb1.grade, 'A')
        self.assertEquals(fb1.points, 100)
        self.assertTrue(fb1.is_passing_grade)
        self.assertEquals(fb1.saved_by, self.ti.cotryti)

        # try again, but with parameters
        self.ti.add_delivery('inf1000.first.oblig1.g2', file2)
        verdict = {'grade': 'B', 'points': 85, 'is_passing_grade': True}
        fb2 = self.ti.add_feedback('inf1000.first.oblig1.g2', verdict=verdict, examiner=self.ti.jose)

        # check its values
        self.assertEquals(fb2.grade, 'B')
        self.assertEquals(fb2.points, 85)
        self.assertTrue(fb2.is_passing_grade)
        self.assertEquals(fb2.saved_by, self.ti.jose)

        # Try making a feedback with a certain timestamp
        fb3 = self.ti.add_feedback(d1, timestamp=datetime.now())
        self.assertEquals(fb3.save_timestamp.date(), datetime.now().date())

        # try to make an illegal feedback. jose can't grade
        # zakias deliveries
        # with self.assertRaises(Exception):
        #     self.ti.add_feedback(d1, examiner=self.ti.jose)
        # # zakia certainly can't grade his own delivery
        # with self.assertRaises(Exception):
        #     self.ti.add_feedback(d1, examiner=self.ti.zakia)

    def test_invalid_parameters(self):
        with self.assertRaises(ValueError):
            self.ti.add(nodes='uio', periods='fall01')

        with self.assertRaises(ValueError):
            self.ti.add(nodes='uio', subjects='inf101', assignments='oblig1')

            #self.ti.add(nodes='uio', subjects='inf101', assignments='oblig1')

    def test_refresh_var(self):
        self.ti.add(nodes='uio.ifi',
                    subjects=['inf1000'],
                    periods=['first:begins(0)', 'second:begins(6):ends(1)'],
                    assignments=['oblig1', 'oblig2:pub(10)'],
                    assignmentgroups=['g1:candidate(zakia):examiner(cotryti)',
                                      'g2:candidate(nataliib):examiner(jose)'],
                    deadlines=['d1:ends(10):text(First deadline)'])

        node = Node.objects.get(pk=self.ti.uio.pk)
        node.long_name = "university"
        node.save()
        self.ti.reload_from_db(self.ti.uio)
        self.assertEquals(node, self.ti.uio)

    def test_create_superuser(self):
        self.ti.add(nodes='uio.ifi',
                    subjects=['inf1000'],
                    periods=['first:begins(0)', 'second:begins(6):ends(1)'],
                    assignments=['oblig1', 'oblig2:pub(10)'],
                    assignmentgroups=['g1:candidate(zakia):examiner(cotryti)',
                                      'g2:candidate(nataliib):examiner(jose)'],
                    deadlines=['d1:ends(10):text(First deadline)'])

        # create a superuser
        self.ti.create_superuser('grandma')
        self.assertTrue(self.ti.grandma.is_superuser)

        # assert that the username needs to be unique!
        with self.assertRaises(Exception):
            self.ti.create_superuser('cotryti')

    def test_load_generic_data(self):
        self.ti.load_generic_scenario()

    def test_create_user(self):
        self.ti.add(nodes='uio.ifi',
                    subjects=['inf1000'],
                    periods=['first:begins(0)', 'second:begins(6):ends(1)'],
                    assignments=['oblig1:anon(true)', 'oblig2:pub(10)'],
                    assignmentgroups=['g1:candidate(zakia;aikaz):examiner(cotryti)',
                                      'g2:candidate(nataliib):examiner(jose)'],
                    deadlines=['d1:ends(10):text(First deadline)'])

        self.ti.create_user('someUser')

        self.assertEquals(self.ti.someUser, User.objects.get(username='someUser'))
        with self.assertRaises(Exception):
            self.ti.create_user('cotryti')

    def test_new_deadline_variables(self):
        self.ti.add(nodes='uio.ifi',
                    subjects=['inf1000'],
                    periods=['first:begins(0)', 'second:begins(6):ends(1)'],
                    assignments=['oblig1:anon(true)', 'oblig2:pub(10)'],
                    assignmentgroups=['g1:candidate(zakia;aikaz):examiner(cotryti)',
                                      'g2:candidate(nataliib):examiner(jose)'],
                    deadlines=['d1:ends(10):text(First deadline)'])

        # check that deadline variables work as expected
        self.assertEquals(self.ti.inf1000_first_oblig1_g1_deadlines[0],
                          self.ti.inf1000_first_oblig1_g1_deadline1)

        # add a new deadline and check that a new variable is created
        self.ti.add_to_path('uio.ifi;inf1000.first.oblig1.g1.d2:ends(20)')
        self.assertEquals(self.ti.inf1000_first_oblig1_g1_deadlines[1],
                          self.ti.inf1000_first_oblig1_g1_deadline2)

        # add a new deadline with the same datetime, and check that it fails
        with self.assertRaises(ValidationError):
            self.ti.add_to_path('uio.ifi;inf1000.first.oblig1.g1.d2:ends(20)')

    def test_new_delivery_variables(self):
        self.ti.add(nodes='uio.ifi',
                    subjects=['inf1000'],
                    periods=['first:begins(0)', 'second:begins(6):ends(1)'],
                    assignments=['oblig1:anon(true)', 'oblig2:pub(10)'],
                    assignmentgroups=['g1:candidate(zakia;aikaz):examiner(cotryti)',
                                      'g2:candidate(nataliib):examiner(jose)'],
                    deadlines=['d1:ends(10):text(First deadline)'])

        # add a delivery
        self.ti.add_delivery(self.ti.inf1000_first_oblig1_g1)

        # and assert that the new variable is created
        self.assertEquals(self.ti.inf1000_first_oblig1_g1_deliveries[0],
                          self.ti.inf1000_first_oblig1_g1_deadline1_delivery1)

        # add another
        self.ti.add_delivery(self.ti.inf1000_first_oblig1_g1)

        # and assert that the new variable is created
        self.assertEquals(self.ti.inf1000_first_oblig1_g1_deliveries[1],
                          self.ti.inf1000_first_oblig1_g1_deadline1_delivery2)

        # add a new deadline, and a delivery to that
        self.ti.add_to_path('uio.ifi;inf1000.first.oblig1.g1.d2:ends(12)')
        self.ti.add_delivery(self.ti.inf1000_first_oblig1_g1)
