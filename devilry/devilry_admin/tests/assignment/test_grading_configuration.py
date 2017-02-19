from django.test import TestCase
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core.models import Assignment
from devilry.devilry_admin.views.assignment import gradingconfiguration


class TestAssignmentGradingConfigurationUpdateView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = gradingconfiguration.AssignmentGradingConfigurationUpdateView

    def test_get_title(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=assignment, viewkwargs={'pk': assignment.id})
        self.assertEquals(mockresponse.selector.one('title').alltext_normalized,
                          'Edit grading configuration')

    def test_get_h1(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=assignment, viewkwargs={'pk': assignment.id})
        self.assertEquals(mockresponse.selector.one('h1').alltext_normalized,
                          'Edit grading configuration')

    def __get_radio_labels(self, selector, wrapper_element_id):
        return [
            element.alltext_normalized
            for element in selector.list('#{} .radio label'.format(wrapper_element_id))]

    def __get_radio_values(self, selector, wrapper_element_id):
        return [
            element.get('value')
            for element in selector.list('#{} input[type="radio"]'.format(wrapper_element_id))]

    def test_get_grading_system_plugin_id_choices_sanity(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=assignment, viewkwargs={'pk': assignment.id})
        self.assertEqual(
            mockresponse.selector.count('input[name="grading_system_plugin_id"]'),
            2)

    def test_get_grading_system_plugin_id_labels(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=assignment, viewkwargs={'pk': assignment.id})
        labels = self.__get_radio_labels(mockresponse.selector, 'div_id_grading_system_plugin_id')
        self.assertEqual(len(labels), 2)
        self.assertEqual(labels[0], 'PASSED/FAILED. The examiner selects passed or failed.')
        self.assertEqual(labels[1], 'POINTS. The examiner types in the number of points to award the '
                                    'student(s) for this assignment.')

    def test_get_grading_system_plugin_id_values(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=assignment, viewkwargs={'pk': assignment.id})
        values = self.__get_radio_values(mockresponse.selector, 'div_id_grading_system_plugin_id')
        self.assertEqual(len(values), 2)
        self.assertEqual(values[0], 'devilry_gradingsystemplugin_approved')
        self.assertEqual(values[1], 'devilry_gradingsystemplugin_points')

    def test_get_points_to_grade_mapper_choices_sanity(self):
        assignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=assignment, viewkwargs={'pk': assignment.id})
        self.assertEqual(
            mockresponse.selector.count('input[name="points_to_grade_mapper"]'),
            3)

    def test_get_points_to_grade_mapper_labels(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=assignment, viewkwargs={'pk': assignment.id})
        labels = self.__get_radio_labels(mockresponse.selector, 'div_id_points_to_grade_mapper')
        self.assertEqual(len(labels), 3)
        self.assertEqual(labels[0], 'As passed or failed')
        self.assertEqual(labels[1], 'As points')
        self.assertEqual(labels[2], 'As a text looked up in a custom table')

    def test_get_points_to_grade_mapper_values(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=assignment, viewkwargs={'pk': assignment.id})
        values = self.__get_radio_values(mockresponse.selector, 'div_id_points_to_grade_mapper')
        self.assertEqual(len(values), 3)
        self.assertEqual(values[0], 'passed-failed')
        self.assertEqual(values[1], 'raw-points')
        self.assertEqual(values[2], 'custom-table')

    def __make_postdata(self, **data):
        data.setdefault('grading_system_plugin_id', Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        data.setdefault('points_to_grade_mapper', Assignment.POINTS_TO_GRADE_MAPPER_PASSED_FAILED)
        data.setdefault('passing_grade_min_points', 1)
        data.setdefault('max_points', 1)
        data.setdefault('custom_table_value_list_json', '')
        return data

    def test_post_sanity(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        self.mock_http302_postrequest(
            cradmin_role=assignment,
            viewkwargs={'pk': assignment.id},
            requestkwargs={'data': self.__make_postdata(
                grading_system_plugin_id=Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS,
                points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS,
                passing_grade_min_points=10,
                max_points=100)
            })
        assignment.refresh_from_db()
        self.assertEqual(assignment.grading_system_plugin_id,
                         Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS)
        self.assertEqual(assignment.points_to_grade_mapper,
                         Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS)
        self.assertEqual(assignment.passing_grade_min_points, 10)
        self.assertEqual(assignment.max_points, 100)
