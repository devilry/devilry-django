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
    title = 'Automatic grading'
    description = 'A gradeeditor where the examiner sets the number of points earned, and the grade is automatically set.'
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
        cls.validate_dict(config, ConfigValidationError, {'maxpoints': int,
                                                          'grades': list,
                                                          'approvedlimit': int})


        if config['approvedlimit'] > config['maxpoints']:
            raise ConfigValidationError('The approvedlimit-value must be smaller than the maxpoints-value')

        if config['maxpoints'] < 0:
            raise ConfigValidationError('maxpoints-value must be higher than 0')

        if config['approvedlimit'] < 0:
            raise ConfigValidationError('The approvedlimit-value must be higher than 0')

        for grade in config['grades']:
            if grade[0] == '':
                raise ConfigValidationError('grade-name cannot be empty')

            if grade[1] == '':
                raise ConfigValidationError('grade-value cannot be empty')

            if int(grade[1]) > config['maxpoints']:
                raise ConfigValidationError("grade-value cannot be higher than maxpoints, grade-value = '{}' , maxpoints = '{}' ".format(grade[1], config['maxpoints']))

            if grade[1] < 0:
                raise ConfigValidationError('grade-value cannot be smaller than 0')



    @classmethod
    def validate_draft(cls, draftstring, configstring):
        config = cls.decode_configstring(configstring)
        buf = json.loads(draftstring)
        points = buf['points']
        feedback = buf['feedback']

        if not isinstance(points, int):
            raise DraftValidationError('The points-field must contain a number.')

        if points > config['maxpoints'] or points < 0:
            raise DraftValidationError('The points-field must be a value between 0 and {}'.format(config['maxpoints']))

        if not isinstance(feedback, basestring):
            raise DraftValidationError('The feedback-field must contain a feedback-text.')

        if feedback == '':
            raise DraftValidationError('The feedback-field must contain a feedback-text')


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
                    rendered_view=feedback)

gradeeditor_registry.register(Manual)
