from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.project.develop.testhelpers.soupselect import cssFind
from devilry.project.develop.testhelpers.soupselect import cssGet
from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder


class TestDashboardView(TestCase):
    def setUp(self):
        self.examiner1 = UserBuilder('examiner1').user

    def _getas(self, username, *args, **kwargs):
        self.client.login(username=username, password='test')
        return self.client.get(reverse('devilry_examiner_dashboard'), *args, **kwargs)

    def test_list_single(self):
        currentperiodbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()
        week1builder = currentperiodbuilder.add_assignment('week1', 'Week 1')
        week1builder.add_group().add_examiners(self.examiner1)
        response = self._getas('examiner1')
        self.assertEquals(response.status_code, 200)
        html = response.content
        self.assertEquals(len(cssFind(html, '.active-assignment-listing-item')), 1)
        linktag = cssGet(html, 'a.assignment-duck1010.active.week1')
        self.assertEquals(linktag.text.strip(), 'duck1010.active - Week 1')
        self.assertEquals(linktag['href'], '/devilry_examiner/allgroupsoverview/{}/waiting_for_feedback_or_all'.format(week1builder.assignment.id))

    def test_list_ordering(self):
        currentperiodbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()
        for short_name in ('week1', 'week2', 'week3'):
            currentperiodbuilder.add_assignment(short_name)\
                .add_group().add_examiners(self.examiner1)
        response = self._getas('examiner1')
        self.assertEquals(response.status_code, 200)
        html = response.content
        self.assertEquals(len(cssFind(html, '.active-assignment-listing-item')), 3)
        names = [name.text.strip() for name in cssFind(html, '.assignmentname')]
        self.assertEquals(names, [
            'duck1010.active - week3',
            'duck1010.active - week2',
            'duck1010.active - week1'])
