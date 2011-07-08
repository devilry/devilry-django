from datetime import datetime, timedelta
from django.contrib.auth.models import User
from models import Node, Subject, Period, Assignment, AssignmentGroup, Candidate, Deadline, Delivery, StaticFeedback


# TODO:
# raise error when trying to give roles to nodes that dont support it?
#
# Example:
#
# subjects don't have candidates, so trying to create a subject with
# `add(subjects=['inf1010:candidates(bendiko)'])` doesn't fail, it
# just doesn't add any users at all.


class StuffError(Exception):
    """ This is stuff """


class TestHelper(object):
    """
    This class helps generate test data.
    """

    objects_created = 0

    def refresh_var(self, obj):
        freshed_obj = type(obj).objects.get(pk=obj.pk)
        for key in vars(self).keys():
            if vars(self)[key] == obj:
                vars(self)[key] = freshed_obj

    def create_superuser(self, name):
        su = User(username=name, is_superuser=True)
        su.clean()
        su.save()
        vars(self)[name] = su

    def add_delivery(self, assignmentgroup, files={}, after_last_deadline=False):
        """
        :param assignmentgroup: Expects either a Delivery object or a
        string path to an assignmentgroup. This is a mandatory parameter.

        :param files: a dictionary with key/values as file name and
        file content as described in Delivery.add_file()

        :param after_last_deadline: if true, sets time_of_delivery 1
        day later than the assignmentgroups active deadline
        """

        # TODO: add timestamp-parameter for time_of_delivery

        if assignmentgroup == None:
            return

        # Check if we're given a group, or fetch from a path
        if type(assignmentgroup) == AssignmentGroup:
            group = assignmentgroup
        elif type(assignmentgroup) == str:
            group = self.get_object_from_path(assignmentgroup)

        # Fetch the first User of the candidates
        delivery = group.deliveries.create(delivered_by=group.candidates.all()[0].student, successful=False)

        # add files if there are any
        for filename in files.keys():
            delivery.add_file(filename, files[filename])

        if after_last_deadline:
            # set the deliverytime to after the deadline
            delivery.time_of_delivery = group.get_active_deadline().deadline + timedelta(days=1)
