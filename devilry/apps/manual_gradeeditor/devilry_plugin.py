import json
from django.conf import settings

from devilry.apps.gradeeditors import (gradeeditor_registry, JsonRegistryItem,
                                       DraftValidationError, ConfigValidationError)



class Manual(JsonRegistryItem):
    """
    Serves as a minimal example of a grade editor, and as a well suited grade
    editor for use in test cases.
    """
    gradeeditorid = 'manual'
    title = 'Manual'
    description = 'A simple gradeeditor where an examiner kan set grade, points and a feedbacktext.'
    config_editor_url = None
    draft_editor_url = settings.DEVILRY_STATIC_URL + '/manual_gradeeditor/drafteditor.js'

    @classmethod
    def validate_draft(cls, draftstring):
        buf = json.loads(draftstring)
        is_approved = buf[0]

        if not isinstance(is_approved, bool):
            raise DraftValidationError('The draft string must contain a boolean value.')

    @classmethod
    def draft_to_staticfeedback_kwargs(cls, draftstring):
        buf = json.loads(draftstring)
        is_approved = buf[0]
        points = buf[1]
        grade = buf[2]
        feedback = buf[3]

        approved = 'not approved'
        if is_approved:
            approved = 'approved'

        return dict(is_passing_grade=is_approved,
                    grade=grade,
                    points=points,
                    rendered_view=feedback)

        #TODO: .format() crashes when using non-ascii symbols.. need to find a fix since norwegian characters are bound to be used in feedbacks!!

gradeeditor_registry.register(Manual)
