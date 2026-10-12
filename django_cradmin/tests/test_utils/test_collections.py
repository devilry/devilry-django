from django import test

from django_cradmin.utils import cradmin_collections


class TestOrderedSet(test.TestCase):
    def test_empty_sanity(self):
        ordered_set = cradmin_collections.OrderedSet()
        self.assertEqual([], list(ordered_set))

    def test_sanity(self):
        ordered_set = cradmin_collections.OrderedSet()
        ordered_set.add("a")
        ordered_set.add("b")
        self.assertEqual(["a", "b"], list(ordered_set))

    def test_duplicates(self):
        ordered_set = cradmin_collections.OrderedSet()
        ordered_set.add("a")
        ordered_set.add("b")
        ordered_set.add("a")
        self.assertEqual(["a", "b"], list(ordered_set))