#            print delivery.time_of_delivery

        delivery.successful = True
        delivery.clean()
        delivery.save()
        # add it to the groups delivery list
        varname = (group.parentnode.parentnode.parentnode.short_name + '_' +  # subject_
                   group.parentnode.parentnode.short_name + '_' +             # period_
                   group.parentnode.short_name + '_' +                        # assignment_
                   group.name + '_deliveries')
        if varname in vars(self).keys():
            vars(self)[varname].append(delivery)
        else:
            vars(self)[varname] = [delivery]

        self.objects_created += 1
        return delivery

    def add_feedback(self, delivery=None, verdict=None, examiner=None, timestamp=None):
        """
        :param delivery: either a Delivery object or a string path to
        an assignmentgroup, where we take the last delivery made. This
        is the only mandatory parameter

        :param verdict: a dict containing grade, score and passing
        grade. Defaults to grade='A', points=100,
        is_passing_grade=True

        :param examiner: A User object. Defaults to the first examiner
        for the delivery's assignment group.

        :param timestamp: A datetime object for when the feedback was
        saved. Defaults to same time the delivery was made
        """

        # get the delivery object
        if type(delivery) == str:
            # since we cant create a path directly to a delivery,
            # expect an assignmentgroup path
            delivery = self.get_object_from_path(delivery)

        # if the path led to an AssignmentGroup, get that groups
        # latest delivery
        if type(delivery) == AssignmentGroup:
            delivery = delivery.deliveries.all().order_by('time_of_delivery')[0]

        # if none of the above, expect we were given a Delivery
        if not type(delivery) == Delivery:
            raise ValueError('Invalid delivery given. Got ' + delivery)

        # get the verdict
        if not verdict:
            verdict = {'grade': 'A', 'points': 100, 'is_passing_grade': True}

        # get the examiner
        if not examiner:
            examiner = delivery.assignment_group.examiners.all()[0]

        # get the timestamp
        if not timestamp:
            timestamp = delivery.assignment_group.get_active_deadline().deadline

        # create the feedback
        feedback = StaticFeedback(saved_by=examiner, delivery=delivery, grade=verdict['grade'],
                                  points=verdict['points'], is_passing_grade=verdict['is_passing_grade'])
        # and finally, save it!
        try:
            feedback.clean()
            feedback.save()
        except:
            raise

        # add it to the groups feedbacks list
        varname = (delivery.assignment_group.parentnode.parentnode.parentnode.short_name + '_' +  # subject_
                   delivery.assignment_group.parentnode.parentnode.short_name + '_' +             # period_
                   delivery.assignment_group.parentnode.short_name + '_' +                        # assignment_
                   delivery.assignment_group.name + '_feedbacks')

        if varname in vars(self).keys():
            vars(self)[varname].append(feedback)
        else:
            vars(self)[varname] = [feedback]

        self.objects_created += 1
        return feedback

    def _parse_extras(self, text, allowed_extras=[]):
        """Parse an 'extras' string. Separate at ':', and create a
        key/value pair of name/value
        """
        res = {}
        for extra in allowed_extras:
            res[extra] = []
        # res = {'admin': [], 'examiner': [], 'candidate': [], 'when': []}
        if not text:
            return res

        sections = text.split(':')
        for section in sections:
            key = section[:section.index('(')]
            if key not in res:
                raise ValueError("{0} is not an allowed command.".format(key))
            res[key] = section[section.index('(') + 1 : section.index(')')].split(',')
        return res

    def _create_or_add_user(self, name):
        user = User(username=name)
        try:
            user.clean()
            user.save()
        except:
            user = User.objects.get(username=name)
        vars(self)[user.username] = user
        self.objects_created += 1
        return user

#######
##
## Node specifics
##
#######
    def _create_or_add_node(self, parent, name, users):
        node = Node(parentnode=parent, short_name=name, long_name=name.capitalize())
        try:
            node.clean()
            node.save()
        except:
            node = Node.objects.get(parentnode=parent, short_name=name)

        # allowed roles in node are:
        for admin in users['admin']:
            node.admins.add(self._create_or_add_user(admin))

        node.clean()
        node.save()

        vars(self)[node.short_name] = node
        self.objects_created += 1
        return node

    def _do_the_nodes(self, nodes):

        if not nodes:
            return None

        new_node = None
        # separate the nodes

        prev_node = None
        for n in nodes.split('.'):
            # initialize the admin-argument
            try:
                node_name, extras_arg = n.split(':', 1)
            except ValueError:
                node_name = n
                extras_arg = None
            users = self._parse_extras(extras_arg, ['admin'])
            new_node = self._create_or_add_node(prev_node, node_name, users)
            prev_node = new_node
        return new_node

#######
##
## Subject specifics
##
#######
    def _create_or_add_subject(self, subject_name, parentnode, extras):
        subject = Subject(parentnode=parentnode, short_name=subject_name, long_name=subject_name.capitalize())
        try:
            subject.clean()
            subject.save()
        except:
            subject = Subject.objects.get(short_name=subject_name)

        # add the extras (only admins allowed in subject)
        for admin in extras['admin']:
            subject.admins.add(self._create_or_add_user(admin))

        # if a long_name is given, set it
        if extras['ln']:
            subject.long_name = extras['ln'][0]

        subject.clean()
        subject.save()

        vars(self)[subject.short_name] = subject
        self.objects_created += 1
        return subject

    def _do_the_subjects(self, node, subject_list):

        # if not node:
        #     raise ValueError('No nodes created. Subjects needs node-parents')

        created_subjects = []
        for subject in subject_list:

            try:
                subject_name, extras_arg = subject.split(':', 1)
            except ValueError:
                subject_name = subject
                extras_arg = None

            users = self._parse_extras(extras_arg, ['admin', 'ln'])
            new_subject = self._create_or_add_subject(subject_name, node, users)
            created_subjects.append(new_subject)
        return created_subjects

