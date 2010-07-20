from django.contrib.auth.models import User

from models import Node, Subject, Period, Assignment, AssignmentGroup, \
        Delivery, FileMeta, Candidate
from deliverystore import FileNotFoundError
from datetime import datetime, timedelta



def create_from_path(path):
    """ Create a Node, Subject, Period, Assignment or AssignmentGroup from
    ``path``.
    
    Examples::

        assignmentgroup = create_from_path(
                'ifi.inf1100.spring05.oblig1.student1,student2')
        oblig1 = create_from_path(
                'ifi.inf1100.spring05.oblig1')
    """
    p = path.split('.')
    node = Node(short_name=p[0], long_name=p[0])
    try:
        node.save()
    except:
        node = Node.objects.get(short_name=p[0])
    last = node
    if len(p) > 1:
        subject = Subject(parentnode=node, short_name=p[1], long_name=p[1])
        try:
            subject.save()
        except:
            subject = Subject.objects.get(short_name=p[1])
        last = subject
    if len(p) > 2:
        period = Period(parentnode=subject, short_name=p[2],
                long_name=p[2], start_time=datetime.now(),
                end_time=datetime.now() + timedelta(10))
        try:
            period.save()
        except:
            period = Period.objects.get(parentnode=subject,
                    short_name=p[2])
        last = period
    if len(p) > 3:
        assignment = Assignment(parentnode=period, short_name=p[3],
                long_name=p[3], publishing_time=datetime.now())
        try:
            assignment.save()
        except:
            assignment = Assignment.objects.get(parentnode=period,
                    short_name=p[3])
        last = assignment
    if len(p) > 4:
        usernames = p[4].split(',')
        users = []
        for u in usernames:
            user = User(username=u)
            try:
                user.save()
            except:
                user = User.objects.get(username=u)
            users.append(user)
        assignment_group = AssignmentGroup(parentnode=assignment)
        assignment_group.save()
        for user in users:
            assignment_group.candidate_set.add(Candidate(student=user))
        last = assignment_group
    return last


class TestDeliveryStoreMixin(object):
    """ Mixin-class that tests if
    :class:`devilry.core.deliverystore.DeliveryStoreInterface` is
    implemented correctly.

    You only need to override
    :meth:`get_storageobj`, and maybe :meth:`setUp` and :meth:`tearDown`,
    but make sure you call ``super(..., self).setUp()`` if you override it.
    
    You **must** mixin this class before :class:`django.test.TestCase` like
    so::

        class TestMyDeliveryStore(TestDeliveryStoreMixin, django.test.TestCase):
            ...
    """
    fixtures = ['tests/core/users', 'tests/core/nodes', 'tests/core/subjects',
            'tests/core/periods', 'tests/core/assignments',
            'tests/core/assignmentgroups', 'tests/core/candidates',
            'tests/core/deliveries']

    def get_storageobj(self):
        """ Return a object implementing
        :class:`devilry.core.deliverystore.DeliveryStoreInterface` """
        raise NotImplementedError()

    def setUp(self):
        """ Make sure to call this if you override it in subclasses, or the
        tests **will fail**. """
        self.filemeta = FileMeta()
        self.filemeta.delivery = Delivery.objects.get(id=1)
        self.filemeta.size = 0
        self.filemeta.filename = 'test.txt'

    def test_writemany(self):
        store = self.get_storageobj()
        w = store.write_open(self.filemeta)
        w.write('hello')
        w.write(' world')
        w.write('!')
        w.close()
        r = store.read_open(self.filemeta)
        self.assertEquals(r.read(), 'hello world!')

    def test_readwrite(self):
        store = self.get_storageobj()
        self.assertFalse(store.exists(self.filemeta))
        self.assertRaises(FileNotFoundError, store.read_open, self.filemeta)
        w = store.write_open(self.filemeta)
        w.write('hello')
        w.close()
        self.assertTrue(store.exists(self.filemeta))
        store.remove(self.filemeta)
        self.assertFalse(store.exists(self.filemeta))
        self.assertRaises(FileNotFoundError, store.remove, self.filemeta)
