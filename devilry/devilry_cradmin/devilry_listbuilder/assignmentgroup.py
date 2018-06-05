from django.utils.translation import ugettext_lazy
from django_cradmin.viewhelpers import listbuilder
from django_cradmin.viewhelpers import multiselect2

from devilry.apps.core.models import Assignment


class FullyAnonymousSubjectAdminItemValueMixin(object):
    valuealias = 'group'

    def __init__(self, *args, **kwargs):
        super(FullyAnonymousSubjectAdminItemValueMixin, self).__init__(*args, **kwargs)
        if self.get_assignment().anonymizationmode != Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS:
            raise ValueError('Can only use {} for fully anonymous assignments.'.format(self.__class__.__name__))

    def get_assignment(self):
        return self.kwargs['assignment']

    def get_all_candidate_users(self):
        return [candidate.relatedstudent.user
                for candidate in self.group.candidates.all()]

    def get_extra_css_classes_list(self):
        return ['devilry-cradmin-groupitemvalue']


class ItemValueMixin(object):
    valuealias = 'group'

    def __init__(self, *args, **kwargs):
        """
        Args:
            *args: Args for the superclass.
            **kwargs: Kwargs for the superclass. Must contain the Assignment object
                in the ``"assignment"`` key.
        """
        super(ItemValueMixin, self).__init__(*args, **kwargs)

    def get_devilryrole(self):
        raise NotImplementedError()

    def should_include_examiners(self):
        return True

    def get_assignment(self):
        return self.kwargs['assignment']

    def get_examiners(self):
        if not hasattr(self, '_examiners'):
            self._examiners = list(self.group.examiners.all())
        return self._examiners

    def get_extra_css_classes_list(self):
        return ['devilry-cradmin-groupitemvalue']


class MinimalItemValueMixin(ItemValueMixin):
    def get_examiners(self):
        return []

    def should_include_examiners(self):
        return False


class StudentItemValueMixin(ItemValueMixin):
    def get_devilryrole(self):
        return 'student'

    def get_assignment(self):
        return self.kwargs['assignment_id_to_assignment_map'][self.group.parentnode_id]

    def should_include_examiners(self):
        return False

    def should_include_periodpath(self):
        return self.kwargs.get('include_periodpath', True)


class ExaminerItemValueMixin(ItemValueMixin):
    def get_devilryrole(self):
        return 'examiner'

    def should_include_examiners(self):
        return self.kwargs.get('include_examiners', False)


class PeriodAdminItemValueMixin(ItemValueMixin):
    def __init__(self, *args, **kwargs):
        super(PeriodAdminItemValueMixin, self).__init__(*args, **kwargs)
        if self.get_assignment().is_anonymous:
            raise ValueError('Can not use PeriodAdminItemValueMixin for anonymous assignments. '
                             'Periodadmins are not supposed have access to them.')

    def get_devilryrole(self):
        return 'periodadmin'


class SubjectAdminItemValueMixin(ItemValueMixin):
    def __init__(self, *args, **kwargs):
        super(SubjectAdminItemValueMixin, self).__init__(*args, **kwargs)
        if self.get_assignment().anonymizationmode == Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS:
            raise ValueError('Can not use SubjectAdminItemValueMixin for fully anonymous assignments. '
                             'Use FullyAnonymousSubjectAdminItemValue istead.')

    def get_devilryrole(self):
        return 'subjectadmin'


class DepartmentAdminItemValueMixin(ItemValueMixin):
    def get_devilryrole(self):
        return 'departmentadmin'


class MinimalPeriodAdminItemValueMixin(MinimalItemValueMixin):
    def __init__(self, *args, **kwargs):
        super(MinimalPeriodAdminItemValueMixin, self).__init__(*args, **kwargs)
        if self.get_assignment().is_anonymous:
            raise ValueError('Can not use PeriodAdminItemValueMixin for anonymous assignments. '
                             'Periodadmins are not supposed have access to them.')

    def get_devilryrole(self):
        return 'periodadmin'