#######
##
## Period specifics
##
#######
    def _create_or_add_period(self, period_name, parentnode, extras):
        period = Period(parentnode=parentnode, short_name=period_name, long_name=period_name.capitalize(),
                        start_time=datetime.now(), end_time=datetime.now() + timedelta(days=5 * 30))
        try:
            period.clean()
            period.save()
        except:
            period = Period.objects.get(parentnode=parentnode, short_name=period_name)

        # add the extras (only admins allowed in subject)
        for admin in extras['admin']:
            period.admins.add(self._create_or_add_user(admin))

        if extras['begins']:
            period.start_time = datetime.now() + timedelta(days=int(extras['begins'][0]) * 30)
        if extras['ends']:
            period.end_time = period.start_time + timedelta(days=int(extras['ends'][0]) * 30)
        elif extras['begins'] and not extras['ends']:
            period.end_time = period.start_time + timedelta(5 * 30)

        if extras['ln']:
            period.long_name = extras['ln']

        period.clean()
        period.save()

        vars(self)[parentnode.short_name + '_' + period.short_name] = period
        self.objects_created += 1
        return period

    def _do_the_periods(self, subjects, periods_list):

        # if not subjects:
        #     subjects = Subject.objects.all()
        #     if not subjects:
        #         raise ValueError("No subjects created. Periods needs subject-parents")

        created_periods = []
        for subject in subjects:
            for period in periods_list:

                try:
                    period_name, extras_arg = period.split(':', 1)
                except ValueError:
                    period_name = period
                    extras_arg = None

                extras = self._parse_extras(extras_arg, ['admin', 'begins', 'ends', 'ln'])
                new_period = self._create_or_add_period(period_name, subject, extras)
                created_periods.append(new_period)
        return created_periods

#######
##
## Assignment specifics
##
#######
    def _create_or_add_assignment(self, assignment_name, parentnode, extras):
        assignment = Assignment(parentnode=parentnode, short_name=assignment_name,
                                long_name=assignment_name.capitalize(), publishing_time=parentnode.start_time)
        try:
            assignment.clean()
            assignment.save()
        except:
            assignment = Assignment.objects.get(parentnode=parentnode,
                                                short_name=assignment_name)

        # add the users (only admins allowed in subject)
        for admin in extras['admin']:
            assignment.admins.add(self._create_or_add_user(admin))

        if extras['pub']:
            assignment.publishing_time += timedelta(days=int(extras['pub'][0]))

        if extras['anon']:
            if extras['anon'][0] == 'true':
                assignment.anonymous = True
            elif extras['anon'][0] == 'false':
                assignment.anonymous = False
            else:
                raise ValueError("anon must be 'true' or 'false'")

        assignment.clean()
        assignment.save()

        vars(self)[parentnode.parentnode.short_name + '_' +  # subject
                   parentnode.short_name + '_' +             # period
                   assignment.short_name] = assignment
        self.objects_created += 1
        return assignment

    def _do_the_assignments(self, periods, assignments_list):

        # if not periods:
        #     periods = Period.objects.all()
        #     if not periods:
        #         raise ValueError("No periods created. Assignments needs a period-parent")

        created_assignments = []
        for period in periods:
            for assignment in assignments_list:

                try:
                    assignment_name, extras_arg = assignment.split(':', 1)
                except ValueError:
                    assignment_name = assignment
                    extras_arg = None

                users = self._parse_extras(extras_arg, ['admin', 'pub', 'anon'])
                new_assignment = self._create_or_add_assignment(assignment_name, period, users)
                created_assignments.append(new_assignment)
        return created_assignments

