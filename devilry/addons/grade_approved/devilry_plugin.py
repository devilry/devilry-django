from django.utils.translation import ugettext as _
from models import ApprovedGrade

from devilry.xmlrpc.gradeconf import GradeConf
from devilry.core import gradeplugin_registry

from gradeviews import view


gradeplugin_registry.register(
        view = view,
        xmlrpc_gradeconf = GradeConf(),
        model_cls = ApprovedGrade,
        label = _('Approved/not approved'),
        description = _('Examiners either approves or disapproves a delivery.'))
