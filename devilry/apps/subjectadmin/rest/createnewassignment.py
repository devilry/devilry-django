from devilry.apps.core.models import Assignment


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

    def _create_group_from_relatedstudent(self, assignment, relatedstudent):
        group = assignment.assignmentgroups.create()
        kw = dict(student=relatedstudent.user)
        if relatedstudent.candidate_id:
            kw['candidate_id'] = relatedstudent.candidate_id
        if relatedstudent.tags:
            for tag in relatedstudent.tags.split(','):
                group.tags.create(tag=tag)
        group.candidates.create(**kw)
        return group

    def _create_deadline(self, group, deadline):
        return group.deadlines.create(deadline=deadline)

    def _add_all_relatedstudents(self, assignment, first_deadline):
        for relatedstudent in assignment.parentnode.relatedstudent_set.all():
            group = self._create_group_from_relatedstudent(assignment, relatedstudent)
            self._create_deadline(group, first_deadline)

    #def set_examiners_from_related

    def create_noauth(self, parentnode, short_name, long_name, publishing_time,
                      delivery_types, anonymous, add_all_relatedstudents,
                      first_deadline, autosetup_examiners):
        assignment = self._create_assignment(parentnode, short_name, long_name,
                                             publishing_time, delivery_types,
                                             anonymous)
        if add_all_relatedstudents:
            self._add_all_relatedstudents(assignment, first_deadline)
