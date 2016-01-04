from crispy_forms import layout
from django import forms
from django.conf import settings
from django.contrib import messages
from django.db.models.functions import Lower, Concat
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.translation import pgettext_lazy, ugettext_lazy
from django_cradmin import crapp
from django_cradmin.crispylayouts import PrimarySubmit
from django_cradmin.viewhelpers import formbase
from django_cradmin.viewhelpers import listbuilderview
from django_cradmin.viewhelpers import listfilter

from devilry.apps.core.models import RelatedStudent, Candidate
from devilry.devilry_admin.cradminextensions.multiselect2 import multiselect2_relatedstudent


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


class RelatedStudentMultiselectTarget(multiselect2_relatedstudent.Target):
    def get_submit_button_text(self):
        return pgettext_lazy('admin create_groups',
                             'Add students')


class OrderRelatedStudentsFilter(listfilter.django.single.select.AbstractOrderBy):
    def get_ordering_options(self):
        if settings.DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND:
            shortname_ascending_label = ugettext_lazy('Order by: Email')
            shortname_descending_label = ugettext_lazy('Order by: Email descending')
        else:
            shortname_ascending_label = ugettext_lazy('Order by: Username')
            shortname_descending_label = ugettext_lazy('Order by: Username descending')

        # NOTE: We use Concat below to get sorting that works even when the user
        #       does not have a fullname, and we use Lower to sort ignoring case.
        return [
            ('', {
                'label': ugettext_lazy('Order by: Name'),
                'order_by': [Lower(Concat('user__fullname', 'user__shortname'))],
            }),
            ('name_descending', {
                'label': ugettext_lazy('Order by: Name descending'),
                'order_by': [Lower(Concat('user__fullname', 'user__shortname')).desc()],
            }),
            ('lastname_ascending', {
                'label': ugettext_lazy('Order by: Last name'),
                'order_by': [Lower('user__lastname')],
            }),
            ('lastname_descending', {
                'label': ugettext_lazy('Order by: Last name descending'),
                'order_by': [Lower('user__lastname').desc()],
            }),
            ('shortname_ascending', {
                'label': shortname_ascending_label,
                'order_by': ['user__shortname'],
            }),
            ('shortname_descending', {
                'label': shortname_descending_label,
                'order_by': ['-user__shortname'],
            }),
        ]


class ManualSelectStudentsForm(forms.Form):
    selected_related_students = forms.ModelMultipleChoiceField(
        queryset=RelatedStudent.objects.none()
    )

    def __init__(self, *args, **kwargs):
        relatedstudents_queryset = kwargs.pop('relatedstudents_queryset')
        super(ManualSelectStudentsForm, self).__init__(*args, **kwargs)
        self.fields['selected_related_students'].queryset = relatedstudents_queryset


class ManualSelectStudentsView(listbuilderview.FilterListMixin, listbuilderview.View):
    model = RelatedStudent
    value_renderer_class = multiselect2_relatedstudent.ItemValue
    paginate_by = 200
    filterlist_class = listfilter.lists.Horizontal

    def dispatch(self, request, *args, **kwargs):
        self.assignment = self.request.cradmin_role
        self.period = self.assignment.parentnode
        return super(ManualSelectStudentsView, self).dispatch(request, *args, **kwargs)

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

    def get_filterlist_template_name(self):
        return 'devilry_admin/assignment/students/create_groups/manual-select-students.django.html'

    def get_label_is_screenreader_only_by_default(self):
        return True

    def add_filterlist_items(self, filterlist):
        filterlist.append(listfilter.django.single.textinput.Search(
            slug='search',
            label=ugettext_lazy('Search'),
            modelfields=['user__fullname', 'user__shortname']))
        filterlist.append(OrderRelatedStudentsFilter(
            slug='orderby',
            label=ugettext_lazy('Order by')))

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'manual-select', kwargs={'filters_string': filters_string})

    def __get_relatedstudents_in_group_on_assignment(self):
        assignment = self.request.cradmin_role
        return Candidate.objects.filter(assignment_group__parentnode=assignment)\
            .values_list('relatedstudent_id', flat=True)

    def get_unfiltered_queryset_for_role(self, role):
        queryset = self.period.relatedstudent_set\
            .select_related('user')\
            .exclude(pk__in=self.__get_relatedstudents_in_group_on_assignment())
        return queryset

    def __get_multiselect_target(self):
        return RelatedStudentMultiselectTarget()

    def get_context_data(self, **kwargs):
        context = super(ManualSelectStudentsView, self).get_context_data(**kwargs)
        context['multiselect_target'] = self.__get_multiselect_target()
        return context

    def post(self, request, *args, **kwargs):
        available_relatedstudents_queryset = self.get_unfiltered_queryset_for_role(
                role=self.request.cradmin_role)
        form = ManualSelectStudentsForm(data=self.request.POST,
                                        relatedstudents_queryset=available_relatedstudents_queryset)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        print()
        print("*" * 70)
        print()
        print(form.cleaned_data['selected_related_students'])
        print()
        print("*" * 70)
        print()
        return redirect(self.request.cradmin_instance.appindex_url('studentoverview'))

    def form_invalid(self, form):
        messages.error(self.request,
                       pgettext_lazy('admin create_groups',
                                     'Oups! Something went wrong. This may happen if someone edited '
                                     'students on the assignment or the semester while you were making '
                                     'your selection. Please try again.'))
        return redirect(self.request.path)


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', ChooseMethod.as_view(), name=crapp.INDEXVIEW_NAME),
        crapp.Url(
            r'^manual-select/(?P<filters_string>.+)?$',
            ManualSelectStudentsView.as_view(),
            name='manual-select'),
    ]
