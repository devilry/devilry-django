from django.utils.translation import ugettext as _
from devilry.core import gradeplugin_registry
from models import ApprovedGrade
from gradeviews import view

gradeplugin_registry.register(
        view = view,
        model_cls = ApprovedGrade,
        label = _('Approved/not approved'),
        description = _('Examiners either approves or disapproves a delivery.'))
