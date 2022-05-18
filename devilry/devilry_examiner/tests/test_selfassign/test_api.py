from datetime import timedelta

from django import test
from django.conf import settings
from django.utils import timezone

from model_bakery import baker

from devilry.apps.core.models import Examiner
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.utils.api import api_test_mixin
from devilry.devilry_group import devilry_group_baker_factories as group_baker
from devilry.devilry_examiner.views.selfassign.api import ExaminerSelfAssignApi


class TestSelfAssignApi(test.TestCase, api_test_mixin.ApiTestMixin):
    apiview_class = ExaminerSelfAssignApi

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()
        self.period = baker.make_recipe('devilry.apps.core.period_active', short_name='thesemester', long_name='The Semester')
        self.examiner_user = baker.make(settings.AUTH_USER_MODEL)
        self.related_examiner = baker.make('core.RelatedExaminer', period=self.period, user=self.examiner_user)

    def __make_group(self, assignment):
        group = baker.make('core.AssignmentGroup', parentnode=assignment)
        relatedstudent = baker.make('core.RelatedStudent', period=assignment.parentnode)
        baker.make('core.Candidate', assignment_group=group, relatedstudent=relatedstudent)
        return group

    def test_user_not_authenticated(self):
        response = self.make_post_request()
        self.assertEqual(response.status_code, 403)
    
    def test_method_get_404(self):
        response = self.make_get_request(
            requestuser=baker.make(settings.AUTH_USER_MODEL)
        )
        self.assertEqual(response.status_code, 404)
    
    def test_missing_group_id_in_post_data(self):
        assignment = baker.make('core.Assignment', examiners_can_self_assign=True, parentnode=self.period)
        group = self.__make_group(assignment=assignment)
        response = self.make_post_request(
            requestuser=self.examiner_user,
            viewkwargs={'period_id': self.period.id},
            data={'action': 'ASSIGN'}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'error': 'Missing "group_id".'
        })

    def test_missing_action_in_post_data(self):
        assignment = baker.make('core.Assignment', examiners_can_self_assign=True, parentnode=self.period)
        group = self.__make_group(assignment=assignment)
        response = self.make_post_request(
            requestuser=self.examiner_user,
            viewkwargs={'period_id': self.period.id},
            data={'group_id': group.id}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'error': 'Missing "action".'
        })
    
    def test_invalid_action_in_post_data(self):
        assignment = baker.make('core.Assignment', examiners_can_self_assign=True, parentnode=self.period)
        group = self.__make_group(assignment=assignment)
        response = self.make_post_request(
            requestuser=self.examiner_user,
            viewkwargs={'period_id': self.period.id},
            data={'group_id': group.id, 'action': 'SOMEACTION'}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'error': 'Unknown action "SOMEACTION".'
        })

    def test_not_ok_user_not_relatedexaminer_for_period(self):
        other_period = baker.make_recipe('devilry.apps.core.period_active')
        other_examiner_user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.RelatedExaminer', period=other_period, user=other_examiner_user)
        assignment = baker.make('core.Assignment', examiners_can_self_assign=True, parentnode=self.period)
        group = self.__make_group(assignment=assignment)
        response = self.make_post_request(
            requestuser=other_examiner_user,
            viewkwargs={'period_id': other_period.id},
            data={'group_id': group.id, 'action': 'ASSIGN'}
        )
        self.assertEqual(response.status_code, 404)

    def test_not_ok_period_not_active_past(self):
        old_period = baker.make_recipe('devilry.apps.core.period_old')
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.RelatedExaminer', period=old_period, user=examiner_user)
        assignment = baker.make('core.Assignment', examiners_can_self_assign=True, parentnode=old_period)
        group = self.__make_group(assignment=assignment)
        response = self.make_post_request(
            requestuser=examiner_user,
            viewkwargs={'period_id': old_period.id},
            data={'group_id': group.id, 'action': 'ASSIGN'}
        )
        self.assertEqual(response.status_code, 404)
    
    def test_not_ok_period_not_active_future(self):
        future_period = baker.make_recipe('devilry.apps.core.period_future')
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.RelatedExaminer', period=future_period, user=examiner_user)
        assignment = baker.make('core.Assignment', examiners_can_self_assign=True, parentnode=future_period)
        group = self.__make_group(assignment=assignment)
        response = self.make_post_request(
            requestuser=examiner_user,
            viewkwargs={'period_id': future_period.id},
            data={'group_id': group.id, 'action': 'ASSIGN'}
        )
        self.assertEqual(response.status_code, 404)

    def test_not_ok_assignment_not_published(self):
        assignment = baker.make('core.Assignment',
            examiners_can_self_assign=True, parentnode=self.period,
            publishing_time=timezone.now() + timedelta(days=1))
        group = self.__make_group(assignment=assignment)
        response = self.make_post_request(
            requestuser=self.examiner_user,
            viewkwargs={'period_id': self.period.id},
            data={'group_id': group.id, 'action': 'ASSIGN'}
        )
        self.assertEqual(response.status_code, 404)

    def test_not_ok_selfassign_not_enabled(self):
        assignment = baker.make('core.Assignment', examiners_can_self_assign=False, parentnode=self.period)
        group = self.__make_group(assignment=assignment)
        response = self.make_post_request(
            requestuser=self.examiner_user,
            viewkwargs={'period_id': self.period.id},
            data={'group_id': group.id, 'action': 'ASSIGN'}
        )
        self.assertEqual(response.status_code, 404)

    def test_not_ok_selfassign_limit_reached(self):
        assignment = baker.make('core.Assignment', examiners_can_self_assign=True, parentnode=self.period)
        group = self.__make_group(assignment=assignment)
        baker.make('core.Examiner', assignmentgroup=group, relatedexaminer=baker.make('core.RelatedExaminer', period=self.period))
        response = self.make_post_request(
            requestuser=self.examiner_user,
            viewkwargs={'period_id': self.period.id},
            data={'group_id': group.id, 'action': 'ASSIGN'}
        )
        self.assertEqual(response.status_code, 404)

    def test_ok_assign_sanity(self):
        assignment = baker.make('core.Assignment', examiners_can_self_assign=True, parentnode=self.period)
        group = self.__make_group(assignment=assignment)
        self.assertFalse(
            Examiner.objects.filter(relatedexaminer=self.related_examiner, assignmentgroup=group).exists()
        )
        response = self.make_post_request(
            requestuser=self.examiner_user,
            viewkwargs={'period_id': self.period.id},
            data={'group_id': group.id, 'action': 'ASSIGN'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            'status': 'assigned'
        })
        self.assertTrue(
            Examiner.objects.filter(relatedexaminer=self.related_examiner, assignmentgroup=group).exists()
        )

    def test_ok_unassign_sanity(self):
        assignment = baker.make('core.Assignment', examiners_can_self_assign=True, parentnode=self.period)
        group = self.__make_group(assignment=assignment)
        baker.make('core.Examiner', assignmentgroup=group, relatedexaminer=self.related_examiner)
        self.assertTrue(
            Examiner.objects.filter(relatedexaminer=self.related_examiner, assignmentgroup=group).exists()
        )
        response = self.make_post_request(
            requestuser=self.examiner_user,
            viewkwargs={'period_id': self.period.id},
            data={'group_id': group.id, 'action': 'UNASSIGN'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            'status': 'unassigned'
        })
        self.assertFalse(
            Examiner.objects.filter(relatedexaminer=self.related_examiner, assignmentgroup=group).exists()
        )
