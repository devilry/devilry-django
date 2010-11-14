from django.test import TestCase
from django.contrib.auth.models import User

from devilry.core.models import Period
from views import PeriodStatsFilterTable


class PeriodStatsFilterTableTest(TestCase):
    fixtures = ["tests/gradestats/data.json"]

    def test_iter_selected_assignmentcols(self):
        period = Period.objects.get(id=1)
        stud0 = User.objects.get(username="student0")
        p = [(scaled_points, status) for scaled_points, status in
                PeriodStatsFilterTable.iter_selected_assignments(
                    period, stud0, )]
        print p

