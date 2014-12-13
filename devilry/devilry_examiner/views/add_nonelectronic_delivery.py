from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.layout import Submit
from crispy_forms.layout import HTML
from crispy_forms.layout import ButtonHolder

from devilry.devilry_examiner.views.crispylayout import DefaultSubmit
from .bulkviewbase import BulkViewBase
from .bulkviewbase import OptionsForm


class AddNonElectronicDeliveryForm(OptionsForm):
    def __init__(self, *args, **kwargs):
        super(AddNonElectronicDeliveryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'group_ids',
            'success_url',
            'cancel_url',
            HTML('<hr>'),
            ButtonHolder(
                Submit('add_nonelectronic_deliveries_form', _('Add non-electronic delivery'), css_class='pull-right'),
                DefaultSubmit('submit_cancel', _('Cancel')),
            )
        )


class AddNonElectronicDeliveryView(BulkViewBase):
    """
    A bulk view for closing one or more groups.
    """
    template_name = "devilry_examiner/add_nonelectronic_delivery.django.html"
    primaryform_classes = {
        'add_nonelectronic_deliveries_form': AddNonElectronicDeliveryForm
    }

    def submitted_primaryform_valid(self, form, context_data):
        self.selected_groups.add_nonelectronic_delivery()
        return super(AddNonElectronicDeliveryView, self).submitted_primaryform_valid(form, context_data)
