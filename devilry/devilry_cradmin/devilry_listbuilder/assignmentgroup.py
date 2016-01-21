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
        self._examiners = list(self.group.examiners.all())

    def get_devilryrole(self):
        raise NotImplementedError()

    def should_include_examiners(self):
        return True

    def get_assignment(self):
        return self.kwargs['assignment']

    def get_examiners(self):
        return self._examiners


class StudentItemValueMixin(ItemValueMixin):
    def get_devilryrole(self):
        return 'student'


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


class StudentItemValue(StudentItemValueMixin, NoMultiselectItemValue):
    pass


class ExaminerItemValue(ExaminerItemValueMixin, NoMultiselectItemValue):
    template_name = 'devilry_cradmin/devilry_listbuilder/assignmentgroup/examiner-item-value.django.html'


class PeriodAdminItemValue(PeriodAdminItemValueMixin, NoMultiselectItemValue):
    pass


class SubjectAdminItemValue(SubjectAdminItemValueMixin, NoMultiselectItemValue):
    pass


class DepartmentAdminItemValue(DepartmentAdminItemValueMixin, NoMultiselectItemValue):
    pass


#
#
# ItemValue classes for multiselect
#
#
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


class MultiselectItemValue(multiselect2.listbuilder_itemvalues.ItemValue):
    """
    Not used directly - use one of the subclasses.
    """
    template_name = 'devilry_cradmin/devilry_listbuilder/assignmentgroup/multiselect-item-value.django.html'


class ExaminerMultiselectItemValue(ExaminerItemValueMixin, MultiselectItemValue):
    template_name = 'devilry_cradmin/devilry_listbuilder/assignmentgroup/multiselect-examiner-item-value.django.html'


class PeriodAdminMultiselectItemValue(PeriodAdminItemValueMixin, MultiselectItemValue):
    pass


class SubjectAdminMultiselectItemValue(SubjectAdminItemValueMixin, MultiselectItemValue):
    pass


class DepartmentAdminMultiselectItemValue(DepartmentAdminItemValueMixin, MultiselectItemValue):
    pass
