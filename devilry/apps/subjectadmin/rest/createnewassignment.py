from devilry.apps.core.models import Assignment

def _find_relatedexaminers_matching_tags(tags, relatedexaminers):
    examiners = []
    for relatedexaminer in relatedexaminers:
        for tag in tags:
            if tag in relatedexaminer.tags:
                examiners.append(relatedexaminer.user)
    return examiners


class CreateNewAssignmentDao(object):
    def _create_assignment(self, parentnode, short_name, long_name,
                           publishing_time, delivery_types, anonymous):
        assignment = Assignment(parentnode=parentnode, short_name=short_name,
                                long_name=long_name,
                                publishing_time=publishing_time,
                                delivery_types=delivery_types,
                                anonymous=anonymous)
        assignment.full_clean()
        assignment.save()
        return assignment

    def _create_group_from_relatedstudent(self, assignment, relatedstudent,
                                          relatedexaminers):
        """
        Create an AssignmentGroup within the given ``assignment`` with tags and
        examiners from the given ``relatedstudent`` and ``relatedexaminers``.

        The examiners are set if an examiner share a tag with a student.

        Note that ``relatedexaminers`` is a parameter (as opposed to using
        assignment.parentnode...) because they should be queried for one time,
        not for each call to this method.
        """
        group = assignment.assignmentgroups.create()
        kw = dict(student=relatedstudent.user)
        if relatedstudent.candidate_id:
            kw['candidate_id'] = relatedstudent.candidate_id
        group.candidates.create(**kw)
        if relatedstudent.tags:
            tags = relatedstudent.tags.split(',')
            for tag in tags:
                group.tags.create(tag=tag)
            examiners = _find_relatedexaminers_matching_tags(tags, relatedexaminers)
            for examiner in examiners:
                group.examiners.create(user=examiner)
        return group

    def _create_deadline(self, group, deadline):
        return group.deadlines.create(deadline=deadline)

    def _add_all_relatedstudents(self, assignment, first_deadline):
        relatedexaminers = assignment.parentnode.relatedexaminer_set.all()
        for relatedstudent in assignment.parentnode.relatedstudent_set.all():
            group = self._create_group_from_relatedstudent(assignment,
                                                           relatedstudent,
                                                           relatedexaminers)
            self._create_deadline(group, first_deadline)

    def create_noauth(self, parentnode, short_name, long_name, publishing_time,
                      delivery_types, anonymous, add_all_relatedstudents,
                      first_deadline, autosetup_examiners):
        assignment = self._create_assignment(parentnode, short_name, long_name,
                                             publishing_time, delivery_types,
                                             anonymous)
        if add_all_relatedstudents:
            self._add_all_relatedstudents(assignment, first_deadline)
