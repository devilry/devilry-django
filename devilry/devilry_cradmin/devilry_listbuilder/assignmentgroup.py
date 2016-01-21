from django_cradmin.viewhelpers import listbuilder

from devilry.apps.core.models import Assignment


class FullyAnonymousSubjectAdminItemValue(listbuilder.itemvalue.TitleDescription):
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
    valuealias = 'group'
    template_name = 'devilry_cradmin/devilry_listbuilder/assignmentgroup/' \
                    'fully-anonymous-subjectadmin-group-item-value.django.html'

    def __init__(self, *args, **kwargs):
        super(FullyAnonymousSubjectAdminItemValue, self).__init__(*args, **kwargs)
        if self.get_assignment().anonymizationmode != Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS:
            raise ValueError('Can only use FullyAnonymousSubjectAdminItemValue for fully anonymous assignments. '
                             'Use SubjectAdminItemValue istead.')

    def get_assignment(self):
        return self.kwargs['assignment']

    def get_all_candidate_users(self):
        return [candidate.relatedstudent.user
                for candidate in self.group.candidates.all()]


class AbstractItemValue(listbuilder.itemvalue.TitleDescription):
    valuealias = 'group'
    template_name = 'devilry_cradmin/devilry_listbuilder/assignmentgroup/item-value.django.html'

    def __init__(self, *args, **kwargs):
        """
        Args:
            *args: Args for the superclass.
            **kwargs: Kwargs for the superclass. Must contain the Assignment object
                in the ``"assignment"`` key.
        """
        super(AbstractItemValue, self).__init__(*args, **kwargs)
        self._examiners = list(self.group.examiners.all())

    def get_devilryrole(self):
        raise NotImplementedError()

    def should_include_examiners(self):
        return True

    def get_assignment(self):
        return self.kwargs['assignment']

    def get_examiners(self):
        return self._examiners


class StudentItemValue(AbstractItemValue):
    def get_devilryrole(self):
        return 'student'


class ExaminerItemValue(AbstractItemValue):
    template_name = 'devilry_cradmin/devilry_listbuilder/assignmentgroup/examiner-item-value.django.html'

    def get_devilryrole(self):
        return 'examiner'

    def should_include_examiners(self):
        return self.kwargs.get('include_examiners', False)


class AbstractAdminItemValue(AbstractItemValue):
    """
    Base class for the admin roles AbstractItemValue classes.
    """


class PeriodAdminItemValue(AbstractAdminItemValue):
    def __init__(self, *args, **kwargs):
        super(PeriodAdminItemValue, self).__init__(*args, **kwargs)
        if self.get_assignment().is_anonymous:
            raise ValueError('Can not use PeriodAdminItemValue for anonymous assignments. '
                             'Periodadmins are not supposed have access to them.')

    def get_devilryrole(self):
        return 'periodadmin'


class SubjectAdminItemValue(AbstractAdminItemValue):
    def __init__(self, *args, **kwargs):
        super(SubjectAdminItemValue, self).__init__(*args, **kwargs)
        if self.get_assignment().anonymizationmode == Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS:
            raise ValueError('Can not use SubjectAdminItemValue for fully anonymous assignments. '
                             'Use FullyAnonymousSubjectAdminItemValue istead.')

    def get_devilryrole(self):
        return 'subjectadmin'


class DepartmentAdminItemValue(AbstractAdminItemValue):
    def get_devilryrole(self):
        return 'departmentadmin'
