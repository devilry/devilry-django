import json

from django.test import TestCase
from cradmin_legacy import cradmin_testhelpers
from model_bakery import baker

from devilry.apps.core.models import Assignment
from devilry.apps.core.models import PointToGradeMap
from devilry.devilry_admin.views.assignment import gradingconfiguration


class TestAssignmentGradingConfigurationUpdateView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = gradingconfiguration.AssignmentGradingConfigurationUpdateView

    def test_get_title(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=assignment, viewkwargs={'pk': assignment.id})
        self.assertEqual(mockresponse.selector.one('title').alltext_normalized,
                          'Edit grading configuration')

    def test_get_h1(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=assignment, viewkwargs={'pk': assignment.id})
        self.assertEqual(mockresponse.selector.one('h1').alltext_normalized,
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
        assignment = baker.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=assignment, viewkwargs={'pk': assignment.id})
        self.assertEqual(
            mockresponse.selector.count('input[name="grading_system_plugin_id"]'),
            2)

    def test_get_grading_system_plugin_id_labels(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=assignment, viewkwargs={'pk': assignment.id})
        labels = self.__get_radio_labels(mockresponse.selector, 'div_id_grading_system_plugin_id')
        self.assertEqual(len(labels), 2)
        self.assertEqual(labels[0], 'PASSED/FAILED. The examiner selects passed or failed.')
        self.assertEqual(labels[1], 'POINTS. The examiner types in the number of points to award the '
                                    'student(s) for this assignment.')

    def test_get_grading_system_plugin_id_values(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=assignment, viewkwargs={'pk': assignment.id})
        values = self.__get_radio_values(mockresponse.selector, 'div_id_grading_system_plugin_id')
        self.assertEqual(len(values), 2)
        self.assertEqual(values[0], 'devilry_gradingsystemplugin_approved')
        self.assertEqual(values[1], 'devilry_gradingsystemplugin_points')

    def test_get_points_to_grade_mapper_choices_sanity(self):
        assignment = baker.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=assignment, viewkwargs={'pk': assignment.id})
        self.assertEqual(
            mockresponse.selector.count('input[name="points_to_grade_mapper"]'),
            3)

    def test_get_points_to_grade_mapper_labels(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=assignment, viewkwargs={'pk': assignment.id})
        labels = self.__get_radio_labels(mockresponse.selector, 'div_id_points_to_grade_mapper')
        self.assertEqual(len(labels), 3)
        self.assertEqual(labels[0], 'Passed or failed')
        self.assertEqual(labels[1], 'Points')
        self.assertEqual(labels[2], 'Lookup in a table defined by you (A-F, and other grading systems)')

    def test_get_points_to_grade_mapper_values(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=assignment, viewkwargs={'pk': assignment.id})
        values = self.__get_radio_values(mockresponse.selector, 'div_id_points_to_grade_mapper')
        self.assertEqual(len(values), 3)
        self.assertEqual(values[0], 'passed-failed')
        self.assertEqual(values[1], 'raw-points')
        self.assertEqual(values[2], 'custom-table')

    def test_get_point_to_grade_map_json_none(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=assignment, viewkwargs={'pk': assignment.id})
        self.assertEqual(
            mockresponse.selector.one('input[name="point_to_grade_map_json"]').alltext_normalized,
            '')

    def test_get_point_to_grade_map_json_has_value(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                       max_points=100)
        point_to_grade_map = baker.make('core.PointToGradeMap', assignment=assignment)
        point_to_grade_map.create_map((0, 'F'), (80, 'A'))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=assignment, viewkwargs={'pk': assignment.id})
        self.assertEqual(
            mockresponse.selector.one('input[name="point_to_grade_map_json"]').get('value'),
            json.dumps([(0, 'F'), (80, 'A')]))

    def __make_postdata(self, **data):
        data.setdefault('grading_system_plugin_id', Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)
        data.setdefault('points_to_grade_mapper', Assignment.POINTS_TO_GRADE_MAPPER_PASSED_FAILED)
        data.setdefault('passing_grade_min_points', 1)
        data.setdefault('max_points', 1)
        data.setdefault('point_to_grade_map_json', '')
        return data

    def test_post_max_points_smaller_than_passing_grade_min_points(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=assignment,
            viewkwargs={'pk': assignment.id},
            requestkwargs={'data': self.__make_postdata(
                passing_grade_min_points=30,
                max_points=20,
                points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS)
            })
        self.assertFalse(PointToGradeMap.objects.filter(assignment=assignment).exists())
        self.assertIn(
            str(gradingconfiguration.GradingConfigurationForm.error_messages[
                    'max_points_larger_than_passing_grade_min_points']),
            mockresponse.selector.one('#div_id_max_points.has-error').alltext_normalized)

    def test_post_ok_sanity(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
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

    def test_post_point_to_grade_map_json_over_max_points(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=assignment,
            viewkwargs={'pk': assignment.id},
            requestkwargs={'data': self.__make_postdata(
                max_points=20,
                points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE,
                point_to_grade_map_json=json.dumps([
                    [0, 'F'],
                    [80, 'A']
                ]))
            })
        self.assertFalse(PointToGradeMap.objects.filter(assignment=assignment).exists())
        self.assertIn(
            str(gradingconfiguration.GradingConfigurationForm.error_messages[
                    'max_points_too_small_for_point_to_grade_map']),
            mockresponse.selector.one('#div_id_max_points.has-error').alltext_normalized)

    def test_post_point_to_grade_map_json_empty(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=assignment,
            viewkwargs={'pk': assignment.id},
            requestkwargs={'data': self.__make_postdata(
                max_points=20,
                points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE,
                point_to_grade_map_json='')
            })
        self.assertFalse(PointToGradeMap.objects.filter(assignment=assignment).exists())
        self.assertIn(
            str(gradingconfiguration.GradingConfigurationForm.error_messages[
                    'point_to_grade_map_json_invalid_format']),
            mockresponse.selector.one('form .alert-danger').alltext_normalized)

    def test_post_point_to_grade_map_json_too_few_rows(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=assignment,
            viewkwargs={'pk': assignment.id},
            requestkwargs={'data': self.__make_postdata(
                max_points=20,
                points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE,
                point_to_grade_map_json=json.dumps([
                    [0, 'F']
                ]))
            })
        self.assertFalse(PointToGradeMap.objects.filter(assignment=assignment).exists())
        self.assertIn(
            str(gradingconfiguration.GradingConfigurationForm.error_messages[
                    'point_to_grade_map_json_invalid_format']),
            mockresponse.selector.one('form .alert-danger').alltext_normalized)

    def test_post_point_to_grade_map_json_sanity(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        self.mock_http302_postrequest(
            cradmin_role=assignment,
            viewkwargs={'pk': assignment.id},
            requestkwargs={'data': self.__make_postdata(
                max_points=100,
                points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE,
                point_to_grade_map_json=json.dumps([
                    [0, 'F'],
                    [80, 'A']
                ]))
            })
        self.assertTrue(PointToGradeMap.objects.filter(assignment=assignment).exists())
        assignment = Assignment.objects.filter(id=assignment.id)\
            .prefetch_point_to_grade_map()\
            .get()
        self.assertEqual(assignment.points_to_grade_mapper,
                         Assignment.POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE)
        point_to_grade_map_dict = dict(assignment.prefetched_point_to_grade_map.as_choices())
        self.assertEqual(len(point_to_grade_map_dict), 2)
        self.assertEqual(point_to_grade_map_dict[0], 'F')
        self.assertEqual(point_to_grade_map_dict[80], 'A')
        self.assertFalse(assignment.pointtogrademap.invalid)
