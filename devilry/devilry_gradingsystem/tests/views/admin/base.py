from devilry.devilry_gradingsystem.pluginregistry import GradingSystemPluginInterface
from devilry.project.develop.testhelpers.corebuilder import UserBuilder


class AdminViewTestMixin(object):
    """
    Mixin class for the grading system admin views. They all take
    ``assignmentid`` as kwarg, and they all require the same permissions,
    so we can allow them to share some code.
    """
    def login(self, user):
        self.client.login(username=user.username, password='test')

    def get_as(self, user, *args, **kwargs):
        """
        Login as the given user and run self.client.get(). Assumes
        that self.url is defined.
        """
        self.login(user)
        return self.client.get(self.url, *args, **kwargs)

    def post_as(self, user, *args, **kwargs):
        """
        Login as the given user and run self.client.post(). Assumes
        that self.url is defined.
        """
        self.login(user)
        return self.client.post(self.url, *args, **kwargs)

    def test_get_not_admin_404(self):
        nobody = UserBuilder('nobody').user
        response = self.get_as(nobody)
        self.assertEquals(response.status_code, 404)



class MockPointsPluginApi(GradingSystemPluginInterface):
    id = 'mock_gradingsystemplugin_points'
    title = 'Mock points'
    description = 'Mock points description.'

    def get_edit_feedback_url(self, deliveryid):
        return '/mock/points/edit_feedback/{}'.format(deliveryid)


class MockApprovedPluginApi(GradingSystemPluginInterface):
    id = 'mock_gradingsystemplugin_approved'
    title = 'Mock approved'
    description = 'Mock approved description.'
    sets_passing_grade_min_points_automatically = True
    sets_max_points_automatically = True

    def get_edit_feedback_url(self, deliveryid):
        return '/mock/approved/edit_feedback/{}'.format(deliveryid)

    def get_passing_grade_min_points(self):
        return 1

    def get_max_points(self):
        return 1


class MockRequiresConfigurationPluginApi(GradingSystemPluginInterface):
    id = 'mock_gradingsystemplugin_requiresconfiguration'
    title = 'Mock requiresconfiguration'
    description = 'Mock requiresconfiguration description.'
    requires_configuration = True

    def get_edit_feedback_url(self, deliveryid):
        return '/mock/requiresconfiguration/edit_feedback/{}'.format(deliveryid)

    def get_configuration_url(self):
        return '/mock/requiresconfiguration/configure/{}'.format(self.assignment.id)
