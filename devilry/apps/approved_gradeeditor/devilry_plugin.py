import json
from django.conf import settings

from devilry.apps.gradeeditors import (gradeeditor_registry, JsonRegistryItem,
                                       DraftValidationError)
from devilry.apps.markup.parse_markdown import markdown_full



class Approved(JsonRegistryItem):
    """
    Serves as a minimal example of a grade editor, and as a well suited grade
    editor for use in test cases.
    """
    gradeeditorid = 'approved'
    title = 'Approved'
    description = 'A simple gradeeditor that allows examiners to select if delivery is approved or not approved, and give a feedback text.'
    config_editor_url = None
    draft_editor_url = settings.DEVILRY_STATIC_URL + '/approved_gradeeditor/drafteditor.js'

    @classmethod
    def validate_draft(cls, draftstring, configstring):
        buf = json.loads(draftstring)
        is_approved = buf[0]
        feedback = buf[1]

        if not isinstance(is_approved, bool):
            raise DraftValidationError('The draft string must contain a single boolean value.')

        if feedback == '':
            raise DraftValidationError('You have to enter a feedback-text')

    @classmethod
    def draft_to_staticfeedback_kwargs(cls, draftstring, configstring):
        buf = json.loads(draftstring)
        is_approved = buf[0]
        feedback = buf[1]

        if is_approved:
            grade = 'approved'
        else:
            grade = 'not approved'
        return dict(is_passing_grade=is_approved,
                    grade=grade,
                    points=int(is_approved),
                    rendered_view=markdown_full(feedback))

gradeeditor_registry.register(Approved)
