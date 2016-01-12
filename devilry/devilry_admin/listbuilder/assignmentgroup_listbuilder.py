from django.utils.translation import gettext
from django_cradmin.viewhelpers import listbuilder


class Value(listbuilder.base.ItemValueRenderer):
    """
    Renders information about an AssignmentGroup.

    It does not render a link - that is left up to the ItemFrameRenderer.

    The queryset used to render these values must use::

        AssignmentGroup.objects.filter(....).prefetch_related(
            models.Prefetch('candidates',
                            queryset=coremodels.Candidate.objects.select_related(
                                'relatedstudent__user'),
                            to_attr='candidates'),
            models.Prefetch('examiners',
                            queryset=coremodels.Examiner.objects.select_related(
                                'relatedexaminer__user'),
                            to_attr='examiners'))
    """
    template_name = 'devilry_admin/listbuilder/assignmentgroup_listbuilder/value.django.html'
    valuealias = 'group'

    def __init__(self, *args, **kwargs):
        super(Value, self).__init__(*args, **kwargs)
        self.candidateinfo_list = self.__get_candidateinfo_list()
        self.examinerinfo_list = self.__get_examinerinfo_list()

    def get_name(self):
        return self.group.name

    def has_name(self):
        return bool(self.group.name.strip())

    def get_fallback_name(self):
        """
        The name used when :meth:`.has_name` is ``False``.
        """
        return gettext('AssignmentGroup #%(id)s') % {
            'id': self.group.id
        }

    def __candidate_to_dict(self, candidate):
        return {
            'fullname': candidate.relatedstudent.user.fullname,
            'shortname': candidate.relatedstudent.user.shortname,
        }

    def __get_candidateinfo_list(self):
        return [self.__candidate_to_dict(candidate)
                for candidate in self.group.candidates.all()]

    def __examiner_to_dict(self, examiner):
        return {
            'fullname': examiner.relatedexaminer.user.fullname,
            'shortname': examiner.relatedexaminer.user.shortname,
        }

    def __get_examinerinfo_list(self):
        return [self.__examiner_to_dict(examiner)
                for examiner in self.group.examiners.all()]
