from django.test import TestCase, RequestFactory
import htmls
import mock

from devilry.devilry_student.cradmin_group import deliveriesapp

from devilry.project.develop.testhelpers.corebuilder import UserBuilder, PeriodBuilder


class TestDeliveryListView(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user
        self.factory = RequestFactory()
        self.periodbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()
        self.assignmentbuilder = self.periodbuilder.add_assignment('testassignment')
        self.groupbuilder = self.assignmentbuilder.add_group()

    def _mock_get_request(self):
        request = self.factory.get('/test')
        request.user = self.testuser
        request.cradmin_role = self.groupbuilder.group
        request.session = mock.MagicMock()
        response = deliveriesapp.DeliveryListView.as_view()(request)
        return response

    def test_list_no_deliveries(self):
        response = self._mock_get_request()
        response.render()
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists('#objecttableview-table'))
        self.assertFalse(selector.exists('#objecttableview-table tbody tr'))

    def test_list_render_single_delivery_nofeedback(self):
        self.groupbuilder.add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)
        response = self._mock_get_request()
        response.render()
        selector = htmls.S(response.content)
        self.assertEquals(selector.count('#objecttableview-table tbody tr'), 1)
        self.assertEquals(selector.count('#objecttableview-table tbody tr'), 1)
