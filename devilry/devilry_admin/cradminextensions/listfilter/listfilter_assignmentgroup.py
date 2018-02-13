from django.utils.translation import pgettext_lazy

from devilry.devilry_admin.cradminextensions.listfilter.listfilter_tags import AbstractTagSelectFilter


class AssignmentGroupRelatedStudentTagSelectFilter(AbstractTagSelectFilter):
    """
    Tag select filter for ``RelatedStudent``s in ``AssignmentGroup``s.
    """
    def get_slug(self):
        return 'stag'

    def get_label(self):
        return pgettext_lazy('tag', 'Student(s) has tag')

    def filter(self, queryobject):
        cleaned_value = self.get_cleaned_value() or ''
        if cleaned_value != '':
            queryobject = queryobject.filter_periodtag_for_students(periodtag_id=cleaned_value)
        return queryobject


class AssignmentGroupRelatedExaminerTagSelectFilter(AbstractTagSelectFilter):
    """
    Tag select filter for ``RelatedExaminers``s in ``AssignmentGroup``s.
    """
    def get_slug(self):
        return 'etag'

    def get_label(self):
        return pgettext_lazy('tag', 'Examiner(s) has tag')

    def filter(self, queryobject):
        cleaned_value = self.get_cleaned_value() or ''
        if cleaned_value != '':
            queryobject = queryobject.filter_periodtag_for_examiners(periodtag_id=cleaned_value)
        return queryobject
