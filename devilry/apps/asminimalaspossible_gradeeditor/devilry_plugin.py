import json
from django.conf import settings

from devilry.apps.gradeeditors import gradeeditor_registry, RegistryItem, DraftValidationError



class AsMinimalAsPossible(RegistryItem):
    """
    Serves as a minimal example of a grade editor, and as a well suited grade
    editor for use in test cases.
    """
    gradeeditorid = 'asminimalaspossible'
    title = 'Minimal'
    description = 'A minimal grade editor for testing. Allows examiners to select if delivery is approved or not approved.'
    config_editor_url = None
    draft_editor_url = settings.DEVILRY_STATIC_URL + '/asminimalaspossible_gradeeditor/drafteditor.js'

    @classmethod
    def validate_config(cls, configstring):
        pass

    @classmethod
    def validate_draft(cls, draftstring):
        try:
            is_approved = json.loads(draftstring)
        except ValueError, e:
            raise DraftValidationError('Could not decode draft string as JSON.')
        if not isinstance(is_approved, bool):
            raise DraftValidationError('The draft string must contain a single boolean value.')

    @classmethod
    def draft_to_staticfeedback_kwargs(cls, draftstring):
        is_approved = json.loads(draftstring)
        if is_approved:
            grade = 'approved'
        else:
            grade = 'not approved'
        return dict(is_passing_grade=is_approved,
                    grade=grade,
                    points=int(is_approved),
                    rendered_view='Your grade is: {0}'.format(grade))


gradeeditor_registry.register(AsMinimalAsPossible)
