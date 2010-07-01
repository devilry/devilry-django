from models import Delivery, FileMeta
from deliverystore import FileNotFoundError


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
        w = store.write_open(self.filemeta)
        w.write('hello')
        w.close()
        self.assertTrue(store.exists(self.filemeta))
        store.remove(self.filemeta)
        self.assertFalse(store.exists(self.filemeta))
        self.assertRaises(FileNotFoundError, store.remove, self.filemeta)
