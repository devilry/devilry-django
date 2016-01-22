import mock
from django import test
from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core import devilry_core_mommy_factories
from devilry.apps.core.models import AssignmentGroup, Assignment
from devilry.devilry_admin.views.assignment.students import groupdetails
from devilry.devilry_comment.models import Comment
from devilry.devilry_group import devilry_group_mommy_factories
from devilry.devilry_group.models import GroupComment, ImageAnnotationComment


class TestGroupDetailsView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = groupdetails.GroupDetailsView

    def __mockinstance_with_devilryrole(self, devilryrole):
        mockinstance = mock.MagicMock()
        mockinstance.get_devilryrole_for_requestuser.return_value = devilryrole
        return mockinstance

    def test_title(self):
        testgroup = mommy.make('core.AssignmentGroup')
        devilry_core_mommy_factories.candidate(group=testgroup,
                                               fullname='Test User')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup.assignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
            viewkwargs={'pk': testgroup.id})
        self.assertIn(
            'Test User',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testgroup = mommy.make('core.AssignmentGroup')
        devilry_core_mommy_factories.candidate(group=testgroup,
                                               fullname='Test User')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup.assignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
            viewkwargs={'pk': testgroup.id})
        self.assertEqual(
            'Test User',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_title_multiple_candidates(self):
        testgroup = mommy.make('core.AssignmentGroup')
        devilry_core_mommy_factories.candidate(group=testgroup,
                                               fullname='UserB')
        devilry_core_mommy_factories.candidate(group=testgroup,
                                               shortname='usera')
        devilry_core_mommy_factories.candidate(group=testgroup,
                                               fullname='UserC')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup.assignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
            viewkwargs={'pk': testgroup.id})
        self.assertIn(
            'usera, UserB, UserC',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1_multiple_candidates(self):
        testgroup = mommy.make('core.AssignmentGroup')
        devilry_core_mommy_factories.candidate(group=testgroup,
                                               fullname='UserB')
        devilry_core_mommy_factories.candidate(group=testgroup,
                                               shortname='usera')
        devilry_core_mommy_factories.candidate(group=testgroup,
                                               fullname='UserC')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup.assignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
            viewkwargs={'pk': testgroup.id})
        self.assertEqual(
            'usera, UserB, UserC',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_404_fully_anonymous_subjectadmin(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        with self.assertRaises(Http404):
            self.mock_getrequest(
                cradmin_role=testgroup.assignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
                viewkwargs={'pk': testgroup.id})

    def test_not_404_fully_anonymous_departmentadmin(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        self.mock_getrequest(
            cradmin_role=testgroup.assignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'pk': testgroup.id})
