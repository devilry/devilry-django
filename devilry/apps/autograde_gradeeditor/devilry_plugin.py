import json
from django.conf import settings

from devilry.apps.gradeeditors import (gradeeditor_registry, JsonRegistryItem,
                                       DraftValidationError, ConfigValidationError)



class Manual(JsonRegistryItem):
    """
    Serves as a minimal example of a grade editor, and as a well suited grade
    editor for use in test cases.
    """
    gradeeditorid = 'autograde'
    title = 'Automatig grading'
    description = 'A gradeeditor where the examiner sets the number of points earned, and the grade is automatically set.'
    config_editor_url = settings.DEVILRY_STATIC_URL + '/autograde_gradeeditor/configeditor.js'
    draft_editor_url = settings.DEVILRY_STATIC_URL + '/autograde_gradeeditor/drafteditor.js'

    @classmethod
    def validate_config(cls, configstring):
        config = cls.decode_configstring(configstring)
        cls.validate_dict(config, ConfigValidationError, {'maxpoints': int,
                                                          'approvedlimit': int,
                                                          'usegrades': bool,
                                                          'A': int,
                                                          'B': int,
                                                          'C': int,
                                                          'D': int,
                                                          'E': int,
                                                          'pointlabel': basestring,
                                                          'feedbacklabel': basestring})

    @classmethod
    def validate_draft(cls, draftstring):
        buf = json.loads(draftstring)
        points = buf[0]
        grade = buf[1]
        feedback = buf[2]
        is_approved = buf[3]

        if not isinstance(points, int):
            raise DraftValidationError('The points-field must be an integer-value.')

        if not isinstance(grade, basestring):
            raise DraftValidationError('The grade-field must be a string-value.')

        if not isinstance(feedback, basestring):
            raise DraftValidationError('The feedback-field must contain a string-value.')

        if not isinstance(is_approved, bool):
            raise DraftValidationError('is_approved must be a boolean value.')

    @classmethod
    def draft_to_staticfeedback_kwargs(cls, draftstring):
        buf = json.loads(draftstring)
        points = buf[0]
        grade = buf[1]
        feedback = buf[2]
        is_approved = buf[3]

        return dict(is_passing_grade=is_approved,
                    grade=grade,
                    points=points,
                    rendered_view=feedback)

        #TODO: .format() crashes when using non-ascii symbols.. need to find a fix since norwegian characters are bound to be used in feedbacks!!

gradeeditor_registry.register(Manual)
