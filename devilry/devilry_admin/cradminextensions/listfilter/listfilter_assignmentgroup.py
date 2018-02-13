from devilry.devilry_admin.cradminextensions.listfilter.listfilter_tags import AbstractTagSelectFilter


class AssignmentGroupRelatedStudentTagSelectFilter(AbstractTagSelectFilter):
    """
    Tag select filter for ``RelatedStudent``s in ``AssignmentGroup``s.
    """
    def filter(self, queryobject):
        cleaned_value = self.get_cleaned_value() or ''
        if cleaned_value != '':
            queryobject = queryobject.filter(candidates__relatedstudent__periodtag__id=cleaned_value)
        return queryobject


class AssignmentGroupRelatedExaminerTagSelectFilter(AbstractTagSelectFilter):
    """
    Tag select filter for ``RelatedExaminers``s in ``AssignmentGroup``s.
    """
    def filter(self, queryobject):
        cleaned_value = self.get_cleaned_value() or ''
        if cleaned_value != '':
            queryobject = queryobject.filter(examiners__relatedexaminer__periodtag__id=cleaned_value)
        return queryobject