#######
##
## Assignmentgroups specifics
##
#######
    def _create_or_add_assignmentgroup(self, group_name, parentnode, extras):
        if AssignmentGroup.objects.filter(parentnode=parentnode, name=group_name).count() == 1:
            group = AssignmentGroup.objects.get(parentnode=parentnode, name=group_name)
        else:
            group = AssignmentGroup(parentnode=parentnode, name=group_name)
            try:
                group.clean()
                group.save()
            except:
                raise ValueError("Assignmentgroup not created!")

        # add the extras (only admins allowed in subject)
        for candidate in extras['candidate']:
            group.candidates.add(Candidate(student=self._create_or_add_user(candidate)))
            cand = group.candidates.order_by('-id')[0]
            cand.candidate_id = str(cand.student.id)
            cand.clean()
            cand.save()

        for examiner in extras['examiner']:
            group.examiners.add(self._create_or_add_user(examiner))

        group.clean()
        group.save()

        vars(self)[parentnode.parentnode.parentnode.short_name + '_' +  # subject_
                   parentnode.parentnode.short_name + '_' +             # period_
                   parentnode.short_name + '_' +                        # assignment_
                   group_name] = group
        self.objects_created += 1
        return group

    def _do_the_assignmentgroups(self, assignments, assignmentgroups_list):

        # if not assignments:
        #     assignments = Assignment.objects.all()
        #     if not assignments:
        #         raise ValueError("No periods created. Assignments needs a period-parent")

        created_groups = []
        for assignment in assignments:
            for group in assignmentgroups_list:

                try:
                    group_name, extras_arg = group.split(':', 1)
                except ValueError:
                    group_name = group
                    extras_arg = None

                users = self._parse_extras(extras_arg, ['examiner', 'candidate'])
                new_group = self._create_or_add_assignmentgroup(group_name, assignment, users)
                created_groups.append(new_group)
        return created_groups

