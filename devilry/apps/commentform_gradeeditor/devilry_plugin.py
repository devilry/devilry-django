"""
A plugin for the CommentForm grade editor. See the class documentation for more details.

@author Svenn-Arne Dragly
"""
import json
from django.conf import settings

from devilry.apps.gradeeditors import (gradeeditor_registry, JsonRegistryItem,
                                       DraftValidationError, ConfigValidationError)
from devilry.apps.markup.parse_markdown import markdown_full



class CommentForm(JsonRegistryItem):
"""
The CommentForm grade editor is based on the Simple Schema/Form grade editor, 
with the addition that comments to the students may be generated directly from 
the selected checkboxes. An administrator may set the checkbox fields up with 
a predefined number of points for each selected checkbox. The number of points 
may be negative to give reduced points when errors are made by the student. 
The number of points are summarized and a limit is set as to how many points 
are needed for approval. General comments may be added in the usual feedback 
box in addition to adjusting the number of point by an arbitrary positive
or negative number.
"""
    gradeeditorid = 'commentform'
    title = 'Comment form'
    description = '<p>Based on the Simple Schema/Form, with the addition of comments for each checkbox. It will generate an automated feedback to the student based on the selected checkboxes. You set up a very simple schema. This schema may contain multiple input fields. An input field is a text (<em>I.E: "Question 2.3"</em>) and corresponding input field (number-input or checkbox). You may choose the number of points required to pass the assignment.</p><p>Examiners fill out this schema and an optional feedback text. A numeric grade (I.E.: <em>64/100</em>) is calculated from their input.</p>'
    config_editor_url = settings.DEVILRY_STATIC_URL + '/commentform_gradeeditor/configeditor.js'
    draft_editor_url = settings.DEVILRY_STATIC_URL + '/commentform_gradeeditor/drafteditor.js'

    @classmethod
    def validate_draft(cls, draftstring, configstring):
        draft = json.loads(draftstring)
        config = json.loads(configstring)

        cls.validate_dict(draft, DraftValidationError, {'values': list,
                                                        'feedback': basestring})
        cls.validate_gradeeditor_key(draft, 'commentform')

        gradeeditor = draft['gradeeditor']
        draftval = draft['values']
        confval = config['formValues']

        for i in xrange(0, len(draftval)):
            if confval[i][0]=='check':
                if not isinstance(draftval[i], bool):
                    errormsg = 'the field labled "' + confval[i][2] + '" has to contain a boolean-value'
                    raise ConfigValidationError(errormsg)

            elif confval[i][0] == 'number':
                if not isinstance(draftval[i], int):
                    errormsg = 'the field labled "' + confval[i][2] + '" has to contain a number 0 or higher'
                    raise ConfigValidationError(errormsg)

                if draftval[i]<0:
                    errormsg = 'the field labled "' + confval[i][2] + '" has to contain a number 0 or higher'
                    raise ConfigValidationError(errormsg)

    @classmethod
    def validate_config(cls, configstring):
        config = cls.decode_configstring(configstring)

        form = config['formValues']
        approvedLimit = config['approvedLimit']

        if len(form) == 0:
            raise ConfigValidationError('You have to specify at least one form-field')

        pointSum = 0
        for entry in form:
            if len(entry) != 4:
                raise ConfigValidationError('You have to specify fieldtype, points, default and label')

            if not isinstance(entry[0], basestring):
                raise ConfigValidationError('You have to specify fieldtype as either "number" or "check"')
            if entry[0] != 'number' and entry[0] != 'check':
                raise ConfigValidationError('You have to specify fieldtype as either "number" or "check"')

            if entry[1] == '':
                raise ConfigValidationError('You have to enter points as a number 0 or higher')

            #if int(entry[1])<0:
            #    raise ConfigValidationError('You have to enter points as a number 0 or higher')

            if not isinstance(entry[2], basestring):
                raise ConfigValidationError('You have to enter the field-label as plain text')

            if entry[2] == '':
                raise ConfigValidationError('You have to enter a default value')
            
            if entry[3] == '':
                raise ConfigValidationError('You have to enter a field-label')

            pointSum+=int(entry[1])

        if not isinstance(approvedLimit, int):
                raise ConfigValidationError('You have to enter points to pass as a number 0 or higher')

        #if approvedLimit < 0:
        #        raise ConfigValidationError('You have to enter points to pass as a number 0 or higher')

        if approvedLimit>pointSum:
            raise ConfigValidationError('Points to pass has to be equal to, or smaller than, the sum of available points')


    @classmethod
    def draft_to_staticfeedback_kwargs(cls, draftstring, configstring):
        #TODO: For now, 'grade' is just set to be points, but all info from configs and drafts is available here, so anything can be shown to the student.
        # might want to add grade-calculation like autograde in the config though..
        draft = json.loads(draftstring)
        config = json.loads(configstring)
        draftval = draft['values']
        confval = config['formValues']
        points = 0

        feedback = ""

        for i in xrange(0, len(draftval)):
            if confval[i][0]=='check':
                if draftval[i]:
                    points+=int(confval[i][1])
                    feedback += markdown_full(confval[i][3]) + "\n"

            elif confval[i][0] == 'number':
                points+=draftval[i]

        is_approved = False
        if points >= config['approvedLimit']:
            is_approved = True

        # Putting the feedback text and the full feedback together
        feedback = markdown_full(draft['feedback']) + "\n" + feedback

        return dict(is_passing_grade=is_approved,
                    grade=points,
                    points=points,
                    rendered_view=feedback)

gradeeditor_registry.register(CommentForm)
