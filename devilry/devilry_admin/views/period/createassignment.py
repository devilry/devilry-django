from datetime import timedelta

from crispy_forms import layout
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.exceptions import ValidationError
from django.db import models
from django.http import Http404
from django.template.loader import render_to_string
from django.utils import timezone
from django_cradmin import crapp
from django_cradmin import crinstance
from django_cradmin.viewhelpers import create
from django_cradmin.viewhelpers import crudbase
from django.utils.translation import ugettext_lazy as _, pgettext_lazy
from django_cradmin.widgets.datetimepicker import DateTimePickerWidget

from devilry.apps.core.models import Assignment
from devilry.utils import datetimeutils
from devilry.utils import nodenamesuggestor


class CreateForm(forms.ModelForm):
    IMPORT_STUDENTS_ALL_FROM_SEMESTER = 'all'
    IMPORT_STUDENTS_NONE = 'none'

    student_import_option = forms.ChoiceField(
        label=_('Import students'),
        required=True,
        choices=[]
    )

    class Meta:
        model = Assignment
        fields = [
            'long_name',
            'short_name',
            'student_import_option',
            'first_deadline',
            'publishing_time',
            'parentnode'
        ]

    def __init__(self, *args, **kwargs):
        self.period = kwargs.pop('period')
        super(CreateForm, self).__init__(*args, **kwargs)
        self.fields['long_name'].help_text = _(
            'Type the name of your assignment.')
        self.fields['short_name'].help_text = _(
            'Up to 20 letters of lowercase english letters (a-z), '
            'numbers, underscore ("_") and hyphen ("-").')

        # Set student import options data.
        self.fields['student_import_option'].help_text = _('Choose how you would like to set up students for the new '
                                                           'assignment. You can add all students from the semester, no '
                                                           'students or copy students and examiners from previous '
                                                           'assignments.')
        self.fields['student_import_option'].choices = []
        self.fields['student_import_option'].choices = self.__create_student_import_choices()

        self.fields['first_deadline'].widget = DateTimePickerWidget(
            buttonlabel_novalue=pgettext_lazy('CrAdmin datetime picker typo fix', 'Select a date/time'),
            required=True,
            minimum_datetime=timezone.now() + timedelta(
                minutes=settings.DEVILRY_ASSIGNMENT_PUBLISHING_TIME_DELAY_MINUTES),
            maximum_datetime=self.period.end_time)
        self.fields['first_deadline'].required = True
        self.fields['first_deadline'].label = _('Set first deadline')
        self.fields['first_deadline'].help_text = _(
            'The first deadline for this assignment. This is shared by all the '
            'students on the assignment.'
        )

        # We ignore this, we just need to include it to be able to
        # change the value in clean()
        self.fields['publishing_time'].widget = forms.HiddenInput()
        self.fields['publishing_time'].required = False

        # We ignore this, we just need to include it to be able to
        # change the value in clean()
        self.fields['parentnode'].widget = forms.HiddenInput()
        self.fields['parentnode'].required = False

    @property
    def default_import_options(self):
        return [
            ('', '----'),
            ('all', _('All students on semester')),
            ('none', _('No students'))
        ]

    def __create_grouped_choice_tuple_for_assignment(self, assignment):
        return (
            assignment.long_name,
            tuple([
                ('{}_all'.format(assignment.id), _('Copy all students')),
                ('{}_passed'.format(assignment.id), _('Copy students with passing grade'))
            ]))

    def __create_student_import_choices(self):
        assignment_queryset = Assignment.objects \
            .filter_is_active() \
            .filter(parentnode=self.period)\
            .order_by('-first_deadline')
        choices_list = self.default_import_options
        for assignment in assignment_queryset:
            choices_list.append(self.__create_grouped_choice_tuple_for_assignment(assignment=assignment))
        return choices_list

    def clean(self):
        cleaned_data = super(CreateForm, self).clean()
        first_deadline = cleaned_data.get('first_deadline', None)
        cleaned_data['parentnode'] = self.period
        if first_deadline:
            if self.period.start_time > timezone.now():
                publishing_time = self.period.start_time + timedelta(
                    minutes=settings.DEVILRY_ASSIGNMENT_PUBLISHING_TIME_DELAY_MINUTES)
                self.__compare_deadline_and_publishing_time(
                    period=self.period, publishing_time=publishing_time, first_deadline=first_deadline
                )
            else:
                publishing_time = timezone.now() + timedelta(
                    minutes=settings.DEVILRY_ASSIGNMENT_PUBLISHING_TIME_DELAY_MINUTES)
                self.__compare_deadline_and_publishing_time(
                    period=self.period, publishing_time=publishing_time, first_deadline=first_deadline
                )
            cleaned_data['publishing_time'] = publishing_time
        return cleaned_data

    def __compare_deadline_and_publishing_time(self, period, publishing_time, first_deadline):
        if first_deadline < publishing_time:
            if period.start_time > timezone.now():
                self.__raise_validation_error(start_time=period.start_time)
            else:
                self.__raise_validation_error(start_time=timezone.now())

    def __raise_validation_error(self, start_time):
        publishing_time_naturaltime = naturaltime(start_time + timedelta(
            minutes=settings.DEVILRY_ASSIGNMENT_PUBLISHING_TIME_DELAY_MINUTES,
            # We add some seconds to make the naturaltime show the correct amount of
            # hours/minutes because at least a small fraction of time will pass between
            # creating the datetime and the formatting in the naturaltime function.
            seconds=10))
        raise ValidationError({
            # Translators: The "delay" is formatted as "X hours/minutes from now"
            'first_deadline': _('First deadline must be at least %(delay)s.') % {
                'delay': publishing_time_naturaltime
            }
        })


