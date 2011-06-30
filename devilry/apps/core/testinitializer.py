from datetime import datetime, timedelta
from django.contrib.auth.models import User
from models import Node, Subject, Period, Assignment, AssignmentGroup, Candidate


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


class TestInitializer(object):

    def _parse_user_list(self, text):
        res = {'admin': [], 'examiner': [], 'candidate': []}
        if not text:
            return res

        sections = text.split(':')
        for section in sections:
            key = section[:section.index('(')]
            if key not in res:
                raise ValueError("{0} is not an allowed role.".format(key))
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
        return user

#######
##
## Node specifics
##
#######
    def _create_or_add_node(self, name, users):
        node = Node(short_name=name, long_name=name.capitalize())
        try:
            node.clean()
            node.save()
        except:
            node = Node.objects.get(short_name=name)

        # allowed roles in node are:
        for admin in users['admin']:
            node.admins.add(self._create_or_add_user(admin))
        vars(self)[node.short_name] = node
        return node

    def _do_the_nodes(self, nodes):
        prev_node = None
        users_arg = None

        # separate the nodes
        for node in nodes.split('.'):

            # initialize the admin-argument
            try:
                node_name, users_arg = node.split(':', 1)
            except ValueError:
                node_name = node
                users_arg = None

            users = self._parse_user_list(users_arg)
            new_node = self._create_or_add_node(node_name, users)

            # set up the relation ship between the previous node
            if prev_node:
                prev_node.child_nodes.add(new_node)
            prev_node = new_node

#######
##
## Subject specifics
##
#######
    def _create_or_add_subject(self, subject_name, parentnode, users):
        subject = Subject(parentnode=parentnode, short_name=subject_name, long_name=subject_name.capitalize())
        try:
            subject.clean()
            subject.save()
        except:
            subject = Subject.objects.get(short_name=subject_name)

        # add the users (only admins allowed in subject)
        for admin in users['admin']:
            subject.admins.add(self._create_or_add_user(admin))
        vars(self)[subject.short_name] = subject
        return subject

    def _do_the_subjects(self, subject_list):

        nodes = Node.objects.all()
        if not nodes:
            raise Exception('No nodes created. Subjects needs node-parents')

        for node in nodes:
            for subject in subject_list:

                try:
                    subject_name, users_arg = subject.split(':', 1)
                except ValueError:
                    subject_name = subject
                    users_arg = None

                users = self._parse_user_list(users_arg)
                self._create_or_add_subject(subject_name, node, users)

#######
##
## Period specifics
##
#######
    def _create_or_add_period(self, period_name, parentnode, users):
        period = Period(parentnode=parentnode, short_name=period_name, long_name=period_name.capitalize(),
                        start_time=datetime.now(), end_time=datetime.now() + timedelta(10))
        try:
            period.clean()
            period.save()
        except:
            period = Period.objects.get(parentnode=parentnode, short_name=period_name)

        # add the users (only admins allowed in subject)
        for admin in users['admin']:
            period.admins.add(self._create_or_add_user(admin))

        vars(self)[parentnode.short_name + '_' + period.short_name] = period
        return period

    def _do_the_periods(self, periods_list):
        subjects = Subject.objects.all()
        if not subjects:
            raise Exception("No subjects created. Periods needs subject-parents")

        for subject in subjects:
            for period in periods_list:

                try:
                    period_name, users_arg = period.split(':', 1)
                except ValueError:
                    period_name = period
                    users_arg = None

                users = self._parse_user_list(users_arg)
                self._create_or_add_period(period_name, subject, users)

#######
##
## Assignment specifics
##
#######
    def _create_or_add_assignment(self, assignment_name, parentnode, users):
        assignment = Assignment(parentnode=parentnode, short_name=assignment_name,
                                long_name=assignment_name.capitalize(), publishing_time=datetime.now())
        try:
            assignment.clean()
            assignment.save()
        except:
            assignment = Assignment.objects.get(parentnode=parentnode,
                                                short_name=assignment_name)

        # add the users (only admins allowed in subject)
        for admin in users['admin']:
            assignment.admins.add(self._create_or_add_user(admin))

        for examiner in users['examiner']:
            assignment.examiners.add(self._create_or_add_user(examiner))

        vars(self)[parentnode.parentnode.short_name + '_' + parentnode.short_name + '_' + assignment.short_name] = assignment
        return assignment

    def _do_the_assignments(self, assignments_list):
        periods = Period.objects.all()
        if not periods:
            raise Exception("No periods created. Assignments needs a period-parent")

        for period in periods:
            for assignment in assignments_list:

                try:
                    assignment_name, users_arg = assignment.split(':', 1)
                except ValueError:
                    assignment_name = assignment
                    users_arg = None

                users = self._parse_user_list(users_arg)
                self._create_or_add_assignment(assignment_name, period, users)

#######
##
## Assignment group specifics
##
#######
    def _create_or_add_assignmentgroup(self, group_name, parentnode, users):
        if AssignmentGroup.objects.filter(parentnode=parentnode, name=group_name) == 1:
            group = AssignmentGroup.objects.filter(parentnode=parentnode, name=group_name)
        else:
            group = AssignmentGroup(parentnode=parentnode, name=group_name)
            try:
                group.clean()
                group.save()
            except:
                raise ValueError("Assignmentgroup not created!")

        # add the users (only admins allowed in subject)
        for candidate in users['candidate']:
            group.candidates.add(Candidate(student=self._create_or_add_user(candidate)))

        for examiner in users['examiner']:
            group.examiners.add(self._create_or_add_user(examiner))

        vars(self)[parentnode.parentnode.parentnode.short_name + '_' +  # subject_
                   parentnode.parentnode.short_name + '_' +             # period_
                   parentnode.short_name + '_' +                        # assignment_
                   group_name] = group
        return group

    def _do_the_assignmentgroups(self, assignmentgroups_list):
        assignments = Assignment.objects.all()
        if not assignments:
            raise ValueError("No periods created. Assignments needs a period-parent")

        for assignment in assignments:
            for group in assignmentgroups_list:

                try:
                    group_name, users_arg = group.split(':', 1)
                except ValueError:
                    group_name = group
                    users_arg = None

                users = self._parse_user_list(users_arg)
                self._create_or_add_assignmentgroup(group_name, assignment, users)

    def add(self, nodes=None, subjects=None, periods=None, assignments=None, assignmentgroups=None,
            delivery=None, feedback=None):

        if nodes:
            self._do_the_nodes(nodes)

        if subjects:
            self._do_the_subjects(subjects)

        if periods:
            self._do_the_periods(periods)

        if assignments:
            self._do_the_assignments(assignments)

        if assignmentgroups:
            self._do_the_assignmentgroups(assignmentgroups)

        if delivery:
            pass

        if feedback:
            pass

    @classmethod
    def example(self):
        self.add(nodes="uio:admin(rektor).ifi:admin(mortend)",
                 subjects=["inf1000:admin(stein,steing)", "inf1100:admin(arne)"],
                 periods=["2009", "2010"],
                 assignments=["oblig1:admin(jose)", "oblig2:admin(jose)"],
                 assignmentgroups=['g1:candidate(zakia):examiner(cotryti)',
                                   'g2:candidate(nataliib):examiner(jose)'],
                 )

        self.add(nodes="uio.ifi",
                 subjects=["inf1000"],
                 periods=["2009"],
                 assignments=["oblig1:student(stud3)"])