class MinimalSubjectAdminItemValueMixin(MinimalItemValueMixin):
    def __init__(self, *args, **kwargs):
        super(MinimalSubjectAdminItemValueMixin, self).__init__(*args, **kwargs)
        if self.get_assignment().anonymizationmode == Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS:
            raise ValueError('Can not use SubjectAdminItemValueMixin for fully anonymous assignments. '
                             'Use FullyAnonymousSubjectAdminItemValue istead.')

    def get_devilryrole(self):
        return 'subjectadmin'


class MinimalDepartmentAdminItemValueMixin(MinimalItemValueMixin):
    def get_devilryrole(self):
        return 'departmentadmin'


#
#
# ItemValue classes for normal rendering (no multiselect)
#
#

class FullyAnonymousSubjectAdminItemValue(FullyAnonymousSubjectAdminItemValueMixin,
                                          listbuilder.itemvalue.TitleDescription):
    """
    This item value renderer is for fully anonymous assignments
    with the "subjectadmin" devilryrole. It does not include anything
    that can link the student to an anonymized student in the examiner
    UI (in case the admin is also examiner). It basically only
    renders the name of the students in each group.

    We have purposly not let this inherit from :class:`.AbstractItemValue`
    because we do not want to risk that a change in that class affects
    anonymization.

    See :devilryissue:`846` for more information.
    """
    template_name = 'devilry_cradmin/devilry_listbuilder/assignmentgroup/' \
                    'fully-anonymous-subjectadmin-group-item-value.django.html'


class NoMultiselectItemValue(listbuilder.itemvalue.TitleDescription):
    """
    Not used directly - use one of the subclasses.
    """
    template_name = 'devilry_cradmin/devilry_listbuilder/assignmentgroup/item-value.django.html'


class MinimalNoMultiselectItemValue(listbuilder.itemvalue.TitleDescription):
    """
    Not used directly - use one of the subclasses.
    """
    template_name = 'devilry_cradmin/devilry_listbuilder/assignmentgroup/minimal-item-value.django.html'


class StudentItemValue(StudentItemValueMixin, NoMultiselectItemValue):
    template_name = 'devilry_cradmin/devilry_listbuilder/assignmentgroup/student-item-value.django.html'


class ExaminerItemValue(ExaminerItemValueMixin, NoMultiselectItemValue):
    template_name = 'devilry_cradmin/devilry_listbuilder/assignmentgroup/examiner-item-value.django.html'


class PeriodAdminItemValue(PeriodAdminItemValueMixin, NoMultiselectItemValue):
    pass


class SubjectAdminItemValue(SubjectAdminItemValueMixin, NoMultiselectItemValue):
    pass


class DepartmentAdminItemValue(DepartmentAdminItemValueMixin, NoMultiselectItemValue):
    pass


class MinimalPeriodAdminItemValue(MinimalPeriodAdminItemValueMixin, MinimalNoMultiselectItemValue):
    pass


class MinimalSubjectAdminItemValue(MinimalSubjectAdminItemValueMixin, MinimalNoMultiselectItemValue):
    pass


class MinimalDepartmentAdminItemValue(MinimalDepartmentAdminItemValueMixin, MinimalNoMultiselectItemValue):
    pass


#
#
# ItemValue classes for multiselect
#
#


class BaseSelectedItem(multiselect2.selected_item_renderer.SelectedItem):
    valuealias = 'group'

    def __init__(self, value, assignment):
        self.assignment = assignment
        super(BaseSelectedItem, self).__init__(value=value)

    def get_assignment(self):
        return self.assignment

    def get_title(self):
        return self.group.get_unanonymized_long_displayname()


class MinimalUnanonymizedSelectedItem(BaseSelectedItem):
    valuealias = 'group'
    template_name = 'devilry_cradmin/devilry_listbuilder/assignmentgroup/' \
                    'minimal-unanonymized-selected-item.django.html'

    def get_all_candidate_users(self):
        return [candidate.relatedstudent.user
                for candidate in self.group.candidates.all()]


