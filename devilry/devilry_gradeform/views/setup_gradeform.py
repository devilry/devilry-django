import json
from xml.sax.saxutils import quoteattr

from crispy_forms import layout
from django.template.loader import render_to_string
from cradmin_legacy import renderable
from cradmin_legacy.viewhelpers import create
from markdown import serializers


class SetupGradeForm(renderable.AbstractRenderable, create.CreateView):
    """

    """
    template_name = "devilry_gradeform/setup.gradeform.django.html"
    fields=['text']

    def __init__(self, assignment):
        self.assignment = assignment

    def get_template_context_object(self, request=None):
        """

        :param request:
        :return:
        """
        context = super(SetupGradeForm, self).get_context_data()
        context['test'] = 'a test context object'

        context['gradeform_json'] = json.loads(self.assignment.gradeform_setup_json)
        # context['gradeform_json'] = self.get_json_iterable()

        return context

    def get_field_layout(self):
        """

        :return:
        """
        return [
            layout.Fieldset(
                '',
                layout.Div(
                    layout.Div(
                        'text',
                        # css_class='panel-body'
                    ),
                    # css_class='panel panel-default'
                ),
                layout.Div(
                    layout.Div(*self.get_buttons()),
                    css_class="col-xs-12 text-right"
                ),
                css_class='comment-form-container'
            )
        ]

    def get_buttons(self):
        """

        :return:
        """
        return [
            layout.Submit(
                'student_add_comment',
                _('Add comment'),
                css_class='btn btn-success')
        ]