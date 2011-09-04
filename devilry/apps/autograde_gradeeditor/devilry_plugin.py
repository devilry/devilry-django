import json
from django.conf import settings

from devilry.apps.gradeeditors import (gradeeditor_registry, JsonRegistryItem,
                                       DraftValidationError, ConfigValidationError)
from devilry.apps.markup.parse_markdown import markdown_full



class Autograde(JsonRegistryItem):
    """
    Serves as a minimal example of a grade editor, and as a well suited grade
    editor for use in test cases.
    """
    gradeeditorid = 'autograde'
    title = 'Automatic grading'
    description = 'A gradeeditor where the examiner sets the number of points earned, and the grade is automatically set, using values given by an admin.'
    config_editor_url = settings.DEVILRY_STATIC_URL + '/autograde_gradeeditor/configeditor.js'
    draft_editor_url = settings.DEVILRY_STATIC_URL + '/autograde_gradeeditor/drafteditor.js'

    @classmethod
    def getGrade(cls, points, grades):
        retval = ''
        retpoints = 0
        for grade in grades:
            if points >= int(grade[1]) and int(grade[1]) >= retpoints:
                retval = grade[0]
                retpoints = int(grade[1])

        return retval

    @classmethod
    def validate_config(cls, configstring):
        config = cls.decode_configstring(configstring)

        if config['maxpoints'] < 0:
            raise ConfigValidationError('Maximum points must be a number higher than 0')

        if config['approvedlimit'] < 0:
            raise ConfigValidationError('Points to pass must be a number higher than 0')

        if config['approvedlimit'] > config['maxpoints']:
            raise ConfigValidationError('Maximum points must be smaller than points to pass')

        if len(config['grades']) == 0:
            raise ConfigValidationError('You have to enter at least one grade')

        hasZeroGrade = False

        for grade in config['grades']:
            if grade[0] == '':
                raise ConfigValidationError('Grade-name cannot be empty')

            if grade[1] == '':
                raise ConfigValidationError('Grade-value cannot be empty')

            if int(grade[1]) > config['maxpoints']:
                raise ConfigValidationError("Grade-value cannot be higher than maxpoints, grade-value = '{}' , maxpoints = '{}' ".format(grade[1], config['maxpoints']))

            if grade[1] < 0:
                raise ConfigValidationError('Grade-value cannot be smaller than 0')

            if int(grade[1]) == 0:
                hasZeroGrade = True

        if not hasZeroGrade:
            raise ConfigValidationError("You have to enter a grade with pointlimit 0")



    @classmethod
    def validate_draft(cls, draftstring, configstring):
        config = cls.decode_configstring(configstring)
        draft = json.loads(draftstring)
        points = draft['points']
        feedback = draft['feedback']

        cls.validate_dict(draft, DraftValidationError, {'points': int,
                                                        'feedback': basestring})
        cls.validate_gradeeditor_key(draft, 'autograde')

        if points > config['maxpoints'] or points < 0:
            raise DraftValidationError('The points-field must be a value between 0 and {}'.format(config['maxpoints']))


    @classmethod
    def draft_to_staticfeedback_kwargs(cls, draftstring, configstring):
        config = cls.decode_configstring(configstring)
        buf = json.loads(draftstring)
        points = buf['points']
        feedback = buf['feedback']

        grade = cls.getGrade(points, config['grades'])

        is_approved = False
        if points >= config['approvedlimit']:
            is_approved = True

        return dict(is_passing_grade=is_approved,
                    grade=grade,
                    points=points,
                    rendered_view=markdown_full(feedback))

gradeeditor_registry.register(Autograde)
