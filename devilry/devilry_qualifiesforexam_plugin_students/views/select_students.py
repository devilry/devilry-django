# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Django imports
from django.http import HttpResponseRedirect

# Devilry imports
from devilry.apps.core import models as core_models
from devilry.devilry_qualifiesforexam.views import plugin_mixin
from devilry.devilry_qualifiesforexam.views.plugin_base_views import base_multiselect_view


class StudentQualificationForm(base_multiselect_view.SelectedQualificationForm):
    qualification_modelclass = core_models.RelatedStudent


class StudentQualificationItemTargetRenderer(base_multiselect_view.QualificationItemTargetRenderer):
    descriptive_item_name = 'students'


class PluginSelectStudentsView(base_multiselect_view.QualificationItemListView, plugin_mixin.PluginMixin):
    model = core_models.RelatedStudent
    plugintypeid = 'devilry_qualifiesforexam_plugin_students.plugin_select_students'

    def get_period_result_collector_class(self):
        pass

    def get_queryset_for_role(self, role):
        return self.model.objects.filter(period__id=role.id)

    def get_inititially_selected_queryset(self):
        return self.model.objects.none()

    def get_target_renderer_class(self):
        return StudentQualificationItemTargetRenderer

    def get_form_class(self):
        return StudentQualificationForm

    def get_pagetitle(self):
        return 'Select students'

    def form_valid(self, form):
        self.request.session['passing_relatedstudentids'] = self.get_qualifying_itemids(posted_form=form)
        self.request.session['plugintypeid'] = PluginSelectStudentsView.plugintypeid
        return HttpResponseRedirect(self.request.cradmin_app.reverse_appurl('preview'))
