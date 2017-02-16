# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django import http
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy
from django_cradmin.widgets.datetimepicker import DateTimePickerWidget

from crispy_forms import layout

from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_cradmin import devilry_listfilter
from devilry.devilry_deadlinemanagement.views import viewutils
from devilry.devilry_group import models as group_models
from devilry.utils import datetimeutils


class NewAttemptDeadlineForm(viewutils.SelectedAssignmentGroupForm):
    invalid_qualification_item_message = pgettext_lazy(
        'examiner group multiselect submit',
        'Something went wrong. This may happen if someone else performed a similar operation '
        'while you where selecting. Refresh the page and try again')


class SelectedAssignmentGroupsTargetRenderer(viewutils.AssignmentGroupTargetRenderer):
    def get_hidden_fields(self):
        return [
            layout.Hidden(name='post_type_received_data', value='')
        ]

    def get_form_action(self, request):
        self.form_action = 'post'
        print '\n\n\nTARGET DEADLINE: {}\n\n\n'.format(self.deadline)
        # return super(SelectedAssignmentGroupsTargetRenderer, self).get_form_action(request)
        return request.cradmin_app.reverse_appurl(viewname='manage-deadline-post')


class BulkManageDeadlineMultiSelectView(viewutils.AbstractAssignmentGroupMultiSelectListFilterView):
    value_renderer_class = devilry_listbuilder.assignmentgroup.ExaminerMultiselectItemValue
    template_name = 'devilry_deadlinemanagement/deadline-bulk-multiselect-filterlistview.django.html'

    def dispatch(self, request, *args, **kwargs):
        self.deadline = datetimeutils.string_to_datetime(kwargs.get('deadline'))
        return super(BulkManageDeadlineMultiSelectView, self).dispatch(request, *args, **kwargs)

    def get_pagetitle(self):
        return ugettext_lazy('Manage groups on deadline')

    def add_filterlist_items(self, filterlist):
        super(BulkManageDeadlineMultiSelectView, self).add_filterlist_items(filterlist)
        filterlist.append(devilry_listfilter.assignmentgroup.IsPassingGradeFilter())
        filterlist.append(devilry_listfilter.assignmentgroup.PointsFilter())

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'choose-manually-filter', kwargs={
                'deadline': datetimeutils.datetime_to_string(self.deadline),
                'filters_string': filters_string
            })

    def get_target_renderer_class(self):
        return SelectedAssignmentGroupsTargetRenderer

    def get_form_class(self):
        return NewAttemptDeadlineForm
