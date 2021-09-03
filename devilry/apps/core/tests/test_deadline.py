from django import test
from model_bakery import baker

from devilry.utils.datetimeutils import default_timezone_datetime


class TestDeadline(test.TestCase):

    def test_clean_sets_correct_second(self):
        deadline = baker.make('core.Deadline', deadline=default_timezone_datetime(2021, 8, 23, 10, 59, 00))

        self.assertEqual(deadline.deadline.second, 00)
        deadline._clean_deadline()
        deadline.save()
        deadline.refresh_from_db()
        self.assertEqual(deadline.deadline.second, 59)
