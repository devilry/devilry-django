from django import test
from django.test import override_settings
from django.utils import translation

from devilry.utils import setting_utils


class TestHardDeadlineInfoTextSettingUtil(test.TestCase):
    @override_settings(
        DEVILRY_INFO_TEXT_TEST={}
    )
    def test_get_devilry_hard_deadline_info_text_no_default(self):
        with self.assertRaisesMessage(ValueError, "User error: The DEVILRY_INFO_TEXT_TEST must contain a '__default' "
                                                  "info setting. This exists by default and has been wrongly removed "
                                                  "during setup."):
            setting_utils.get_devilry_hard_deadline_info_text(setting_name='DEVILRY_INFO_TEXT_TEST')

    @override_settings(
        DEVILRY_INFO_TEXT_TEST={
            '__default': 'Default info text'
        })
    def test_get_devilry_hard_deadline_info_text_default(self):
        self.assertEqual(
            setting_utils.get_devilry_hard_deadline_info_text(setting_name='DEVILRY_INFO_TEXT_TEST'),
            'Default info text')

    @override_settings(
        DEVILRY_INFO_TEXT_TEST={
            '__default': 'Default info text',
            'en': 'English info text'
        })
    def test_get_devilry_hard_deadline_info_text_english(self):
        translation.activate('en')
        self.assertEqual(
            setting_utils.get_devilry_hard_deadline_info_text(setting_name='DEVILRY_INFO_TEXT_TEST'),
            'English info text'
        )

    @override_settings(
        DEVILRY_INFO_TEXT_TEST={
            '__default': 'Default info text'
        })
    def test_get_devilry_hard_deadline_info_text_default_if_language_code_does_not_exist(self):
        translation.activate('en')
        self.assertEqual(
            setting_utils.get_devilry_hard_deadline_info_text(setting_name='DEVILRY_INFO_TEXT_TEST'),
            'Default info text'
        )
