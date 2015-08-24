from django.test import TestCase

from devilry.devilry_admin.tests.common import admins_common_testmixins
from devilry.devilry_admin.views.subject import admins
from devilry.project.develop.testhelpers.corebuilder import UserBuilder2, SubjectBuilder


class TestAdminsListView(TestCase, admins_common_testmixins.AdminsListViewTestMixin):
    builderclass = SubjectBuilder
    viewclass = admins.AdminsListView

    def test_title(self):
        testuser = UserBuilder2().user
        subjectbuilder = SubjectBuilder.make(long_name='DUCK 1010 - Programming')\
            .add_admins(testuser)
        selector = self.mock_http200_getrequest_htmls(role=subjectbuilder.subject,
                                                      user=testuser)
        self.assertEqual(selector.one('title').alltext_normalized,
                         'Administrators for DUCK 1010 - Programming')
