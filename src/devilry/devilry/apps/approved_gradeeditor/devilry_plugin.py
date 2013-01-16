import json
from django.conf import settings

from devilry.apps.gradeeditors import (gradeeditor_registry, JsonRegistryItem,
                                       DraftValidationError)
from devilry.apps.gradeeditors import ShortFormat
from devilry.apps.gradeeditors import ShortFormatWidgets
from devilry.apps.gradeeditors import ShortFormatValidationError
from devilry.apps.markup.parse_markdown import markdown_full
from django.utils.translation import ugettext_lazy as _


def _grade_from_is_passing_grade(is_passing_grade):
    if is_passing_grade:
        return 'approved'
    else:
        return 'not approved'


class ApprovedShortFormat(ShortFormat):
    widget = ShortFormatWidgets.BOOL
    truevalue = 'true'
    falsevalue = 'false'

    @classmethod
    def validate(cls, config, value):
        if not value == cls.truevalue and not value == cls.falsevalue:
            raise ShortFormatValidationError(_('Must be one of: true, false.'))

    @classmethod
    def to_staticfeedback_kwargs(cls, config, value):
        is_passing_grade = value == cls.truevalue
        grade = _grade_from_is_passing_grade(is_passing_grade)
        return {
            'is_passing_grade': is_passing_grade,
            'grade': grade,
            'points': int(is_passing_grade),
            'rendered_view': ''
        }

    @classmethod
    def format_feedback(cls, config, feedback):
        if feedback.is_passing_grade:
            return cls.truevalue
        else:
            return cls.falsevalue

    @classmethod
    def shorthelp(cls, config):
        return _('Must be one of: true, false.')


class Approved(JsonRegistryItem):
    """
    Serves as a minimal example of a grade editor, and as a well suited grade
    editor for use in test cases.
    """
    gradeeditorid = 'approved'
    title = 'Approved/not approved'
    description = '<p>A simple gradeeditor that allows examiners to select if delivery is approved or not approved, and give a feedback text.</p>'
    config_editor_url = None
    draft_editor_url = settings.DEVILRY_STATIC_URL + '/approved_gradeeditor/drafteditor.js'
    shortformat = ApprovedShortFormat

    @classmethod
    def validate_draft(cls, draftstring, configstring):
        draft = json.loads(draftstring)
        cls.validate_dict(draft, DraftValidationError, {'approved': bool,
                                                        'feedback': basestring})
        cls.validate_gradeeditor_key(draft, 'approved')


    @classmethod
    def draft_to_staticfeedback_kwargs(cls, draftstring, configstring):
        draft = json.loads(draftstring)
        is_approved = draft['approved']
        grade = _grade_from_is_passing_grade(is_approved)
        return dict(is_passing_grade=is_approved,
                    grade=grade,
                    points=int(is_approved),
                    rendered_view=markdown_full(draft['feedback']))

gradeeditor_registry.register(Approved)
