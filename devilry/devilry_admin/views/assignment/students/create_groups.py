from crispy_forms import layout
from django import forms
from django.http import HttpResponseRedirect
from django.utils.translation import pgettext_lazy
from django_cradmin import crapp
from django_cradmin.crispylayouts import PrimarySubmit
from django_cradmin.viewhelpers import formbase


class ChooseMethod(formbase.FormView):
    template_name = 'devilry_admin/assignment/students/create_groups/choose-method.django.html'

    def dispatch(self, request, *args, **kwargs):
        self.assignment = self.request.cradmin_role
        self.period = self.assignment.parentnode
        return super(ChooseMethod, self).dispatch(request, *args, **kwargs)

    def __make_copy_from_assignment_choice(self, assignment):
        copy_passing_value = 'copy-passing-from-assignment-{}'.format(assignment.id)
        copy_passing_label = pgettext_lazy('admin create_groups',
                                           'Students with passing grade on %(assignment)s') % {
            'assignment': assignment.long_name
        }
        copy_all_value = 'copy-all-from-assignment-{}'.format(assignment.id)
        copy_all_label = pgettext_lazy('admin create_groups',
                                       'All students registered on %(assignment)s') % {
            'assignment': assignment.long_name
        }
        return (
            pgettext_lazy('admin create_groups', 'Copy from %(assignment)s') % {
                'assignment': assignment.long_name
            },
            (
                (copy_passing_value, copy_passing_label),
                (copy_all_value, copy_all_label),
            )
        )

    def get_other_assignments_in_period_method_choices(self):
        assignments = self.period.assignments\
            .order_by('-publishing_time')\
            .exclude(pk=self.assignment.pk)
        return [self.__make_copy_from_assignment_choice(assignment)
                for assignment in assignments]

    def get_method_choices(self):
        choices = [
            ('all-from-period', pgettext_lazy(
                    'admin create_groups',
                    'All students registered on %(semester)s') % {'semester': self.period.get_path()}),
            ('select-manually', pgettext_lazy(
                    'admin create_groups',
                    'Select manually'))
        ]
        choices.extend(self.get_other_assignments_in_period_method_choices())
        return choices

    def get_form_class(self):
        method_choices = self.get_method_choices()

        class SelectMethodForm(forms.Form):
            method = forms.ChoiceField(
                required=True,
                label=pgettext_lazy('devilry_admin create_groups', 'How would you like to add students?'),
                initial=method_choices[0][0],
                choices=method_choices
            )

        return SelectMethodForm

    def get_field_layout(self):
        return [
            layout.Div(
                'method',
                css_class='cradmin-globalfields')
        ]

    def get_buttons(self):
        return [
            PrimarySubmit('add-students',
                          pgettext_lazy('admin create_groups', 'Add students')),
        ]

    def form_valid(self, form):
        # ... do something with the form ...
        return HttpResponseRedirect('/some/view')


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', ChooseMethod.as_view(), name=crapp.INDEXVIEW_NAME)
    ]
