from django.test import TestCase
from devilry.devilry_group.templatetags.custom_filter import devilry_truncatefileextension


class TestDevilryGroupTemplateTags(TestCase):
    def setUp(self):
        self.file = 'DesignDocumentForDUCK1100_DeweyDuck.pdf'

    def test_truncatefileextension_truncated(self):
        truncated_filename = devilry_truncatefileextension(self.file, 10)
        self.assertEqual('DesignDocu...pdf', truncated_filename)

    def test_truncatefileextension_not_truncated(self):
        truncated_filename = devilry_truncatefileextension(self.file, 100)
        self.assertEqual('DesignDocumentForDUCK1100_DeweyDuck.pdf', truncated_filename)