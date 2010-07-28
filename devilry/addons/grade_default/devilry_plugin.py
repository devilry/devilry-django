from django.utils.translation import ugettext as _

from devilry.core import gradeplugin

from gradeviews import view
from models import CharFieldGrade


gradeplugin.registry.register(gradeplugin.RegistryItem(
        view = view,
        xmlrpc_gradeconf = gradeplugin.XmlrpcGradeConf(),
        model_cls = CharFieldGrade,
        label = _('Manual grade handling'),
        description = _('Examiners type in grades manually in a text field ' \
            'without any restrictions beyond a 20 character limit.')
))
