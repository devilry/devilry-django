from django_cradmin.viewhelpers import listbuilder

from devilry.apps.core.models import Assignment


class FullyAnonymousSubjectAdminItemValue(listbuilder.itemvalue.TitleDescription):
    """
    This item value renderer is for fully anonymous assignments
    with the "subjectadmin" devilryrole. It does not include anything
    that can link the student to an anonymized student in the examiner
    UI (in case the admin is also examiner). It basically only
    renders the name of the students in each group.

    See :devilryissue:`846` for more information.
    """
    valuealias = 'group'
    template_name = 'devilry_cradmin/devilry_listbuilder/assignmentgroup/' \
                    'fully-anonymous-subjectadmin-group-item-value.django.html'

    def __init__(self, *args, **kwargs):
        super(FullyAnonymousSubjectAdminItemValue, self).__init__(*args, **kwargs)
        if self.group.assignment.anonymizationmode != Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS:
            raise ValueError('Can only use FullyAnonymousSubjectAdminItemValue for fully anonymous assignments. '
                             'Use SubjectAdminItemValue istead.')

    def get_all_candidate_users(self):
        return [candidate.relatedstudent.user
                for candidate in self.group.candidates.all()]


class AbstractItemValue(listbuilder.itemvalue.TitleDescription):
    valuealias = 'group'
    template_name = 'devilry_cradmin/devilry_listbuilder/assignmentgroup/group-item-value.django.html'

    def __init__(self, *args, **kwargs):
        super(AbstractItemValue, self).__init__(*args, **kwargs)
        self._examiners = list(self.group.examiners.all())

    def get_devilryrole(self):
        raise NotImplementedError()

    def should_include_examiners(self):
        return True

    def get_examiners(self):
        return self._examiners

    # def get_extra_css_classes_list(self):
    #     css_classes = ['devilry-examiner-listbuilder-assignmentlist-assignmentitemvalue']
    #     if self.group.waiting_for_feedback_count > 0:
    #         css_classes.append('devilry-django-cradmin-listbuilder-itemvalue-titledescription-description-warning')
    #     else:
    #         css_classes.append('devilry-django-cradmin-listbuilder-itemvalue-titledescription-description-muted')
    #     return css_classes


class StudentItemValue(AbstractItemValue):
    def get_devilryrole(self):
        return 'student'


class ExaminerItemValue(AbstractItemValue):
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
        if self.group.assignment.is_anonymous:
            raise ValueError('Can not use PeriodAdminItemValue for anonymous assignments. '
                             'Periodadmins are not supposed have access to them.')

    def get_devilryrole(self):
        return 'periodadmin'


class SubjectAdminItemValue(AbstractAdminItemValue):
    def __init__(self, *args, **kwargs):
        super(SubjectAdminItemValue, self).__init__(*args, **kwargs)
        if self.group.assignment.anonymizationmode == Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS:
            raise ValueError('Can not use SubjectAdminItemValue for fully anonymous assignments. '
                             'Use FullyAnonymousSubjectAdminItemValue istead.')

    def get_devilryrole(self):
        return 'subjectadmin'


class DepartmentAdminItemValue(AbstractAdminItemValue):
    def get_devilryrole(self):
        return 'departmentadmin'