#######
##
## Deadlines specifics
##
#######
    def _create_or_add_deadline(self, deadline_name, parentnode, extras):
        deadline = Deadline(assignment_group=parentnode, deadline=parentnode.parentnode.publishing_time + timedelta(days=10))
        try:
            deadline.clean()
            deadline.save()
        except:
            raise  ValueError("something impossible happened when creating deadline")

        if extras['ends']:
            deadline.deadline = parentnode.parentnode.publishing_time + timedelta(int(extras['ends'][0]))
        if extras['text']:
            deadline.text = extras['text'][0]

        # create the variable ref'ing directly to the deadline
        prefix = (parentnode.parentnode.parentnode.parentnode.short_name + '_' +  # subject_
                  parentnode.parentnode.parentnode.short_name + '_' +             # period_
                  parentnode.parentnode.short_name + '_' +                        # assignment_
                  parentnode.name + '_')

        deadline.clean()
        deadline.save()

        # only create this variable if a name is given
        if deadline_name:
            varname = prefix + deadline_name
            vars(self)[varname] = deadline

        # Add or append to the deadlines list. Last element will be
        # the same as the most recently created deadline, stored in
        # prefix+deadline_name
        vardict = prefix + 'deadlines'
        if vardict in vars(self).keys():
            vars(self)[vardict].append(deadline)
        else:
            vars(self)[vardict] = [deadline]

        self.objects_created += 1
        return deadline

    def _do_the_deadlines(self, assignmentgroups, deadlines_list):
        created_deadlines = []
        for assignmentgroup in assignmentgroups:
            for deadline_ in deadlines_list:
                try:
                    deadline_name, extras_arg = deadline_.split(':', 1)
                except ValueError:
                    deadline_name = deadline_
                    extras_arg = None

                extras = self._parse_extras(extras_arg, ['ends', 'text'])
                new_deadline = self._create_or_add_deadline(deadline_name, assignmentgroup, extras)
                created_deadlines.append(new_deadline)
        return created_deadlines

    def _validate_args(self, args):
        i = 0
        while i < len(args):
            arg = args[i]
            i += 1
            # look for the first none
            if not arg:
                while i < len(args):
                    # if any args are not-None, return false
                    if args[i]:
                        return False
                    i += 1
        return True

    def add(self, nodes=None, subjects=None, periods=None, assignments=None, assignmentgroups=None,
            delivery=None, feedback=None, deadlines=None):

        # see if any of the parameters 'below' are !None
        args = [subjects, periods, assignments, assignmentgroups, deadlines, delivery, feedback]
        if not self._validate_args(args):
            raise ValueError('Invalid parameters. ')

        if not nodes:
            return
        nodes = self._do_the_nodes(nodes)

        if not subjects:
            return

        subjects = self._do_the_subjects(nodes, subjects)

        if not periods:
            return
        periods = self._do_the_periods(subjects, periods)

        if not assignments:
            return
        assignments = self._do_the_assignments(periods, assignments)

        if not assignmentgroups:
            return
        assignmentgroups = self._do_the_assignmentgroups(assignments, assignmentgroups)

        if not deadlines:
            return
        deadlines = self._do_the_deadlines(assignmentgroups, deadlines)

    # splits up a dot separated path, and calls add() with those
    # pieces as arguments
    def add_to_path(self, path):
        nodes = None
        subjects = None
        periods = None
        assignments = None
        assignmentgroups = None
        deadlines = None

        nodes, rest = path.split(';', 1)
        split_rest = rest.split('.')
        split_rest.reverse()

        if split_rest:
            subjects = [split_rest.pop()]

        if split_rest:
            periods = [split_rest.pop()]

        if split_rest:
            assignments = [split_rest.pop()]

        if split_rest:
            assignmentgroups = [split_rest.pop()]

        if split_rest:
            deadlines = [split_rest.pop()]

        self.add(nodes=nodes, subjects=subjects, periods=periods, assignments=assignments,
                 assignmentgroups=assignmentgroups, deadlines=deadlines)

    def get_object_from_path(self, path):
        try:
            nodes, rest = path.split(';', 1)
        except ValueError:
            rest = path
        varname = rest.replace('.', '_')
        return vars(self)[varname]

    def load_generic_scenario(self):
        # set up the base structure
        self.add(nodes='uni:admin(mortend)',
                 subjects=['cs101:admin(admin1,admin2):ln(Basic OO programming)',
                           'cs110:admin(admin3,admin4):ln(Basic scientific programming)',
                           'cs111:admin(admin1,damin3):ln(Advanced OO programming)'],
                 periods=['fall11', 'spring11:begins(6)'])

        # add 4 assignments to inf101 and inf110 in fall and spring
        self.add(nodes='uni',
                 subjects=['inf101', 'inf110'],
                 periods=['fall11', 'spring11'],
                 assignments=['a1', 'a2'])

        # add 12 assignments to inf111 fall and spring.
        self.add(nodes='uni',
                 subjects=['cs111'],
                 periods=['fall11', 'spring11'],
                 assignments=['week1', 'week2', 'week3', 'week4'])

        # set up some students with descriptive names

        # inf101 is so easy, everyone passes
        self.add_to_path('uni;cs101.fall11.a1.g1:candidate(goodStud1):examiner(examiner1).dl:ends(5)')
        self.add_to_path('uni;cs101.fall11.a1.g2:candidate(goodStud2):examiner(examiner1).dl:ends(5)')
        self.add_to_path('uni;cs101.fall11.a1.g3:candidate(badStud3):examiner(examiner2).dl:ends(5)')
        self.add_to_path('uni;cs101.fall11.a1.g4:candidate(okStud4):examiner(examiner2).dl:ends(5)')

        self.add_to_path('uni;cs101.fall11.a2.g1:candidate(goodStud1):examiner(examiner1).dl:ends(5)')
        self.add_to_path('uni;cs101.fall11.a2.g2:candidate(goodStud2):examiner(examiner1).dl:ends(5)')
        self.add_to_path('uni;cs101.fall11.a2.g3:candidate(badStud3):examiner(examiner2).dl:ends(5)')
        self.add_to_path('uni;cs101.fall11.a2.g4:candidate(okStud4):examiner(examiner2).dl:ends(5)')

        # inf110 is an easy group-project, everyone passes
        self.add_to_path('uni;cs110.fall11.a1.g1:candidate(goodStud1,goodStud2):examiner(examiner1).dl:ends(14)')
        self.add_to_path('uni;cs110.fall11.a1.g2:candidate(badStud3,okStud4):examiner(examiner2).dl.ends(14)')

        self.add_to_path('uni;cs110.fall11.a2.g1:candidate(goodStud1,goodStud2):examiner(examiner1).dl:ends(14)')
        self.add_to_path('uni;cs110.fall11.a2.g2:candidate(badStud3,okStud4):examiner(examiner2).dl.ends(14)')

        # inf111 is hard! Everyone passes week1
        self.add_to_path('uni;cs111.fall11.week1.g1:candidate(goodStud1):examiner(examiner3).dl:ends(5)')
        self.add_to_path('uni;cs111.fall11.week1.g2:candidate(goodStud2):examiner(examiner3).dl:ends(5)')
        self.add_to_path('uni;cs111.fall11.week1.g3:candidate(badStud3):examiner(examiner3).dl:ends(5)')
        self.add_to_path('uni;cs111.fall11.week1.g4:candidate(okStud4):examiner(examiner3).dl:ends(5)')

        # and 2
        self.add_to_path('uni;cs111.fall11.week2.g1:candidate(goodStud1):examiner(examiner3).dl:ends(5)')
        self.add_to_path('uni;cs111.fall11.week2.g2:candidate(goodStud2):examiner(examiner3).dl:ends(5)')
        self.add_to_path('uni;cs111.fall11.week2.g3:candidate(badStud3):examiner(examiner3).dl:ends(5)')
        self.add_to_path('uni;cs111.fall11.week2.g4:candidate(okStud4):examiner(examiner3).dl:ends(5)')

        # badStud4 fails at week3
        self.add_to_path('uni;cs111.fall11.week3.g1:candidate(goodStud1):examiner(examiner3).dl:ends(5)')
        self.add_to_path('uni;cs111.fall11.week3.g2:candidate(goodStud2):examiner(examiner3).dl:ends(5)')
        self.add_to_path('uni;cs111.fall11.week3.g4:candidate(okStud2):examiner(examiner3).dl:ends(5)')

        # and okStud4 fails at week4
        self.add_to_path('uni;cs111.fall11.week4.g1:candidate(goodStud1):examiner(examiner3).dl:ends(5)')
        self.add_to_path('uni;cs111.fall11.week4.g2:candidate(goodStud2):examiner(examiner3).dl:ends(5)')

        # deliveries
        goodFile = {'good.py': ['print ', 'awesome']}
        okFile = {'ok.py': ['print ', 'meh']}
        badFile = {'bad.py': ['print ', 'bah']}

        # cs101
        self.add_delivery('cs101.fall11.a1.g1', goodFile)
        self.add_delivery('cs101.fall11.a1.g2', goodFile)
        self.add_delivery('cs101.fall11.a1.g3', badFile)
        self.add_delivery('cs101.fall11.a1.g4', okFile)
        self.add_delivery('cs101.fall11.a2.g1', goodFile)
        self.add_delivery('cs101.fall11.a2.g2', goodFile)
        self.add_delivery('cs101.fall11.a2.g3', badFile)
        self.add_delivery('cs101.fall11.a2.g4', okFile)

        # cs110
        self.add_delivery('cs110.fall11.a1.g1', goodFile)
        self.add_delivery('cs110.fall11.a1.g1', goodFile)
        self.add_delivery('cs110.fall11.a2.g2', badFile)
        self.add_delivery('cs110.fall11.a2.g2', okFile)

        # cs111
        self.add_delivery('cs111.fall11.week1.g1', goodFile)
        self.add_delivery('cs111.fall11.week1.g2', goodFile)
        self.add_delivery('cs111.fall11.week1.g3', badFile)
        self.add_delivery('cs111.fall11.week1.g4', okFile)

        # g3's delivery fails here
        self.add_delivery('cs111.fall11.week2.g1', goodFile)
        self.add_delivery('cs111.fall11.week2.g2', goodFile)
        self.add_delivery('cs111.fall11.week2.g3', badFile)
        self.add_delivery('cs111.fall11.week2.g4', okFile)

        # g4's delivery fails here
        self.add_delivery('cs111.fall11.week3.g1', goodFile)
        self.add_delivery('cs111.fall11.week3.g2', goodFile)
        self.add_delivery('cs111.fall11.week3.g4', okFile)

        # g4 fails
        self.add_delivery('cs111.fall11.week4.g1', goodFile)
        self.add_delivery('cs111.fall11.week4.g2', goodFile)

        # feedbacks
        #   an empty verdict defaults to max score
        goodVerdict = None
        okVerdict = {'grade': 'C', 'points': 85, 'is_passing_grade': True}
        badVerdict = {'grade': 'E', 'points': 60, 'is_passing_grade': True}
        failVerdict = {'grade': 'F', 'points': 30, 'is_passing_grade': False}

        self.add_feedback('cs101.fall11.a1.g1', verdict=goodVerdict)
        self.add_feedback('cs101.fall11.a1.g2', verdict=goodVerdict)
        self.add_feedback('cs101.fall11.a1.g3', verdict=badVerdict)
        self.add_feedback('cs101.fall11.a1.g4', verdict=okVerdict)
        self.add_feedback('cs101.fall11.a2.g1', verdict=goodVerdict)
        self.add_feedback('cs101.fall11.a2.g2', verdict=goodVerdict)
        self.add_feedback('cs101.fall11.a2.g3', verdict=badVerdict)
        self.add_feedback('cs101.fall11.a2.g4', verdict=okVerdict)

        # cs110
        self.add_feedback('cs110.fall11.a1.g1', verdict=goodVerdict)
        self.add_feedback('cs110.fall11.a1.g1', verdict=badVerdict)
        self.add_feedback('cs110.fall11.a2.g2', verdict=goodVerdict)
        self.add_feedback('cs110.fall11.a2.g2', verdict=okVerdict)

        # cs111
        self.add_feedback('cs111.fall11.week1.g1', verdict=goodVerdict)
        self.add_feedback('cs111.fall11.week1.g2', verdict=goodVerdict)
        self.add_feedback('cs111.fall11.week1.g3', verdict=badVerdict)
        self.add_feedback('cs111.fall11.week1.g4', verdict=okVerdict)

        # g3's feedback fails here
        self.add_feedback('cs111.fall11.week2.g1', verdict=goodVerdict)
        self.add_feedback('cs111.fall11.week2.g2', verdict=goodVerdict)
        self.add_feedback('cs111.fall11.week2.g3', verdict=failVerdict)
        self.add_feedback('cs111.fall11.week2.g4', verdict=okVerdict)

        # g4's feedback fails here
        self.add_feedback('cs111.fall11.week3.g1', verdict=goodVerdict)
        self.add_feedback('cs111.fall11.week3.g2', verdict=goodVerdict)
        self.add_feedback('cs111.fall11.week3.g4', verdict=failVerdict)

        # g4 fails
        self.add_feedback('cs111.fall11.week4.g1', verdict=goodVerdict)
        self.add_feedback('cs111.fall11.week4.g2', verdict=goodVerdict)
