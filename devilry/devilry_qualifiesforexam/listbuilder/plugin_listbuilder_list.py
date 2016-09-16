# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# CrAdmin imports
from django_cradmin.crinstance import reverse_cradmin_url
from django_cradmin.viewhelpers import listbuilder

# Devilry imports
from devilry.devilry_qualifiesforexam import plugintyperegistry
from devilry.devilry_cradmin import devilry_listbuilder


class PluginListBuilderList(listbuilder.base.List):

    @classmethod
    def from_plugin_registry(cls, pluginregistry, roleid):
        """
        Create instance of :class:`~.PluginListBuilderList` and append renderable links
        for the plugins in the plugin registry.

        Args:
            pluginregistry: the registry instance to get plugins from.
            roleid: id for the crinstance role.

        Returns:
            PluginListBuilderList: Instance.
        """
        plugin_list = cls()
        for plugin_class in pluginregistry:
            plugin = plugin_class()
            plugin_list.append_plugin(plugin, roleid)
        return plugin_list

    def append_plugin(self, plugin, roleid):
        """
        Append renderable link frame for plugin, and add :obj:`PluginItemValue`
        as :obj:`PluginItemFrame`s ``innteritem``.

        Args:
            plugin:
                :obj:`devilry.devilry_qualifiesforexam.plugintyperegistry.PluginType` instance to add.
        """
        item_value = PluginItemValue(value=plugin)
        valuerenderer = PluginItemFrame(inneritem=item_value, roleid=roleid)
        self.append(renderable=valuerenderer)


class PluginItemFrame(devilry_listbuilder.common.GoForwardLinkItemFrame):
    """
    Link to the plugin configuration.

    :obj:`PluginItemFrame.value` is the same as :obj:`PluginItemFrame.inneritem.value`
    """
    valuealias = 'plugin'

    def __init__(self, roleid, *args, **kwargs):
        """
        Args:
            roleid: Id for the crinstance role. Needed to build the url.
        """
        super(PluginItemFrame, self).__init__(*args, **kwargs)
        self.roleid = roleid

    def get_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_qualifiesforexam',
            appname='qualifiesforexam',
            roleid=self.roleid,
            viewname='configure-plugin',
            kwargs={
                'plugintypeid': self.plugin.get_plugintypeid(),
            }
        )


class PluginItemValue(listbuilder.base.ItemValueRenderer):
    """
    The ItemValue with information about a plugin.

    This is the inner item Renderable for :class:`PluginItemFrame`
    """
    valuealias = 'plugin'
    template_name = 'devilry_qualifiesforexam/listbuilder/plugin_item_value.django.html'

    def get_extra_css_classes_list(self):
        css_classes_list = super(PluginItemValue, self).get_extra_css_classes_list()
        return css_classes_list
