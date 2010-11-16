from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.utils.simplejson import JSONDecoder

from devilry.core.models import Period
from views import PeriodStatsFilterTable


class PeriodStatsFilterTableTest(TestCase):
    fixtures = ["tests/gradestats/data.json"]

    def test_iter_selected_assignmentcols(self):
        period = Period.objects.get(id=1)
        stud0 = User.objects.get(username="student0")

        def as_list(user, visible_assignments_in_period):
            return [x for x in
                PeriodStatsFilterTable.iter_selected_assignments(
                    period, user, visible_assignments_in_period)]

        periods = period.assignments.all().order_by("publishing_time")
        allvisible = as_list(stud0, periods)
        self.assertEquals(len(allvisible), 7)
        self.assertEquals(allvisible[0], (14.0, True, 3),
                msg="week1 is incorrect")
        self.assertEquals(allvisible[4], (None, None, None),
                msg="proj1 is incorrect")
        self.assertEquals(allvisible[5], (0.0, False, 0),
                msg="week5 is incorrect")

        somevisible = as_list(stud0, periods.filter(
            short_name__in=["week1", "proj1", "week5"]))
        self.assertEquals(len(somevisible), 3)
        self.assertEquals(somevisible[0], (14.0, True, 3),
                msg="week1 is incorrect")
        self.assertEquals(somevisible[1], (None, None, None),
                msg="proj1 is incorrect")
        self.assertEquals(somevisible[2], (0.0, False, 0),
                msg="week5 is incorrect")

        nonevisible = as_list(stud0, periods.none())
        self.assertEquals(len(nonevisible), 0)


    def test_periodstats(self):
        url = reverse("devilry-gradestats-periodstats", args=["1"])
        c = Client()

        c.login(username="student0", password="test")
        self.assertEquals(c.get(url).content.strip(), "Forbidden")

        c.login(username="grandma", password="test")
        r = c.get(url)
        self.assertTrue("duck1100 - Spring year zero" in r.content)

    def test_periodstats_json(self):
        url = reverse("devilry-gradestats-periodstats_json", args=["1"])
        c = Client()

        c.login(username="student0", password="test")
        self.assertEquals(c.get(url).content.strip(), "Forbidden")

        c.login(username="grandma", password="test")
        r = c.get(url)
        json = JSONDecoder().decode(r.content)
        self.assertTrue("20 of 20" in json["statusmsg"])
        self.assertEquals(len(json["data"]), 10)
        self.assertEquals([x['id'] for x in json["active_columns"]],
                ['username', 'sumperiod', 'sumvisible', '1', '2', '3', '4',
                    '6', '5', '7'])

    def test_admin_userstats(self):
        url = reverse("devilry-gradestats-admin_userstats", args=["1",
            "student0"])
        c = Client()

        c.login(username="student0", password="test")
        self.assertEquals(c.get(url).content.strip(), "Forbidden")

        c.login(username="grandma", password="test")
        r = c.get(url)
        self.assertTrue("Statistics for student0 in duck1100.h01" in r.content)
        self.assertContains(r, "No deliveries", 1)
        self.assertContains(r, "The one and only week", 5)
        self.assertTemplateUsed(r,
                'devilry/gradestats/admin-user.django.html')

    def test_userstats(self):
        url = reverse("devilry-gradestats-userstats", args=["1"])
        c = Client()

        c.login(username="student0", password="test")
        r = c.get(url)
        self.assertTrue("Statistics for student0 in duck1100.h01" in r.content)
        self.assertContains(r, "No deliveries", 1)
        self.assertContains(r, "The one and only week", 5)
        self.assertTemplateUsed(r,
                'devilry/gradestats/admin-user.django.html')
