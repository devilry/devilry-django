from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from devilry.core import gradeplugin
from gradeviews import view
from models import RstSchemaGrade, RstSchemaDefinition


def url_callback(assignment_id):
    return reverse('devilry-grade_rstschema-edit_schema',
                args=[assignment_id])

def default_filecontents_callback(assignmentobj):
    schemadef = RstSchemaDefinition.objects.get(assignment=assignmentobj)
    return schemadef.schemadef

gradeplugin.registry.register(gradeplugin.RegistryItem(
        view = view,
        xmlrpc_gradeconf = gradeplugin.XmlrpcGradeConf(
            help = 'Fill out schema.rst.',
            filename = 'schema.rst',
            default_filecontents_callback=default_filecontents_callback),
        model_cls = RstSchemaGrade,
        admin_url_callback = url_callback,
        label = _('reStructuredText schema'),
        description = _(
            'Examiners fill in a schema defined by you (the ' \
            'administrator) using reStructuredText' \
            '(a quite simple plain-text format).')
))
