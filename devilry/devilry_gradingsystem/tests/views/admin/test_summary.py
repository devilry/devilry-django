import unittest
from mock import patch
from django.urls import reverse
from django.test import TestCase

from devilry.project.develop.testhelpers.corebuilder import SubjectBuilder
from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry.project.develop.testhelpers.soupselect import cssGet
from devilry.project.develop.testhelpers.soupselect import cssFind
from devilry.devilry_gradingsystem.pluginregistry import GradingSystemPluginRegistry

from devilry.devilry_gradingsystem.models import FeedbackDraft
from .base import AdminViewTestMixin
# from .base import MockApprovedPluginApi
from .base import MockPointsPluginApi


@unittest.skip('devilry_gradingsystem will most likely be replaced in 3.0')
class TestSummaryView(TestCase, AdminViewTestMixin):

    def setUp(self):
        self.admin1 = UserBuilder('admin1').user
        self.assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_admins(self.admin1)
        self.url = reverse('devilry_gradingsystem_admin_summary', kwargs={
            'assignmentid': self.assignmentbuilder.assignment.id,
        })

    def test_render(self):
        myregistry = GradingSystemPluginRegistry()
        myregistry.add(MockPointsPluginApi)
        self.assignmentbuilder.update(grading_system_plugin_id=MockPointsPluginApi.id)
        with patch('devilry.apps.core.models.assignment.gradingsystempluginregistry', myregistry):
            response = self.get_as(self.admin1)
            self.assertEqual(response.status_code, 200)
            html = response.content
            self.assertEqual(cssGet(html, '.page-header h1').text.strip(),
                'Grading system')

    def test_no_grading_system_configured(self):
        myregistry = GradingSystemPluginRegistry()
        self.assignmentbuilder.update(
            grading_system_plugin_id=None
        )
        with patch('devilry.apps.core.models.assignment.gradingsystempluginregistry', myregistry):
            response = self.get_as(self.admin1)
            self.assertEqual(response.status_code, 200)
            html = response.content
            self.assertIn('No grading system configured.', html)

    def test_invalid_grading_setup(self):
        myregistry = GradingSystemPluginRegistry()
        myregistry.add(MockPointsPluginApi)
        with patch('devilry.apps.core.models.assignment.gradingsystempluginregistry', myregistry):
            self.assignmentbuilder.update(
                grading_system_plugin_id=MockPointsPluginApi.id,
                max_points=None
            )
            response = self.get_as(self.admin1)
            self.assertEqual(response.status_code, 200)
            html = response.content
            self.assertIn('The grading system is not configured correctly.', html)

    def test_no_drafts_or_feedbacks_message(self):
        myregistry = GradingSystemPluginRegistry()
        with patch('devilry.apps.core.models.assignment.gradingsystempluginregistry', myregistry):
            response = self.get_as(self.admin1)
            self.assertEqual(response.status_code, 200)
            html = response.content
            self.assertIn('You can safely reconfigure the grading system for this assignment.', html)

    def test_has_feedbackdrafts_message(self):
        delivery = self.assignmentbuilder\
            .add_group()\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1).delivery
        examiner1 = UserBuilder('examiner1').user
        FeedbackDraft.objects.create(
            points=40,
            delivery=delivery,
            saved_by=examiner1,
            feedbacktext_html='This is a test.'
        )
        myregistry = GradingSystemPluginRegistry()
        with patch('devilry.apps.core.models.assignment.gradingsystempluginregistry', myregistry):
            response = self.get_as(self.admin1)
            self.assertEqual(response.status_code, 200)
            html = response.content
            self.assertIn('You can reconfigure the grading system for this assignment, but be careful, at least one examiner has saved a feedback draft.', html)

    def test_has_staticfeedbacks_warning(self):
        examiner1 = UserBuilder('examiner1').user
        delivery = self.assignmentbuilder\
            .add_group()\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)\
            .add_passed_feedback(saved_by=examiner1)
        myregistry = GradingSystemPluginRegistry()
        with patch('devilry.apps.core.models.assignment.gradingsystempluginregistry', myregistry):
            response = self.get_as(self.admin1)
            self.assertEqual(response.status_code, 200)
            html = response.content
            self.assertIn('You SHOULD NOT reconfigure the grading system for this assignment.', html)


@unittest.skip('devilry_gradingsystem will most likely be replaced in 3.0')
class TestSummaryViewBreadcrumb(TestCase, AdminViewTestMixin):

    def setUp(self):
        self.admin1 = UserBuilder('admin1').user
        self.subjectbuilder = SubjectBuilder.quickadd_ducku_duck1010()
        self.periodbuilder = self.subjectbuilder.add_6month_active_period()
        self.assignmentbuilder = self.periodbuilder.add_assignment('myassignment')
        self.url = reverse('devilry_gradingsystem_admin_summary', kwargs={
            'assignmentid': self.assignmentbuilder.assignment.id,
        })

    def test_subjectadmin(self):
        self.subjectbuilder.add_admins(self.admin1)
        response = self.get_as(self.admin1)
        html = response.content
        breadcrumb = cssFind(html, 'ol.breadcrumb li')
        self.assertEqual(len(breadcrumb), 5)
        self.assertEqual(breadcrumb[0].text, 'Subject administrator')
        self.assertEqual(breadcrumb[1].text, 'duck1010')
        self.assertEqual(breadcrumb[2].text, 'active')
        self.assertEqual(breadcrumb[3].text, 'myassignment')
        self.assertEqual(breadcrumb[4].text, 'Grading system')

    def test_periodadmin(self):
        self.periodbuilder.add_admins(self.admin1)
        response = self.get_as(self.admin1)
        html = response.content
        breadcrumb = cssFind(html, 'ol.breadcrumb li')
        self.assertEqual(len(breadcrumb), 4)
        self.assertEqual(breadcrumb[0].text, 'Subject administrator')
        self.assertEqual(breadcrumb[1].text, 'duck1010.active')
        self.assertEqual(breadcrumb[2].text, 'myassignment')
        self.assertEqual(breadcrumb[3].text, 'Grading system')

    def test_assignmentadmin(self):
        self.assignmentbuilder.add_admins(self.admin1)
        response = self.get_as(self.admin1)
        html = response.content
        breadcrumb = cssFind(html, 'ol.breadcrumb li')
        self.assertEqual(len(breadcrumb), 3)
        self.assertEqual(breadcrumb[0].text, 'Subject administrator')
        self.assertEqual(breadcrumb[1].text, 'duck1010.active.myassignment')
        self.assertEqual(breadcrumb[2].text, 'Grading system')
