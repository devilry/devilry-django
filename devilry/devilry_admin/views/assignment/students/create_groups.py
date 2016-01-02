from crispy_forms import layout
from django import forms
from django.http import HttpResponseRedirect
from django.utils.translation import pgettext_lazy
from django_cradmin import crapp
from django_cradmin.crispylayouts import PrimarySubmit
from django_cradmin.viewhelpers import formbase
from django_cradmin.viewhelpers import listbuilderview
from django_cradmin.viewhelpers import listfilter
from django_cradmin.viewhelpers import multiselect2

from devilry.apps.core.models import RelatedStudent, Candidate


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


class RelatedStudentSelectedItem(multiselect2.selected_item_renderer.SelectedItem):
    def get_title(self):
        return self.value.user.fullname

    def get_description(self):
        return self.value.user.shortname


class RelatedStudentItemValue(multiselect2.listbuilder_itemvalues.ItemValue):
    valuealias = 'relatedstudent'
    selected_item_renderer_class = RelatedStudentSelectedItem

    def get_inputfield_name(self):
        return 'selected_related_students'

    def get_title(self):
        return self.relatedstudent.user.fullname

    def get_description(self):
        return self.relatedstudent.user.shortname


class RelatedStudentMultiselectTarget(multiselect2.target_renderer.Target):
    def get_submit_button_text(self):
        return pgettext_lazy('admin create_groups',
                             'Add students')

    def get_with_items_title(self):
        return pgettext_lazy('admin create_groups',
                             'Selected students')

    def get_without_items_text(self):
        return pgettext_lazy('admin create_groups',
                             'No students selected')


class ManualSelectStudentsView(listbuilderview.FilterListMixin, listbuilderview.View):
    model = RelatedStudent
    value_renderer_class = RelatedStudentItemValue
    paginate_by = 20

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

    def add_filterlist_items(self, filterlist):
        filterlist.append(listfilter.django.single.textinput.Search(
            slug='search',
            label='Search',
            label_is_screenreader_only=True,
            modelfields=['user__fullname', 'user__shortname']))

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'manual-select', kwargs={'filters_string': filters_string})

    def __get_users_in_group_on_assignment(self):
        assignment = self.request.cradmin_role
        return Candidate.objects.filter(assignment_group__parentnode=assignment)\
            .values_list('relatedstudent_id', flat=True)

    def get_queryset_for_role(self, role):
        queryset = self.period.relatedstudent_set\
            .order_by('user__fullname')\
            .select_related('user')\
            .exclude(pk__in=self.__get_users_in_group_on_assignment())
        queryset = self.get_filterlist().filter(queryset)
        return queryset

    def __get_multiselect_target(self):
        return RelatedStudentMultiselectTarget()

    def get_context_data(self, **kwargs):
        context = super(ManualSelectStudentsView, self).get_context_data(**kwargs)
        context['multiselect_target'] = self.__get_multiselect_target()
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', ChooseMethod.as_view(), name=crapp.INDEXVIEW_NAME),
        crapp.Url(
            r'^manual-select/(?P<filters_string>.+)?$',
            ManualSelectStudentsView.as_view(),
            name='manual-select'),
    ]
