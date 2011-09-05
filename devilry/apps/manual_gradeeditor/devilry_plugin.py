import json
from django.conf import settings

from devilry.apps.gradeeditors import (gradeeditor_registry, JsonRegistryItem,
                                       DraftValidationError, ConfigValidationError)
from devilry.apps.markup.parse_markdown import markdown_full



class Manual(JsonRegistryItem):
    gradeeditorid = 'manual'
    title = 'Manual'
    description = 'A simple gradeeditor where an examiner kan set grade, points and a feedbacktext. Note that this editor is a FALLBACK if none of the other editors fit your needs.'
    config_editor_url = None
    draft_editor_url = settings.DEVILRY_STATIC_URL + '/manual_gradeeditor/drafteditor.js'

    @classmethod
    def validate_draft(cls, draftstring, configstring):
        draft = json.loads(draftstring)
        cls.validate_dict(draft, DraftValidationError, {'approved': bool,
                                                        'points': int,
                                                        'grade': basestring,
                                                        'feedback': basestring})

        cls.validate_gradeeditor_key(draft, 'manual')

        if draft['grade'] == '':
            raise DraftValidationError('Grade-field cannot be empty')

    @classmethod
    def draft_to_staticfeedback_kwargs(cls, draftstring, configstring):
        draft = json.loads(draftstring)
        is_approved = draft['approved']
        points = draft['points']
        grade = draft['grade']
        feedback = draft['feedback']

        approved = 'not approved'
        if is_approved:
            approved = 'approved'

        return dict(is_passing_grade=is_approved,
                    grade=grade,
                    points=points,
                    rendered_view=markdown_full(feedback))

gradeeditor_registry.register(Manual)
