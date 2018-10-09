import logging

from crispy_forms import layout
from django import forms
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
from django.utils.translation import pgettext_lazy, ugettext_lazy
from django.views.generic import TemplateView
from django_cradmin import crapp
from django_cradmin.crispylayouts import PrimarySubmit, CradminFormHelper
from django_cradmin.viewhelpers import listbuilder
from django_cradmin.viewhelpers import multiselect2view

from devilry.apps.core.models import Candidate, AssignmentGroup, RelatedStudent
from devilry.devilry_admin.cradminextensions.listbuilder import listbuilder_relatedstudent
from devilry.devilry_admin.cradminextensions.multiselect2 import multiselect2_relatedstudent

from devilry.devilry_admin.views.assignment.students.create_groups_accumulated_score import SelectAssignmentsView, \
    PreviewRelatedstudentsListView

logger = logging.getLogger(__name__)


class ChoosePeriodItemValue(listbuilder.itemvalue.TitleDescription):
    valuealias = 'period'
    template_name = 'devilry_admin/assignment/students/create_groups/choose-period-item-value.django.html'

    def get_extra_css_classes_list(self):
        return ['devilry-django-cradmin-listbuilder-itemvalue-titledescription-lg']

    def get_title(self):
        return pgettext_lazy('admin create_groups',
                             'Select students from %(subject)s %(period)s') % {
            'subject': self.period.subject.long_name,
            'period': self.period.long_name
        }


class ChooseAssignmentItemValue(listbuilder.itemvalue.TitleDescription):
    valuealias = 'assignment'
    template_name = 'devilry_admin/assignment/students/create_groups/choose-assignment-item-value.django.html'

    def get_title(self):
        return pgettext_lazy('admin create_groups',
                             'Select students from %(assignment)s') % {
            'assignment': self.assignment.long_name
        }


class ChooseAccumulatedAssignmentScore(listbuilder.itemvalue.TitleDescription):
    template_name = 'devilry_admin/assignment/students/create_groups/choose-accumulated-score.django.html'

    def get_title(self):
        return pgettext_lazy('admin create_groups_accumulated_score_on_assignments',
                             'Add students based on their total score')

    def get_description(self):
        return pgettext_lazy('admin create_groups_accumulated_score_on_assignments',
                             'Add students based on their total score across assignments you '
                             'select from this semester.')


class ChooseMethod(TemplateView):
    template_name = 'devilry_admin/assignment/students/create_groups/choose-method.django.html'

    def get_pagetitle(self):
        assignment = self.request.cradmin_role
        return pgettext_lazy('admin create_group', 'Add students to %(assignment)s') % {
            'assignment': assignment.get_path()
        }

    def get_pageheading(self):
        return pgettext_lazy('admin create_group', 'Add students')

    def get_page_subheading(self):
        return pgettext_lazy('admin create_group',
                             'Please select how you would like to add students. You will get a '
                             'preview of your choice on the next page before any students are added.')

    def dispatch(self, request, *args, **kwargs):
        self.assignment = self.request.cradmin_role
        self.period = self.assignment.parentnode
        return super(ChooseMethod, self).dispatch(request, *args, **kwargs)

    def __make_listbuilder_list(self):
        listbuilder_list = listbuilder.lists.RowList()

        # Choice for adding students from period.
        listbuilder_list.append(listbuilder.itemframe.DefaultSpacingItemFrame(
            ChoosePeriodItemValue(value=self.period)))

        # Choices for adding all students or only students with passing grade from assignments.
        assignments = self.period.assignments\
            .order_by('-publishing_time')\
            .exclude(pk=self.assignment.pk)
        for assignment in assignments:
            listbuilder_list.append(
                listbuilder.itemframe.DefaultSpacingItemFrame(
                    ChooseAssignmentItemValue(value=assignment)))

        # Choice for adding students by their accumulated score across selected assignments.
        listbuilder_list.append(listbuilder.itemframe.DefaultSpacingItemFrame(
            ChooseAccumulatedAssignmentScore(value=self.request.cradmin_role)
        ))
        return listbuilder_list

    def get_context_data(self, **kwargs):
        context = super(ChooseMethod, self).get_context_data(**kwargs)
        context['listbuilder_list'] = self.__make_listbuilder_list()
        context['pagetitle'] = self.get_pagetitle()
        context['pageheading'] = self.get_pageheading()
        context['page_subheading'] = self.get_page_subheading()
        return context


