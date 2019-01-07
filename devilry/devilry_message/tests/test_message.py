from django import test
from django.conf import settings

from model_mommy import mommy


class TestMessage(test.TestCase):
    def __make_email_for_user(self, user, email):
        return mommy.make('devilry_account.UserEmail', user=user, email=email)

    def test_validate_user_ids_not_in_virtual_message_receivers(self):
        message = mommy.make('devilry_message.Message', virtual_message_receivers={'test': 'lol'},
                             message_type=['email'])
        with self.assertRaisesMessage(ValueError, 'Missing \'user_ids\' in \'virtual_message_receivers\''):
            message.validate_virtual_message_receivers()

    def test_validate_virtual_message_receivers_not_list(self):
        message = mommy.make('devilry_message.Message', virtual_message_receivers={'user_ids': {}},
                             message_type=['email'])
        with self.assertRaisesMessage(ValueError, '\'user_ids\' in \'virtual_message_receivers\' is not a list'):
            message.validate_virtual_message_receivers()

    def test_validate_virtual_message_receivers_empty(self):
        message = mommy.make('devilry_message.Message', virtual_message_receivers={'user_ids': []},
                             message_type=['email'])
        with self.assertRaisesMessage(ValueError, '\'user_ids\' in \'virtual_message_receivers\' is empty'):
            message.validate_virtual_message_receivers()

    def test_validate_virtual_message_receivers_contains_non_integer_values(self):
        message = mommy.make('devilry_message.Message', virtual_message_receivers={'user_ids': [1, '23']},
                             message_type=['email'])
        with self.assertRaisesMessage(ValueError, '\'virtual_message_receivers["user_ids"]\' contains a non-integer value.: 23'):
            message.validate_virtual_message_receivers()

