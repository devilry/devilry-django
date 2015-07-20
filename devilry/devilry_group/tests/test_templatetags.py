from django.test import TestCase
from devilry.devilry_group.templatetags.custom_filter import devilry_truncatefileextension


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