class CreateGroupsViewMixin(object):
    #: If this is ``True``, we remove all AssignmentGroups before
    #: adding new groups instead of just adding groups for students
    #: not already on the assignment. If this is ``True``, RelatedStudents
    #: already on the assignment are note excluded from the valid set
    #: of students to add to the assignment.
    replace_groups = False

    form_invalid_message = pgettext_lazy(
        'admin create_groups',
        'Oups! Something went wrong. This may happen if someone edited '
        'students on the assignment or the semester while you were making '
        'your selection. Please try again.')

    def dispatch(self, request, *args, **kwargs):
        self.assignment = self.request.cradmin_role
        self.period = self.assignment.parentnode
        return super(CreateGroupsViewMixin, self).dispatch(request, *args, **kwargs)

    def __get_relatedstudents_in_group_on_assignment(self):
        assignment = self.request.cradmin_role
        return Candidate.objects.filter(assignment_group__parentnode=assignment)\
            .values_list('relatedstudent_id', flat=True)

    def get_unfiltered_queryset_for_role(self, role):
        queryset = self.period.relatedstudent_set\
            .prefetch_syncsystemtag_objects()\
            .filter(active=True)\
            .select_related('user')
        if not self.replace_groups:
            queryset = queryset.exclude(pk__in=self.__get_relatedstudents_in_group_on_assignment())
        return queryset

    def get_form_class(self):
        return multiselect2_relatedstudent.SelectRelatedStudentsForm

    def get_form_kwargs(self):
        available_relatedstudents_queryset = self.get_unfiltered_queryset_for_role(
            role=self.request.cradmin_role)
        kwargs = {'relatedstudents_queryset': available_relatedstudents_queryset}
        if self.request.method == 'POST':
            kwargs['data'] = self.request.POST
        return kwargs

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs())

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def __remove_all_existing_groups(self):
        if self.assignment.assignmentgroups.filter_with_published_feedback_or_comments().exists():
            raise Http404()
        self.assignment.assignmentgroups.all().delete()

    def create_groups_with_candidate_and_feedbackset(self, relatedstudent_queryset):
        if self.replace_groups:
            self.__remove_all_existing_groups()
        assignment = self.request.cradmin_role
        return AssignmentGroup.objects.bulk_create_groups(
            created_by_user=self.request.user,
            assignment=assignment,
            relatedstudents=list(relatedstudent_queryset))

    def get_success_url(self):
        return self.request.cradmin_instance.appindex_url('studentoverview')

    def form_valid(self, form):
        self.create_groups_with_candidate_and_feedbackset(
            relatedstudent_queryset=form.cleaned_data['selected_items'])
        return redirect(self.get_success_url())

    def get_error_url(self):
        raise NotImplementedError()

    def form_invalid(self, form):
        messages.error(self.request, self.form_invalid_message)
        logger.warning('%s.%s failed to validate. '
                       'This should not happen unless a user was removed '
                       'from the semester while the user selected students, '
                       'or if multiple admins edited/added students at the same time. '
                       'The user that experienced this error: %s (userid=%s). '
                       'Form validation error messages: %r',
                       self.__class__.__module__, self.__class__.__name__,
                       self.request.user.shortname,
                       self.request.user.id,
                       form.errors.as_data())
        return redirect(self.get_error_url())


