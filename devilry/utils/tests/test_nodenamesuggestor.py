from django.test import TestCase
from devilry.utils import nodenamesuggestor


class TestNameSuggestion(TestCase):
    def test_number_no_number(self):
        self.assertEqual(nodenamesuggestor.Suggest(long_name='Test', short_name='test').number, None)

    def test_number_not_the_same_number(self):
        self.assertEqual(nodenamesuggestor.Suggest(long_name='Test1', short_name='test2').number, None)

    def test_number_number_in_the_middle(self):
        self.assertEqual(
            nodenamesuggestor.Suggest(long_name='Test 1 assignment', short_name='test1assignment').number,
            None)

    def test_number_suffixed_with_number(self):
        self.assertEqual(nodenamesuggestor.Suggest(long_name='Test1', short_name='test1').number, 1)

    def test_number_suffixed_with_number_zero(self):
        # Ensure we do not have any ``if not number``, which would
        # evaluate to no match for ``0``.
        self.assertEqual(nodenamesuggestor.Suggest(long_name='Test0', short_name='test0').number, 0)

    def test_number_suffixed_multicharacter_number(self):
        self.assertEqual(nodenamesuggestor.Suggest(long_name='Test2001', short_name='test2001').number, 2001)

    def test_create_names_from_number_no_number(self):
        namesuggestion = nodenamesuggestor.Suggest(long_name='Test', short_name='test')
        self.assertEqual(namesuggestion.suggested_long_name, '')
        self.assertEqual(namesuggestion.suggested_short_name, '')

    def test_create_names_from_number(self):
        namesuggestion = nodenamesuggestor.Suggest(long_name='Test 1', short_name='test1')
        self.assertEqual(namesuggestion.suggested_long_name, 'Test 2')
        self.assertEqual(namesuggestion.suggested_short_name, 'test2')

    def test_has_suggestion_false(self):
        namesuggestion = nodenamesuggestor.Suggest(long_name='Test', short_name='test')
        self.assertFalse(namesuggestion.has_suggestion())

    def test_has_suggestion_true(self):
        namesuggestion = nodenamesuggestor.Suggest(long_name='Test 1', short_name='test1')
        self.assertTrue(namesuggestion.has_suggestion())
