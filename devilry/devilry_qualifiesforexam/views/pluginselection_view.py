# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Django imports
from django.utils.translation import ugettext_lazy
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect

# Devilry imports
from devilry.devilry_qualifiesforexam.listbuilder import plugin_listbuilder_list
from devilry.devilry_qualifiesforexam import plugintyperegistry
from devilry.devilry_qualifiesforexam import models as status_models


class SelectPluginView(TemplateView):
    """
    Lists registered plugins.

    If a :class:`~.devilry.devilry_qualifiesforexam.models.Status` already exists for this period,
    the request will be redirected to a show status view.
    """
    template_name = 'devilry_qualifiesforexam/selectplugin.django.html'

    def dispatch(self, request, *args, **kwargs):
        """
        Redirect to show status if a ready status already exists.
        """
        # status = status_models.Status.objects.order_by('-createtime').first()
        period = self.request.cradmin_role
        status = status_models.Status.objects.get_last_status_in_period(period=period)
        if status and status.status == status_models.Status.READY:
            return HttpResponseRedirect(self.request.cradmin_app.reverse_appurl(
                viewname='show-status',
                kwargs={
                    'roleid': self.request.cradmin_role.id,
                    'statusid': status.id
                }
            ))
        return super(SelectPluginView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.cradmin_instance.get_rolequeryset()

    def get_plugin_listbuilder_list(self):
        """
        Get a plugin listbuilder list.
        This function is mostly used for patching in tests.
        Override this to use a mockable registry for testing.

        Returns:
            A :class:`devilry.devilry_qualifiesforexam.listbuilder.plugin_listbuilder_list.PluginListBuilderList`
            instance.
        """
        listbuilder_class = plugin_listbuilder_list.PluginListBuilderList
        return listbuilder_class.from_plugin_registry(
                pluginregistry=plugintyperegistry.Registry.get_instance(),
                roleid=self.request.cradmin_role.id)

    def get_context_data(self, **kwargs):
        context_data = super(SelectPluginView, self).get_context_data(**kwargs)
        context_data['headline'] = ugettext_lazy('How do students qualify for final exams?')
        context_data['help_text'] = ugettext_lazy(
            'Select one of the options from the list. '
            'Each option starts a wizard that ends with a preview of the results before you get the option to save'
        )
        context_data['plugin_listbuilder_list'] = self.get_plugin_listbuilder_list()

        return context_data