class ConfirmView(CreateGroupsViewMixin,
                  listbuilder_relatedstudent.VerticalFilterListView):
    value_renderer_class = listbuilder_relatedstudent.ReadOnlyItemValue

    SELECTED_STUDENTS_ALL_ON_ASSIGNMENT = 'all_on_assignment'
    SELECTED_STUDENTS_PASSING_GRADE_ON_ASSIGNMENT = 'passing_grade_on_assignment'
    SELECTED_STUDENTS_RELATEDSTUDENTS = 'relatedstudents'
    SELECTED_STUDENTS_CHOICES_MAP = {
        SELECTED_STUDENTS_ALL_ON_ASSIGNMENT: ugettext_lazy('All students on %(assignment)s'),
        SELECTED_STUDENTS_PASSING_GRADE_ON_ASSIGNMENT: ugettext_lazy('Students with passing grade on %(assignment)s'),
        SELECTED_STUDENTS_RELATEDSTUDENTS: ugettext_lazy('All students on %(period)s'),
    }

    def get_period(self):
        return self.assignment.period

    def dispatch(self, request, *args, **kwargs):
        self.from_assignment = None
        return super(ConfirmView, self).dispatch(request, *args, **kwargs)

    def get_filterlist_template_name(self):
        return 'devilry_admin/assignment/students/create_groups/confirm.django.html'

    def get_pagetitle(self):
        return pgettext_lazy('admin create_groups',
                             'Confirm that you want to add the following students to %(assignment)s') % {
            'assignment': self.assignment.get_path()
        }

    def get_pageheading(self):
        return pgettext_lazy('admin create_groups',
                             'Confirm that you want to add the following students to %(assignment)s') % {
            'assignment': self.assignment.long_name
        }

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'confirm',
            kwargs={'selected_students': self.kwargs['selected_students'],
                    'filters_string': filters_string})

    def __get_assignment_id_form_class(self):
        assignment_queryset = self.period.assignments.exclude(id=self.assignment.id)

        class AssignmentIdForm(forms.Form):
            assignment = forms.ModelChoiceField(
                queryset=assignment_queryset,
                required=True
            )

        return AssignmentIdForm

    def __get_assignment_id_form(self):
        form_class = self.__get_assignment_id_form_class()
        return form_class(data=self.request.GET)

    def __filter_students_on_assignment(self,
                                        assignment,
                                        relatedstudents_queryset,
                                        only_passing_grade):
            matching_candidates = Candidate.objects\
                .filter(assignment_group__parentnode=assignment)
            if only_passing_grade:
                matching_candidates = matching_candidates\
                    .filter_has_passing_grade(assignment=assignment)
            matching_relatedstudent_ids = matching_candidates\
                .values_list('relatedstudent_id', flat=True)
            matching_relatedstudent_ids = set(matching_relatedstudent_ids)
            return relatedstudents_queryset.filter(id__in=matching_relatedstudent_ids)

    def __filter_selected_students_on_assignment(self, relatedstudents_queryset,
                                                 only_passing_grade):
        form = self.__get_assignment_id_form()
        if form.is_valid():
            self.from_assignment = form.cleaned_data['assignment']
            return self.__filter_students_on_assignment(
                assignment=self.from_assignment,
                relatedstudents_queryset=relatedstudents_queryset,
                only_passing_grade=only_passing_grade)
        else:
            raise Http404('Invalid assignment_id')

    def get_unfiltered_queryset_for_role(self, role):
        if self.request.method == 'POST':
            return super(ConfirmView, self)\
                .get_unfiltered_queryset_for_role(role=role)
        else:
            selected_students = self.kwargs['selected_students']
            relatedstudents_queryset = super(ConfirmView, self)\
                .get_unfiltered_queryset_for_role(role=role)
            if selected_students == self.SELECTED_STUDENTS_ALL_ON_ASSIGNMENT:
                queryset = self.__filter_selected_students_on_assignment(
                    relatedstudents_queryset=relatedstudents_queryset,
                    only_passing_grade=False)
            elif selected_students == self.SELECTED_STUDENTS_PASSING_GRADE_ON_ASSIGNMENT:
                queryset = self.__filter_selected_students_on_assignment(
                    relatedstudents_queryset=relatedstudents_queryset,
                    only_passing_grade=True)
            elif selected_students == self.SELECTED_STUDENTS_RELATEDSTUDENTS:
                queryset = relatedstudents_queryset
            else:
                raise Http404('Invalid selected_students.')
            return queryset

    def get_error_url(self):
        return self.request.cradmin_app.reverse_appindexurl()

    def __get_selected_students_label(self):
        selected_students = self.kwargs['selected_students']
        if self.from_assignment:
            formatting_dict = {
                'assignment': self.from_assignment.long_name,
            }
        else:
            formatting_dict = {
                'period': self.period.get_path(),
            }
        return self.SELECTED_STUDENTS_CHOICES_MAP[selected_students] % formatting_dict

    def get_form_kwargs(self):
        kwargs = super(ConfirmView, self).get_form_kwargs()
        if self.request.method == 'GET':
            relatedstudents_queryset = kwargs['relatedstudents_queryset']
            kwargs['initial'] = {
                'selected_items': relatedstudents_queryset.values_list('id', flat=True),
            }
        return kwargs

    def __get_formhelper(self):
        helper = CradminFormHelper()
        helper.form_class = 'django-cradmin-form-wrapper devilry-django-cradmin-form-wrapper-top-bottom-spacing'
        helper.form_id = 'devilry_admin_create_groups_confirm_form'
        helper.layout = layout.Layout(
            'selected_items',
            PrimarySubmit('add_students', pgettext_lazy('admin create_groups', 'Add students'))
        )
        helper.form_action = self.request.get_full_path()
        return helper

    def get_context_data(self, **kwargs):
        context = super(ConfirmView, self).get_context_data(**kwargs)
        context['no_students_found'] = not self.get_unfiltered_queryset_for_role(
            role=self.request.cradmin_role).exists()
        context['selected_students_label'] = self.__get_selected_students_label()
        context['formhelper'] = self.__get_formhelper()
        context['form'] = self.get_form()
        return context


