from django.utils.translation import ugettext as _
from models import ApprovedGrade

from devilry.core import gradeplugin

from gradeviews import view


gradeplugin.registry.register(gradeplugin.RegistryItem(
        view = view,
        xmlrpc_gradeconf = gradeplugin.XmlrpcGradeConf(),
        model_cls = ApprovedGrade,
        label = _('Approved/not approved'),
        description = _('Examiners either approves or disapproves a delivery.')
))
