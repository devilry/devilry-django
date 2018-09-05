# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Django imports
from django.utils.translation import ugettext
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect

# CrAdmin imports
from django_cradmin.crinstance import reverse_cradmin_url
from django_cradmin.viewhelpers import listbuilder

# Devilry imports
from devilry.apps.core.models import Assignment
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_qualifiesforexam.listbuilder import plugin_listbuilder_list
from devilry.devilry_qualifiesforexam import plugintyperegistry
from devilry.devilry_qualifiesforexam import models as status_models


class ItemFrameMixin(object):
    def __init__(self, roleid, *args, **kwargs):
        self.roleid = roleid
        super(ItemFrameMixin, self).__init__(*args, **kwargs)

    def get_extra_css_classes_list(self):
        css_classes_list = super(ItemFrameMixin, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-qualifiesforexam-plugin-spacing')
        css_classes_list.append('django-cradmin-listbuilder-itemvalue'
                                ' devilry-frontpage-listbuilder-roleselect-itemvalue'
                                ' devilry-frontpage-listbuilder-roleselect-itemvalue-anyadmin'
                                ' devilry-passed-previous-semester-mode-item-value')
        return css_classes_list


class ManualPassModeItemFrame(ItemFrameMixin, devilry_listbuilder.common.GoForwardLinkItemFrame):
    """
    """
    def get_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_admin_assignmentadmin',
            appname='passed_previous_period',
            roleid=self.roleid,
            viewname='manually_select_groups'
        )


class ManualPassModeItemValue(listbuilder.itemvalue.TitleDescription):
    def get_title(self):
        return ugettext('Manually pass students')

    def get_description(self):
        return ugettext('Manually select students that has passed this assignment, or it\'s equivalent, on a previous '
                        'semester. This is for simplifying bulk-passing students on an assignment for an admin, '
                        'you don\'t actually select a semester.')

    def get_extra_css_classes_list(self):
        css_classes_list = super(ManualPassModeItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-passed-previous-semester-mode-auto-item-value')
        return css_classes_list


class AutoPassPreviousPeriodItemFrame(ItemFrameMixin, devilry_listbuilder.common.GoForwardLinkItemFrame):
    def get_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_admin_assignmentadmin',
            appname='passed_previous_period',
            roleid=self.roleid,
            viewname='select_period'
        )


class AutoPassPreviousPeriodItemValue(listbuilder.itemvalue.TitleDescription):
    def get_title(self):
        return ugettext('Automatically pass students from an earlier semester')

    def get_description(self):
        return ugettext('Automatically pass students from earlier semester by selecting the semester you want to '
                        'get the results from. This requires that the assignment has the same shortname as the '
                        'previous assignment.')

    def get_extra_css_classes_list(self):
        css_classes_list = super(AutoPassPreviousPeriodItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-passed-previous-semester-mode-auto-item-value')
        return css_classes_list


class Overview(TemplateView):
    """
    Lists registered plugins.

    If a :class:`~.devilry.devilry_qualifiesforexam.models.Status` already exists for this period,
    the request will be redirected to a show status view.
    """
    template_name = 'devilry_admin/assignment/passed_previous_period/overview.django.html'

    def dispatch(self, request, *args, **kwargs):
        return super(Overview, self).dispatch(request=request, *args, **kwargs)

    def get_mode_renderables(self):
        return [
            ManualPassModeItemFrame(
                inneritem=ManualPassModeItemValue(value=None),
                roleid=self.request.cradmin_role.id
            ),
            AutoPassPreviousPeriodItemFrame(
                inneritem=AutoPassPreviousPeriodItemValue(value=None),
                roleid=self.request.cradmin_role.id
            )
        ]

    def __get_mode_listbuilder_list(self):
        """
        Get a plugin listbuilder list.
        This function is mostly used for patching in tests.
        Override this to use a mockable registry for testing.

        Returns:
            A :class:`devilry.devilry_qualifiesforexam.listbuilder.plugin_listbuilder_list.PluginListBuilderList`
            instance.
        """
        list_builder = listbuilder.base.List()
        for renderable in self.get_mode_renderables():
            list_builder.append(renderable=renderable)
        return list_builder

    def get_context_data(self, **kwargs):
        context_data = super(Overview, self).get_context_data(**kwargs)
        assignment = self.request.cradmin_role
        if assignment.grading_system_plugin_id != Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED:
            context_data['unsupported_grading_plugin'] = True
        else:
            context_data['mode_listbuilder_list'] = self.__get_mode_listbuilder_list()
        return context_data
