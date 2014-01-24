from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.layout import Field
from crispy_forms.layout import Submit
from crispy_forms.layout import HTML
from crispy_forms.layout import ButtonHolder

from .crispylayout import DefaultSubmit
from .bulkviewbase import BulkViewBase
from .bulkviewbase import OptionsForm




class CloseGroupsForm(OptionsForm):
    def __init__(self, *args, **kwargs):
        super(CloseGroupsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'group_ids',
            'success_url',
            'cancel_url',
            HTML('<hr>'),
            ButtonHolder(
                Submit('close_groups_confirm_form', _('Close groups'), css_class='pull-right'),
                DefaultSubmit('submit_cancel', _('Cancel')),
            )
        )


class CloseGroupsView(BulkViewBase):
    """
    A bulk view for closing one or more groups.
    """
    template_name = "devilry_examiner/close_groups.django.html"
    primaryform_classes = {
        'close_groups_confirm_form': CloseGroupsForm
    }

    def submitted_primaryform_valid(self, form, context_data):
        self.selected_groups.close_groups()
        return super(CloseGroupsView, self).submitted_primaryform_valid(form, context_data)