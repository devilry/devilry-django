# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# CrAdmin imports
from django_cradmin.viewhelpers import multiselect


class FormViewBase(multiselect.MultiSelectFormView):
    """

    """
    def get_form(self, form_class=None):
        pass

    def get_queryset_for_role(self, role):
        pass

    def form_valid(self, form):
        pass

    def get_field_layout(self):
        pass