class CreateView(crudbase.OnlySaveButtonMixin, create.CreateView):
    form_class = CreateForm
    model = Assignment
    suggested_deadlines_template_name = 'devilry_admin/period/createassignment/suggested_deadlines.django.html'
    helpbox_template_name = 'devilry_admin/period/createassignment/helpbox.django.html'
    success_message_template_name = 'devilry_admin/period/createassignment/success_message.django.html'
    template_name = 'devilry_admin/period/createassignment/createassignment.django.html'

    def dispatch(self, *args, **kwargs):
        self.period = self.request.cradmin_role
        self.previous_assignment = self.period.assignments \
            .exclude(first_deadline=None) \
            .order_by('first_deadline') \
            .last()
        return super(CreateView, self).dispatch(*args, **kwargs)

    def get_pagetitle(self):
        return u'{} - {}'.format(self.get_pageheading(), self.period.get_path())

    def get_pageheading(self):
        return _('Create new assignment')

    def get_form_kwargs(self):
        kwargs = super(CreateView, self).get_form_kwargs()
        kwargs['period'] = self.request.cradmin_role
        return kwargs

    def get_initial(self):
        initial = super(CreateView, self).get_initial()
        if self.previous_assignment:
            namesuggestion = nodenamesuggestor.Suggest(long_name=self.previous_assignment.long_name,
                                                       short_name=self.previous_assignment.short_name)
            if namesuggestion.has_suggestion():
                namecollision_queryset = self.period.assignments.filter(
                    models.Q(long_name=namesuggestion.suggested_long_name) |
                    models.Q(short_name=namesuggestion.suggested_short_name))
                if not namecollision_queryset.exists():
                    initial['long_name'] = namesuggestion.suggested_long_name
                    initial['short_name'] = namesuggestion.suggested_short_name
        return initial

    def __get_suggested_deadlines(self):
        suggested_deadlines = []
        if self.previous_assignment:
            if self.previous_assignment.first_deadline > timezone.now():
                first_suggested_deadline = self.previous_assignment.first_deadline + timedelta(days=7)
            else:
                first_suggested_deadline = datetimeutils.datetime_with_same_day_of_week_and_time(
                    weekdayandtimesource_datetime=self.previous_assignment.first_deadline,
                    target_datetime=timezone.now())
            suggested_deadlines.append(first_suggested_deadline)
            for days_forward in range(7, (7 * 4), 7):
                suggested_deadline = first_suggested_deadline + timedelta(days=days_forward)
                suggested_deadlines.append(suggested_deadline)
        return suggested_deadlines

    def __render_suggested_deadlines_box(self):
        return render_to_string(self.suggested_deadlines_template_name, {
            'suggested_deadlines': self.__get_suggested_deadlines()
        })

    def __render_help_box(self):
        return render_to_string(self.helpbox_template_name)

    def get_field_layout(self):
        return [
            layout.Div(
                layout.Field('long_name', placeholder=_('Example: Assignment 1'),
                             focusonme='focusonme'),
                layout.Field('short_name', placeholder=_('Example: assignment1')),
                layout.Field('student_import_option'),
                # layout.HTML(self.__render_help_box()),
                layout.Div(
                    layout.Div(
                        layout.Field('first_deadline'),
                        css_class='col-sm-6'
                    ),
                    layout.HTML(self.__render_suggested_deadlines_box()),
                    css_class='row'
                ),
                css_class='cradmin-globalfields'
            )
        ]

    def get_success_url(self):
        return crinstance.reverse_cradmin_url(
            instanceid='devilry_admin_assignmentadmin',
            appname='overview',
            roleid=self.created_assignment.id
        )

    def add_success_messages(self, object):
        messages_template_context = {'assignment': object, 'group_count': object.assignmentgroups.count()}
        messages.success(
            self.request,
            render_to_string(self.success_message_template_name, context=messages_template_context))

    def __get_selected_assignment_from_import_option(self, student_import_option):
        try:
            assignment_id = int(student_import_option.split('_')[0])
        except ValueError:
            raise ValidationError(_('Something went wrong'))
        try:
            assignment = Assignment.objects\
                .filter_is_active()\
                .filter(parentnode=self.period)\
                .get(id=assignment_id)
        except Assignment.DoesNotExist:
            raise Http404()
        return assignment

    def __copy_all_students_from_assignment(self, created_assignment, student_import_option):
        """
        Import group setup from another assignment, including examiners.
        """
        import_from_assignment = self.__get_selected_assignment_from_import_option(
            student_import_option=student_import_option)
        created_assignment.copy_groups_from_another_assignment(
            sourceassignment=import_from_assignment)

    def __copy_students_with_passing_grade_from_assignment(self, created_assignment, student_import_option):
        """
        Import group setup only for groups that passed from another assignment, including examiners.
        """
        import_from_assignment = self.__get_selected_assignment_from_import_option(
            student_import_option=student_import_option)
        created_assignment.copy_groups_from_another_assignment(
            sourceassignment=import_from_assignment, passing_grade_only=True)

    def save_object(self, form, commit=True):
        assignment = super(CreateView, self).save_object(form=form, commit=commit)
        student_import_option = form.cleaned_data['student_import_option']
        if student_import_option == self.form_class.IMPORT_STUDENTS_ALL_FROM_SEMESTER:
            assignment.create_groups_from_relatedstudents_on_period()
        elif student_import_option.endswith('_all'):
            self.__copy_all_students_from_assignment(
                created_assignment=assignment, student_import_option=student_import_option)
        elif student_import_option.endswith('_passed'):
            self.__copy_students_with_passing_grade_from_assignment(
                created_assignment=assignment, student_import_option=student_import_option)
        elif student_import_option == 'none':
            pass
        return assignment

    def form_saved(self, object):
        self.created_assignment = object

    def get_backlink_url(self):
        return crinstance.reverse_cradmin_url(
            instanceid='devilry_admin_periodadmin',
            appname='overview',
            roleid=self.request.cradmin_role.id
        )

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['backlink_url'] = self.get_backlink_url()
        context['import_option_not_selected_text'] = _('Choose how you would like to set up students for the new '
                                                       'assignment. You can add all students from the semester, no '
                                                       'students or copy students and examiners from previous '
                                                       'assignments.')
        context['import_option_all_selected_text'] = _('Will import all students on the semester if any.')
        context['import_option_none_selected_text'] = _('Will not import any students. You have to manually configure '
                                                        'students from the assignment-dashboard.')
        context['import_option_assignment_all_selected_text'] = _('Copy all students from this assignment. '
                                                                  'This will copy the group and examiner setup from '
                                                                  'the selected assignment.')
        context['import_option_assignment_passing_selected_text'] = _('Copy students from this assignment with passing '
                                                                      'grade only. This will copy the group and '
                                                                      'examiner setup from the selected assignment.')
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', CreateView.as_view(), name=crapp.INDEXVIEW_NAME)
    ]
