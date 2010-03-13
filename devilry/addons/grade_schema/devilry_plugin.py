from django.utils.translation import ugettext as _
from devilry.core import gradeplugin_registry
from django.core.urlresolvers import reverse
from models import SchemaGrade
from gradeviews import view

def url_callback(assignment_id):
    return reverse('devilry.addons.grade_schema.views.edit_schema',
                args=[assignment_id])

gradeplugin_registry.register(
        view = view,
        model_cls = SchemaGrade,
        label = _('Schema'),
        admin_url_callback = url_callback,
        description = _('Examiner fills in a schema.'))
