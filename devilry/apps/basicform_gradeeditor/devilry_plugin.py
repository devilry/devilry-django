import json
from django.conf import settings

from devilry.apps.gradeeditors import (gradeeditor_registry, JsonRegistryItem,
                                       DraftValidationError, ConfigValidationError)
from devilry.apps.markup.parse_markdown import markdown_full



class Approved(JsonRegistryItem):
    gradeeditorid = 'basicform'
    title = 'Basicform Editor'
    description = 'An editor where admin can set up different fields for feedback for different parts of an assignment'
    config_editor_url = settings.DEVILRY_STATIC_URL + '/basicform_gradeeditor/configeditor.js'
    draft_editor_url = settings.DEVILRY_STATIC_URL + '/basicform_gradeeditor/drafteditor.js'

    @classmethod
    def validate_draft(cls, draftstring, configstring):
        pass

    @classmethod
    def validate_config(cls, configstring):
        config = cls.decode_configstring(configstring)

        form = config['formValues']

        if len(form) == 0:
            raise ConfigValidationError('You have to specify at least one form-field')

        for entry in form:
            if len(entry) != 3:
                raise ConfigValidationError('You have to specify fieldtype, points and label')

            if not isinstance(entry[0], basestring):
                raise ConfigValidationError('You have to specify fieldtype as either "number" or "check"')

            if entry[0] != 'number' and entry[0] != 'check':
                raise ConfigValidationError('You have to specify fieldtype as either "number" or "check"')

            if entry[1] == '':
                raise ConfigValidationError('You have to enter points as a number above 0')

            if int(entry[1])<0:
                raise ConfigValidationError('You have to enter points as a number above 0')

            if not isinstance(entry[2], basestring):
                raise ConfigValidationError('You have to enter the field-label as plain text')

            if entry[2] == '':
                raise ConfigValidationError('You have to enter a field-label')


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
