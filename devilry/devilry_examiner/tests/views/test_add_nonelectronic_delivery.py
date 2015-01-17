from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry.project.develop.testhelpers.soupselect import cssGet
from devilry.project.develop.testhelpers.soupselect import cssExists
from devilry.apps.core.models import deliverytypes, Delivery


class TestAddNonElectronicDeliveryView(TestCase):
    def setUp(self):
        self.examiner1 = UserBuilder('examiner1').user
        self.assignment1builder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1', long_name='Assignment One')
        self.url = reverse('devilry_examiner_add_nonelectronic_delivery', kwargs={
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
            'Add non-electronic delivery')
        self.assertEquals(cssGet(html, '.page-header .subheader').text.strip(),
            "Assignment One &mdash; duck1010, active")
        self.assertTrue(cssExists(html, 'input[name=success_url]'))
        self.assertTrue(cssExists(html, 'input[name=cancel_url]'))
        self.assertTrue(cssExists(html, 'input[name=group_ids]'))
        self.assertTrue(cssExists(html, '[name=add_nonelectronic_deliveries_form]'))
        self.assertTrue(cssExists(html, '[name=submit_cancel]'))


    ##########################################
    # Form handling
    ##########################################

    def test_post_single(self):
        group1builder = self.assignment1builder\
            .add_group(examiners=[self.examiner1])
        group1builder.add_deadline_in_x_weeks(weeks=1)
        self.assertTrue(group1builder.group.is_open)
        response = self._postas(self.examiner1, {
            'group_ids': [group1builder.group.id],
            'add_nonelectronic_deliveries_form': 'i18nlabel'
        })
        self.assertEquals(response.status_code, 302)
        group1builder.reload_from_db()
        group1delivery = Delivery.objects.get(deadline__assignment_group=group1builder.group)
        self.assertEquals(group1delivery.delivery_type, deliverytypes.NON_ELECTRONIC)
        self.assertTrue(group1delivery.successful)

    def test_post_multiple(self):
        group1builder = self.assignment1builder\
            .add_group(examiners=[self.examiner1])
        group1builder.add_deadline_in_x_weeks(weeks=1)
        group2builder = self.assignment1builder\
            .add_group(examiners=[self.examiner1])
        group2builder.add_deadline_in_x_weeks(weeks=1)

        response = self._postas(self.examiner1, {
            'group_ids': [group1builder.group.id, group2builder.group.id],
            'add_nonelectronic_deliveries_form': 'i18nlabel'
        })
        self.assertEquals(response.status_code, 302)

        group1builder.reload_from_db()
        group2builder.reload_from_db()
        group1delivery = Delivery.objects.get(deadline__assignment_group=group1builder.group)
        group2delivery = Delivery.objects.get(deadline__assignment_group=group2builder.group)
        self.assertEquals(group1delivery.delivery_type, deliverytypes.NON_ELECTRONIC)
        self.assertTrue(group1delivery.successful)
        self.assertEquals(group2delivery.delivery_type, deliverytypes.NON_ELECTRONIC)
        self.assertTrue(group2delivery.successful)



    #
    #
    # Cancel and success urls
    #
    #

    def test_custom_success_url(self):
        group1builder = self.assignment1builder\
            .add_group(examiners=[self.examiner1])
        group1builder.add_deadline_in_x_weeks(weeks=1)
        response = self._postas(self.examiner1, {
            'group_ids': [group1builder.group.id],
            'success_url': '/my/test',
            'add_nonelectronic_deliveries_form': 'i18nlabel'
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
        group1builder.add_deadline_in_x_weeks(weeks=1)
        response = self._postas(self.examiner1, {
            'group_ids': [group1builder.group.id],
            'add_nonelectronic_deliveries_form': 'i18nlabel'
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
