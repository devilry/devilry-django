# -*- coding: utf-8 -*-


# Django imports
from django.http import HttpResponseBadRequest
from django.views.generic import View

# Devilry imports
from devilry.devilry_qualifiesforexam import plugintyperegistry


class PluginProxyView(View):
    """
    View that forwards the request to a defined plugin.

    The plugin id is fetched from the
    :obj:`devilry.devilry_qualifiesforexam.plugintyperegistry.Registry` and the request is forwarded to the view
    returned from :meth:`devilry.devilry_qualifiesforexam.plugintyperegistry.PluginType.get_plugin_view_class`.
    """
    def dispatch(self, request, *args, **kwargs):
        """
        Proxy the request to the correct
        :meth:`devilry.devilry_qualifiesforexam.plugintyperegistry.PluginType.get_plugin_view_class`.

        Args:
            plugintypeid: The :obj:`devilry.devilry_qualifiesforexam.plugintyperegistry.PluginType.plugintypeid` for
                the :class:`devilry.devilry_qualifiesforexam.plugintyperegistry.PluginType` that should be used.

        Returns:
            An instance of the class returned by
            :meth:`devilry.devilry_qualifiesforexam.plugintyperegistry.PluginType.get_plugin_view_class`.
            or a :class:`~django.http.HttpResponseBadRequest` if ``plugintypeid`` provided in ``**kwargs`` does not
            exist.
        """
        plugintypeid = kwargs['plugintypeid']

        try:
            pluginclass = plugintyperegistry.Registry.get_instance()[plugintypeid]
        except KeyError:
            return HttpResponseBadRequest('<h1>Plugin "{}" does not exist.</h1>'.format(plugintypeid))

        plugin = pluginclass()
        viewclass = plugin.get_plugin_view_class()
        view = viewclass.as_view(
            proxyview=self,
            plugin=plugin
        )
        return view(request, *args, **kwargs)
