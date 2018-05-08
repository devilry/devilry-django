from django.test import TestCase
from devilry.devilry_group.templatetags.devilry_group_tags import devilry_truncatefileextension
from devilry.devilry_group.templatetags.devilry_group_tags import devilry_verbosenumber


class TestDevilryGroupTemplateTags(TestCase):
    def setUp(self):
        self.filename = 'Delivery.pdf'
        self.filename_length = len('Delivery.pdf')

    def test_truncatefileextension_truncated(self):
        truncated_filename = devilry_truncatefileextension(self.filename, 10)
        self.assertEqual('Deli...pdf', truncated_filename)

    def test_truncatefileextension_not_truncated(self):
        truncated_filename = devilry_truncatefileextension(self.filename, 20)
        self.assertEqual('Delivery.pdf', truncated_filename)

    def test_truncatefileextension_same_as_max(self):
        truncated_filename = devilry_truncatefileextension(self.filename, self.filename_length)
        self.assertEqual('Delivery.pdf', truncated_filename)

    def test_truncatefileextension_one_shorter_than_max(self):
        truncated_filename = devilry_truncatefileextension(self.filename, self.filename_length+1)
        self.assertEqual('Delivery.pdf', truncated_filename)

    def test_truncatefileextension_one_longer_than_max(self):
        truncated_filename = devilry_truncatefileextension(self.filename, self.filename_length-1)
        self.assertEqual('Deliv...pdf', truncated_filename)

    def test_truncatefileextension_shorter_than_min_length(self):
        truncated_filename = devilry_truncatefileextension('De.html', 8)
        self.assertEqual('De.html', truncated_filename)

    def test_truncatefileextension_three_letters_from_value(self):
        truncated_filename = devilry_truncatefileextension('Deliv.pdf', 8)
        self.assertEqual('Del...pdf', truncated_filename)

    def test_truncatefileextension_no_extension(self):
        truncated_filename = devilry_truncatefileextension('DeliveryFile', 8)
        self.assertEqual('Deliv...', truncated_filename)

    def test_min_truncation(self):
        truncated_filename = devilry_truncatefileextension('DesignDocument.pdf', 0)
        self.assertEqual('Des...pdf', truncated_filename)
    
    def test_verbosenumber_1_to_10(self):
        self.assertEqual('first', devilry_verbosenumber('', 1))
        self.assertEqual('second', devilry_verbosenumber('', 2))
        self.assertEqual('third', devilry_verbosenumber('', 3))
        self.assertEqual('fourth', devilry_verbosenumber('', 4))
        self.assertEqual('fifth', devilry_verbosenumber('', 5))
        self.assertEqual('sixth', devilry_verbosenumber('', 6))
        self.assertEqual('seventh', devilry_verbosenumber('', 7))
        self.assertEqual('eighth', devilry_verbosenumber('', 8))
        self.assertEqual('ninth', devilry_verbosenumber('', 9))
        self.assertEqual('tenth', devilry_verbosenumber('', 10))

    def test_numbers_over_ten_added_as_number_dottet(self):
        self.assertEqual('11.', devilry_verbosenumber('', 11))
        self.assertEqual('25.', devilry_verbosenumber('', 25))
        self.assertEqual('733.', devilry_verbosenumber('', 733))
        self.assertEqual('628353.', devilry_verbosenumber('', 628353))
