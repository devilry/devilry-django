# 3rd party imports
from model_bakery import baker

# Django imports
from django import test
from django.core.exceptions import ValidationError

# Devilry imports
from devilry.devilry_qualifiesforexam import models as status_models


class TestStatus(test.TestCase):

    def test_notready_no_message(self):
        test_status = baker.make('devilry_qualifiesforexam.Status', status=status_models.Status.NOTREADY)
        with self.assertRaisesMessage(ValidationError, 'Message can not be empty when status is ``notready``.'):
            test_status.full_clean()

    def test_ready_no_message_and_no_plugin(self):
        test_status = baker.make('devilry_qualifiesforexam.Status', status=status_models.Status.READY)
        with self.assertRaisesMessage(ValidationError, 'A ``message`` is required when no ``plugin`` is specified. '
                                                       'The message should explain why a plugin is not used.'):
            test_status.full_clean()

    def test_notready_no_plugin(self):
        test_status = baker.make('devilry_qualifiesforexam.Status', status=status_models.Status.NOTREADY,
                                 message='No plugin', plugin='some.plugin')
        with self.assertRaisesMessage(ValidationError, '``plugin`` is not allowed when status is ``notready``.'):
            test_status.full_clean()

    def test_get_current_status_no_status_for_period(self):
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        last_status = status_models.Status.objects.get_last_status_in_period(period=testperiod)
        self.assertIsNone(last_status)

    def test_get_current_status(self):
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        baker.make('devilry_qualifiesforexam.Status',
                   period=testperiod,
                   status=status_models.Status.READY,
                   plugin='plugin')
        last_status = baker.make('devilry_qualifiesforexam.Status',
                                 period=testperiod,
                                 status=status_models.Status.READY,
                                 plugin='plugin')
        current_status = status_models.Status.objects.get_last_status_in_period(period=testperiod)
        self.assertEqual(current_status, last_status)

    def test_get_qualified_students(self):
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        teststatus = baker.make('devilry_qualifiesforexam.Status',
                                period=testperiod,
                                status=status_models.Status.READY,
                                plugin='plugin')
        baker.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   status=teststatus,
                   qualifies=True,
                   _quantity=10)
        baker.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   status=teststatus,
                   qualifies=False,
                   _quantity=10)
        self.assertEqual(10, len(teststatus.get_qualified_students()))
