from urllib import urlencode
from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry.project.develop.testhelpers.soupselect import cssFind
from devilry.project.develop.testhelpers.soupselect import cssGet
from devilry.project.develop.testhelpers.soupselect import cssExists



class TestCloseGroupsView(TestCase):
    def setUp(self):
        self.examiner1 = UserBuilder('examiner1').user
        self.assignment1builder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1', long_name='Assignment One')
        self.url = reverse('devilry_examiner_close_groups', kwargs={
            'assignmentid': self.assignment1builder.assignment.id})

    def _getas(self, user, *args, **kwargs):
        self.client.login(username=user.username, password='test')
        return self.client.get(self.url, *args, **kwargs)

    def _postas(self, user, *args, **kwargs):
        self.client.login(username=user.username, password='test')
        return self.client.post(self.url, *args, **kwargs)


    ##############################
    # Security checks
    ##############################

    def test_post_200_when_examiner(self):
        group1 = self.assignment1builder\
            .add_group(examiners=[self.examiner1]).group
        response = self._postas(self.examiner1, {
            'group_ids': [group1.id]
        })
        self.assertEquals(response.status_code, 200)

    def test_post_404_when_not_examiner(self):
        group1 = self.assignment1builder\
            .add_group().group # Not adding any examiners.
        response = self._postas(self.examiner1, {
            'group_ids': [group1.id]
        })
        self.assertEquals(response.status_code, 404)

    def test_get_405(self):
        response = self._getas(self.examiner1)
        self.assertEquals(response.status_code, 405)


    #######################################
    # Initial rendering
    #######################################

    def test_render(self):
        group1 = self.assignment1builder\
            .add_group(examiners=[self.examiner1]).group
        response = self._postas(self.examiner1, {
            'group_ids': [group1.id]
        })
        self.assertEquals(response.status_code, 200)
        html = response.content
        self.assertEquals(cssGet(html, '.page-header h1').text.strip(),
            'Close groups')
        self.assertEquals(cssGet(html, '.page-header .subheader').text.strip(),
            "Assignment One &mdash; duck1010, active")
        self.assertTrue(cssExists(html, 'input[name=success_url]'))
        self.assertTrue(cssExists(html, 'input[name=cancel_url]'))
        self.assertTrue(cssExists(html, 'input[name=group_ids]'))
        self.assertTrue(cssExists(html, '[name=close_groups_confirm_form]'))
        self.assertTrue(cssExists(html, '[name=submit_cancel]'))


    ##########################################
    # Form handling
    ##########################################

    def test_post_single(self):
        group1builder = self.assignment1builder\
            .add_group(examiners=[self.examiner1])
        self.assertTrue(group1builder.group.is_open)
        response = self._postas(self.examiner1, {
            'group_ids': [group1builder.group.id],
            'close_groups_confirm_form': 'i18nlabel'
        })
        self.assertEquals(response.status_code, 302)
        group1builder.reload_from_db()
        self.assertFalse(group1builder.group.is_open)
        self.assertEquals(group1builder.group.delivery_status, 'closed-without-feedback')

    def test_post_multiple(self):
        group1builder = self.assignment1builder\
            .add_group(examiners=[self.examiner1])
        group2builder = self.assignment1builder\
            .add_group(examiners=[self.examiner1])
        response = self._postas(self.examiner1, {
            'group_ids': [group1builder.group.id, group2builder.group.id],
            'close_groups_confirm_form': 'i18nlabel'
        })
        self.assertEquals(response.status_code, 302)

        group1builder.reload_from_db()
        group2builder.reload_from_db()
        self.assertFalse(group1builder.group.is_open)
        self.assertFalse(group2builder.group.is_open)
        self.assertEquals(group1builder.group.delivery_status, 'closed-without-feedback')
        self.assertEquals(group2builder.group.delivery_status, 'closed-without-feedback')



    #
    #
    # Cancel and success urls
    #
    #

    def test_custom_success_url(self):
        group1builder = self.assignment1builder\
            .add_group(examiners=[self.examiner1])
        response = self._postas(self.examiner1, {
            'group_ids': [group1builder.group.id],
            'success_url': '/my/test',
            'close_groups_confirm_form': 'i18nlabel'
        })
        self.assertEquals(response.status_code, 302)
        self.assertTrue(response['Location'].endswith('/my/test'))

    def test_custom_cancel_url(self):
        group1builder = self.assignment1builder\
            .add_group(examiners=[self.examiner1])
        response = self._postas(self.examiner1, {
            'group_ids': [group1builder.group.id],
            'cancel_url': '/my/test',
            'submit_cancel': 'i18nlabel'
        })
        self.assertEquals(response.status_code, 302)
        self.assertTrue(response['Location'].endswith('/my/test'))


    def test_default_success_url(self):
        group1builder = self.assignment1builder\
            .add_group(examiners=[self.examiner1])
        response = self._postas(self.examiner1, {
            'group_ids': [group1builder.group.id],
            'close_groups_confirm_form': 'i18nlabel'
        })
        self.assertEquals(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(
            reverse('devilry_examiner_allgroupsoverview', kwargs={'assignmentid': self.assignment1builder.assignment.id})))

    def test_default_cancel_url(self):
        group1builder = self.assignment1builder\
            .add_group(examiners=[self.examiner1])
        response = self._postas(self.examiner1, {
            'group_ids': [group1builder.group.id],
            'submit_cancel': 'i18nlabel'
        })
        self.assertEquals(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(
            reverse('devilry_examiner_allgroupsoverview', kwargs={'assignmentid': self.assignment1builder.assignment.id})))
