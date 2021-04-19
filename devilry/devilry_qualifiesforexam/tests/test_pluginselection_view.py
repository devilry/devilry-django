# 3rd party imports
import mock
from model_bakery import baker

# Django imports
from django import test

# CrAdmin imports
from cradmin_legacy import cradmin_testhelpers

# Devilry imports
from devilry.project.common import settings
from devilry.devilry_qualifiesforexam.views import pluginselection_view
from devilry.devilry_qualifiesforexam import plugintyperegistry
from devilry.devilry_qualifiesforexam.listbuilder import plugin_listbuilder_list


class TestSelectPluginView(pluginselection_view.SelectPluginView):
    """
    This class works as a `patch` for SelectPluginView.

    Testview that does exactly the same as SelectPluginView. This is neccessary because the plugins are loaded
    when the app(the actual django app that is the plugin) is loaded. If only using SelectPluginView, the plugins
    will be loaded from the app and we'll get plugins that are NOT meant for the tests
    (plugins added for development or production).

    To start with a blank slate, this subclass is created and the get_plugin_listbuilder_list is overridden by
    creating a mockable registry, instead of using the default registry, and the plugins added to the class attribute
    ``plugin_classes`` is added to the mockable registry. When the testplugin is created in a test, it's simply added
    to the TestPluginSelectionView.viewclass (which is this class).

    This is to make sure we have an EMPTY registry for each test!
    """
    plugin_classes = []

    def get_plugin_listbuilder_list(self):
        mock_registry = plugintyperegistry.MockableRegistry.make_mockregistry()
        for plugin in self.plugin_classes:
            mock_registry.add(plugin)
        return plugin_listbuilder_list.PluginListBuilderList.from_plugin_registry(
            pluginregistry=mock_registry,
            roleid=self.request.cradmin_role.id
        )


class TestPluginSelectionView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    """
    Tests the plugin selection view and what is rendered to the page.
    """
    viewclass = TestSelectPluginView

    def __create_period_admin(self, period=None):
        """
        Automation for creating a testadmin.

        Args:
            period: if period is None, an active period is created.
        Returns:
            User: admin user in a periodpermissiongroup
        """
        if period is None:
            period = baker.make_recipe('devilry.apps.core.period_active')
        testadmin = baker.make(settings.AUTH_USER_MODEL)
        periodpermissiongroup = baker.make('devilry_account.PeriodPermissionGroup', period=period)
        baker.make('devilry_account.PermissionGroupUser',
                   user=testadmin,
                   permissiongroup=periodpermissiongroup.permissiongroup)
        return testadmin, period

    def test_list_no_plugins(self):
        # No plugins are added, make sure no plugins are listed.
        testadmin, testperiod = self.__create_period_admin()
        mockrequest = mock.MagicMock()
        mockrequest.cradmin_role = testperiod
        mockrequest.user = testadmin
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                requestuser=testadmin)
        self.assertFalse(mockresponse.selector.exists('devilry-cradmin-legacy-listbuilder-itemframe-goforward'))

    def test_list_single_plugin(self):
        # Add a single plugin to the registry and make sure its listed.
        testadmin, testperiod = self.__create_period_admin()
        mockrequest = mock.MagicMock()
        mockrequest.cradmin_role = testperiod
        mockrequest.user = testadmin

        # Create a PluginType subclass
        testplugin = plugintyperegistry.PluginTypeSubclassFactory.make_subclass(
                classname='TestPlugin',
                plugintypeid='test_plugin')
        self.viewclass.plugin_classes = [testplugin]

        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                requestuser=testadmin)
        self.assertTrue(mockresponse.selector.one('.devilry-cradmin-legacy-listbuilder-itemframe-goforward'))

    def test_list_multiple_plugins(self):
        # Add a three plugins and make sure all three plugins are listed.
        testadmin, testperiod = self.__create_period_admin()
        mockrequest = mock.MagicMock()
        mockrequest.cradmin_role = testperiod
        mockrequest.user = testadmin

        # Create a PluginType subclasses
        testplugin1 = plugintyperegistry.PluginTypeSubclassFactory.make_subclass(
                classname='TestPluginOne',
                plugintypeid='test_plugin_1')
        testplugin2 = plugintyperegistry.PluginTypeSubclassFactory.make_subclass(
                classname='TestPluginTwo',
                plugintypeid='test_plugin_2')
        testplugin3 = plugintyperegistry.PluginTypeSubclassFactory.make_subclass(
                classname='TestPluginThree',
                plugintypeid='test_plugin_3')
        self.viewclass.plugin_classes = [testplugin1, testplugin2, testplugin3]

        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                requestuser=testadmin)
        self.assertEqual(3, len(mockresponse.selector.list('.devilry-cradmin-legacy-listbuilder-itemframe-goforward')))
