from crispy_forms.layout import Div


class EditFeedbackButtonBar(Div):
    template = "devilry_gradingsystem/editfeedbackbuttonbar.django.html"


class BulkEditFeedbackButtonBar(Div):
    template = "devilry_gradingsystem/bulkeditfeedbackbuttonbar.django.html"