class SelectedItemFull(BaseSelectedItem):
    template_name = 'devilry_cradmin/devilry_listbuilder/assignmentgroup/selected-item-full.django.html'

    def get_devilryrole(self):
        raise NotImplementedError()


class SelectedItemFullExaminer(SelectedItemFull):
    def get_title(self):
        if self.get_assignment().students_must_be_anonymized_for_devilryrole(
                devilryrole='examiner'):
            return self.group.get_anonymous_displayname()
        else:
            return super(SelectedItemFullExaminer, self).get_title()

    def get_devilryrole(self):
        return 'examiner'


class SelectedItemFullPeriodAdmin(SelectedItemFull):
    def get_devilryrole(self):
        return 'periodadmin'


class SelectedItemFullSubjectAdmin(SelectedItemFull):
    def get_devilryrole(self):
        return 'subjectadmin'


class SelectedItemFullDepartmentAdmin(SelectedItemFull):
    def get_devilryrole(self):
        return 'departmentadmin'


class FullyAnonymousSubjectAdminMultiselectItemValue(FullyAnonymousSubjectAdminItemValueMixin,
                                                     multiselect2.listbuilder_itemvalues.ItemValue):
    """
    This item value renderer is for fully anonymous assignments
    with the "subjectadmin" devilryrole. It does not include anything
    that can link the student to an anonymized student in the examiner
    UI (in case the admin is also examiner). It basically only
    renders the name of the students in each group.

    We have purposly not let this inherit from :class:`.AbstractItemValue`
    because we do not want to risk that a change in that class affects
    anonymization.

    See :devilryissue:`846` for more information.
    """
    template_name = 'devilry_cradmin/devilry_listbuilder/assignmentgroup/' \
                    'multiselect-fully-anonymous-subjectadmin-group-item-value.django.html'
    selected_item_renderer_class = MinimalUnanonymizedSelectedItem

    def get_title(self):
        return self.group.get_unanonymized_long_displayname()

    def make_selected_item_renderer(self):
        return MinimalUnanonymizedSelectedItem(
            value=self.value, assignment=self.get_assignment())


class MultiselectItemValue(multiselect2.listbuilder_itemvalues.ItemValue):
    """
    Not used directly - use one of the subclasses.
    """
    template_name = 'devilry_cradmin/devilry_listbuilder/assignmentgroup/multiselect-item-value.django.html'
    selected_item_renderer_class = SelectedItemFull

    def get_title(self):
        return self.group.get_unanonymized_long_displayname()

    def make_selected_item_renderer(self):
        return self.selected_item_renderer_class(
            value=self.value, assignment=self.get_assignment())


class ExaminerMultiselectItemValue(ExaminerItemValueMixin, MultiselectItemValue):
    template_name = 'devilry_cradmin/devilry_listbuilder/assignmentgroup/multiselect-examiner-item-value.django.html'
    selected_item_renderer_class = SelectedItemFullExaminer

    def get_title(self):
        if self.get_assignment().students_must_be_anonymized_for_devilryrole(devilryrole='examiner'):
            return self.group.get_anonymous_displayname()
        else:
            return self.group.get_unanonymized_long_displayname()


class PeriodAdminMultiselectItemValue(PeriodAdminItemValueMixin, MultiselectItemValue):
    selected_item_renderer_class = SelectedItemFullPeriodAdmin


class SubjectAdminMultiselectItemValue(SubjectAdminItemValueMixin, MultiselectItemValue):
    selected_item_renderer_class = SelectedItemFullSubjectAdmin


class DepartmentAdminMultiselectItemValue(DepartmentAdminItemValueMixin, MultiselectItemValue):
    selected_item_renderer_class = SelectedItemFullDepartmentAdmin


class GroupTargetRenderer(multiselect2.target_renderer.Target):
    def get_with_items_title(self):
        return ugettext_lazy('Selected students:')

    def get_submit_button_text(self):
        return ugettext_lazy('Save')

    def get_without_items_text(self):
        return ugettext_lazy('No students selected')
