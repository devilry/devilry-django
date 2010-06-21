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

    def render(self, *args, **kwargs):
        widget = super(DevilryDateWidget, self).render(*args, **kwargs)
        return mark_safe(
                u'%s <span class="devilry-date-format">%s</span>' % (
                    widget, _('yyyy-mm-dd')))

class DevilryTimeWidget(forms.TimeInput):
    def __init__(self, attrs={}):
        super(DevilryTimeWidget, self).__init__(
                attrs={'class': 'devilry-time', 'size': '8'},
                format='%H:%M')

    def render(self, *args, **kwargs):
        widget = super(DevilryTimeWidget, self).render(*args, **kwargs)
        return mark_safe(
                u'%s <span class="devilry-time-format">%s</span>' % (
                    widget, _('hh:mm')))

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
    def __init__(self, attrs={}):
        widgets = [DevilryMultiSelectFew]
        attrs["size"] = 60
        super(DevilryMultiSelectFew, self).__init__(attrs)
    
    def render(self, name, value, attrs=None):
        #print "value:", type(value)
        qry = User.objects.filter(pk__in=value).all()
        #value = ", ".join([str(x) for x in value])
        value = ", ".join([u.username for u in qry])
        return super(DevilryMultiSelectFew, self).render(name, value, attrs)
        #print "type:", type(widget)
        #return mark_safe(widget)



