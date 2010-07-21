from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django import forms
from django.conf import settings
from django.contrib.auth.models import User

class DevilryDateWidget(forms.DateTimeInput):
    class Media:
        js = (settings.DEVILRY_RESOURCES_URL + "/ui/js/datewidget.js",)

    def __init__(self, attrs={}):
        super(DevilryDateWidget, self).__init__(
                attrs = {'class': 'devilry-date', 'size': '11'},
                format = '%Y-%m-%d')

class DevilryTimeWidget(forms.TimeInput):
    class Media:
        js = (settings.DEVILRY_RESOURCES_URL + "/ui/js/timewidget.js",)

    def __init__(self, attrs={}):
        super(DevilryTimeWidget, self).__init__(
                attrs={'class': 'devilry-time', 'size': '8'},
                format='%H:%M')

class DevilryDateTimeWidget(forms.SplitDateTimeWidget):
    def __init__(self, attrs=None):
        widgets = [DevilryDateWidget, DevilryTimeWidget]
        forms.MultiWidget.__init__(self, widgets, attrs)

    def format_output(self, rendered_widgets):
        return mark_safe(
                u'<div class="devilry-datetime">'
                u'<div><span class"devilry-date-label">%s</span> %s</div>' \
                u'<div><span class"devilry-time-label">%s</span> %s</div>' \
                u'</div>' % (
                _('Date:'), rendered_widgets[0], _('Time:'), rendered_widgets[1]))


class DevilryMultiSelectFew(forms.TextInput):
    class Media:
        js = (settings.DEVILRY_RESOURCES_URL + "/ui/js/multiSelect_char_user_field.js",)
                
    def __init__(self, attrs={}):
        widgets = [DevilryMultiSelectFew]
        attrs["size"] = 60
        attrs["class"] = "devilry_multiselect_few"
        super(DevilryMultiSelectFew, self).__init__(attrs)
    
    def render(self, name, value, attrs=None):
        qry = User.objects.filter(pk__in=value).all()
        value = ", ".join([u.username for u in qry])
        return super(DevilryMultiSelectFew, self).render(name, value, attrs)
       



