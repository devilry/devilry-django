from django.utils.translation import ugettext as _
from devilry.core import gradeplugin_registry
from gradeviews import view
from models import CharFieldGrade

gradeplugin_registry.register(
        view = view,
        model_cls = CharFieldGrade,
        description = _('Examiners type in grades manually in a text field ' \
            'without any restrictions beyond a 20 character limit.'))
