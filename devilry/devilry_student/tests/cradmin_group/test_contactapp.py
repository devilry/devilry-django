from django.test import TestCase, RequestFactory
from django_cradmin.crinstance import reverse_cradmin_url
import htmls
from devilry.project.develop.testhelpers.corebuilder import UserBuilder, PeriodBuilder


class TestContactApp(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user
        self.factory = RequestFactory()
        self.periodbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()
        self.assignmentbuilder = self.periodbuilder.add_assignment('testassignment')
        self.groupbuilder = self.assignmentbuilder.add_group()
        self.groupbuilder.add_deadline_in_x_weeks(weeks=1)
        self.groupbuilder.add_students(self.testuser)

    def _get_as(self, username):
        self.client.login(username=username, password='test')
        return self.client.get(reverse_cradmin_url(
            'devilry_student_group', 'contact', roleid=self.groupbuilder.group.id))

    def test_no_examiners(self):
        response = self._get_as('testuser')
        selector = htmls.S(response.content)
        self.assertFalse(selector.exists('#devilry_student_group_contact_hasexaminers'))
        self.assertTrue(selector.exists('#devilry_student_group_contact_noexaminers'))

    def test_single_examiner(self):
        self.groupbuilder.add_examiners(UserBuilder('testexaminer').user)
        response = self._get_as('testuser')
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists('#devilry_student_group_contact_hasexaminers'))
        self.assertFalse(selector.exists('#devilry_student_group_contact_noexaminers'))
        self.assertEquals(selector.count('#devilry_student_group_contact_hasexaminers ul li'), 1)

    def test_multiple_examiners(self):
        self.groupbuilder.add_examiners(
            UserBuilder('testexaminer1').user,
            UserBuilder('testexaminer2').user)
        response = self._get_as('testuser')
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists('#devilry_student_group_contact_hasexaminers'))
        self.assertFalse(selector.exists('#devilry_student_group_contact_noexaminers'))
        self.assertEquals(selector.count('#devilry_student_group_contact_hasexaminers ul li'), 2)

    def test_render_examiner_has_fullname(self):
        self.groupbuilder.add_examiners(UserBuilder('testexaminer', full_name='Test Examiner').user)
        response = self._get_as('testuser')
        selector = htmls.S(response.content)
        self.assertEquals(
            selector.one('#devilry_student_group_contact_hasexaminers ul li').alltext_normalized,
            'Test Examiner <testexaminer@example.com>')

    def test_render_examiner_no_fullname(self):
        self.groupbuilder.add_examiners(UserBuilder('testexaminer').user)
        response = self._get_as('testuser')
        selector = htmls.S(response.content)
        self.assertEquals(
            selector.one('#devilry_student_group_contact_hasexaminers ul li').alltext_normalized,
            'testexaminer <testexaminer@example.com>')

    def test_render_examiner_email_href(self):
        self.groupbuilder.add_examiners(UserBuilder('testexaminer').user)
        response = self._get_as('testuser')
        selector = htmls.S(response.content)
        self.assertEquals(
            selector.one('#devilry_student_group_contact_hasexaminers ul li a')['href'],
            'mailto:testexaminer@example.com?subject=duck1010.active.testassignment%20-%20testuser')

    def test_404_if_anonymous_assignment(self):
        self.assignmentbuilder.update(anonymous=True)
        response = self._get_as('testuser')
        self.assertEquals(response.status_code, 404)
