# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# CrAdmin imports
from django.views.generic import TemplateView
from django_cradmin import crapp

# Devilry imports
from devilry.devilry_qualifiesforexam.views import plugin_mixin
from devilry.devilry_qualifiesforexam.views import base_formview


class PluginSelectAssignmentsView(TemplateView, plugin_mixin.PluginMixin):
    """

    """
    template_name = 'devilry_qualifiesforexam_plugin_approved/base.django.html'