class RelatedStudentMultiselectTarget(multiselect2_relatedstudent.Target):
    def get_submit_button_text(self):
        return pgettext_lazy('admin create_groups',
                             'Add students')


class ManualSelectStudentsView(listbuilder_relatedstudent.AddFilterListItemsMixin,
                               CreateGroupsViewMixin,
                               multiselect2view.ListbuilderFilterView):
    """
    View used to manually select students when creating groups.
    """

    value_renderer_class = multiselect2_relatedstudent.ItemValue
    template_name = 'devilry_admin/assignment/students/create_groups/manual-select-students.django.html'
    model = RelatedStudent

    def get_period(self):
        return self.assignment.period

    def get_pagetitle(self):
        return pgettext_lazy('admin create_groups',
                             'Select the students you want to add to %(assignment)s') % {
            'assignment': self.assignment.get_path()
        }

    def get_pageheading(self):
        return pgettext_lazy('admin create_groups',
                             'Select the students you want to add to %(assignment)s') % {
            'assignment': self.assignment.long_name
        }

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'manual-select', kwargs={'filters_string': filters_string})

    def get_target_renderer_class(self):
        return RelatedStudentMultiselectTarget

    def get_error_url(self):
        return self.request.cradmin_app.reverse_appurl('manual-select')


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', ChooseMethod.as_view(), name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^confirm/(?P<selected_students>\w+)/(?P<filters_string>.+)?$',
                  ConfirmView.as_view(),
                  name='confirm'),
        crapp.Url(
            r'^manual-select/(?P<filters_string>.+)?$',
            ManualSelectStudentsView.as_view(),
            name='manual-select'),
        crapp.Url(
            r'^accumulated-score/select-assignments',
            SelectAssignmentsView.as_view(),
            name='accumulated-score-select-assignments'
        ),
        crapp.Url(
            r'^accumulated-score/preview',
            PreviewRelatedstudentsListView.as_view(),
            name='accumulated-score-preview'
        )
    ]
