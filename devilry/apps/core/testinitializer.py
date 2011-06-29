from django.contrib.auth.models import User
# from django.conf import settings

from models import Node, Subject, Period, Assignment, AssignmentGroup, Delivery, FileMeta, Candidate


class TestInitializer(object):

    nodes = {}
    subjects = {}
    periods = {}
    assignments = {}
    deliveries = {}
    feedbacks = {}

    def _create_or_add_user(self, name):
        user = User(username=name)
        try:
            user.clean()
            user.save()
        except:
            user = User.objects.get(username=name)
        return user

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
        return node

    def _parse_user_list(self, text):
        res = {'admin': [], 'examiner': [], 'candidate': []}
        if not text:
            return res
        sections = text.split(':')
        for section in sections:
            res[section[:section.index('(')]] = section[section.index('(') + 1 : section.index(')')].split(',')
        return res

    # parse the node stuff!
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

            roles_and_users = self._parse_user_list(users_arg)
            new_node = self._create_or_add_node(node_name, roles_and_users)

            # set up the relation ship between the previous node
            if prev_node:
                prev_node.child_nodes.add(new_node)
            prev_node = new_node

    def add(self, nodes=None, subjects=None, periods=None, assignments=None, delivery=None, feedback=None):

        # do the nodes
        if nodes:
            self._do_the_nodes(nodes)

        if subjects:
            pass

        if periods:
            pass

        if assignments:
            pass

        if delivery:
            pass

        if feedback:
            pass

    @classmethod
    def example(self):
        # "uio.ifi:inf000[1-3](admin{counter},otheradmin{counter}).h0[1-6].oblig[1-2].(student[0-2],otherstud[0-2])"

        self.add(nodes="uio:admin(rektor).ifi:admin(mortend)",
                 subjects=["inf1000:admin(stein,steing)", "inf1100:admin(arne)"],
                 periods=["2009", "2010"],
                 assignments=["oblig1:student(student0,studen1):examiner(bendiko)", "oblig2"])
        self.

        self.add(nodes="uio.ifi",
                 subjects=["inf1000"],
                 periods=["2009"],
                 assignments=["oblig1:student(stud3)"])


