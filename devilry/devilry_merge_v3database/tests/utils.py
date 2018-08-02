from django import test
from django.conf import settings
from django.contrib.auth import get_user_model

from model_mommy import mommy

from devilry.apps.core import models as core_models
from devilry.devilry_group import models as group_models
from devilry.apps.core import mommy_recipes


class MergerTestHelper(test.TestCase):
    def get_or_create_subject(self, subject_kwargs=None, db_alias='default'):
        """
        Get Subject if it exists with short_name, else create.
        """
        if not subject_kwargs:
            subject_kwargs = {'short_name': 'default_subject'}
        if core_models.Subject.objects.using(db_alias).filter(short_name=subject_kwargs['short_name']).exists():
            subject = core_models.Subject.objects.using(db_alias).get(short_name=subject_kwargs['short_name'])
        else:
            subject = mommy.prepare('core.Subject', **subject_kwargs)
            subject.save(using=db_alias)
        return subject

    def get_or_create_period(self, subject, period_kwargs=None, db_alias='default'):
        """
        Get Period if it exists with short_name, else create.
        """
        if not period_kwargs:
            period_kwargs = {'short_name': 'default_period'}
        if core_models.Period.objects.using(db_alias).filter(short_name=period_kwargs['short_name']).exists():
            period = core_models.Period.objects.using(db_alias).get(short_name=period_kwargs['short_name'])
        else:
            period = mommy.prepare('core.Period',
                                   parentnode=subject,
                                   start_time=mommy_recipes.ACTIVE_PERIOD_START,
                                   end_time=mommy_recipes.ACTIVE_PERIOD_END,
                                   **period_kwargs)
            period.save(using=db_alias)
        return period

    def get_or_create_assignment(self, period, assignment_kwargs=None, db_alias='default'):
        """
        Get Assignment if it exists with short_name, else create.
        """
        if not assignment_kwargs:
            assignment_kwargs = {'short_name': 'default_assignment'}
        if core_models.Assignment.objects.using(db_alias).filter(short_name=assignment_kwargs['short_name']).exists():
            assignment = core_models.Assignment.objects.using(db_alias).get(short_name=assignment_kwargs['short_name'])
        else:
            assignment = mommy.prepare('core.Assignment',
                                       parentnode=period,
                                       first_deadline=mommy_recipes.ASSIGNMENT_ACTIVEPERIOD_MIDDLE_FIRST_DEADLINE,
                                       publishing_time=mommy_recipes.ASSIGNMENT_ACTIVEPERIOD_START_FIRST_DEADLINE,
                                       **assignment_kwargs)
            assignment.save(using=db_alias)
        return assignment

    def get_or_create_assignment_group(self, assignment, assignment_group_kwargs, db_alias='default'):
        """
        Get AssignmentGroup if it exists with name, else create.
        """
        if not assignment_group_kwargs:
            assignment_group_kwargs = {'name': 'default_group'}
        if core_models.AssignmentGroup.objects.using(db_alias).filter(name=assignment_group_kwargs['name']).exists():
            assignment_group = core_models.AssignmentGroup.objects.using(db_alias)\
                .get(name=assignment_group_kwargs['name'])
        else:
            assignment_group = mommy.prepare('core.AssignmentGroup', parentnode=assignment, **assignment_group_kwargs)
            assignment_group.save(using=db_alias)
        return assignment_group

    def get_or_create_feedback_set(self, assignment_group, feedback_set_kwargs, db_alias='default'):
        """
        Get FeedbackSet if it exists with assignment_group, else create.
        """
        if not feedback_set_kwargs:
            feedback_set_kwargs = {}
        if group_models.FeedbackSet.objects.using(db_alias).select_related('group')\
                .filter(group_id=assignment_group.id).exists():
            feedback_set = group_models.FeedbackSet.objects.using(db_alias).select_related('group')\
                .get(group_id=assignment_group.id)
        else:
            feedback_set = mommy.prepare('devilry_group.FeedbackSet', group=assignment_group, **feedback_set_kwargs)
            feedback_set.save(using=db_alias)
        return feedback_set

    def get_or_create_user(self, user_kwargs, db_alias='default'):
        """
        Get User if it exists with shortname, else create.
        """
        if not user_kwargs:
            user_kwargs = {'shortname': 'default_user'}
        if get_user_model().objects.using(db_alias).filter(shortname=user_kwargs['shortname']).exists():
            user = get_user_model().objects.using(db_alias).get(shortname=user_kwargs['shortname'])
        else:
            user = mommy.prepare(settings.AUTH_USER_MODEL, **user_kwargs)
            user.save(using=db_alias)
        return user

    def get_or_create_related_student(self, user, period, db_alias='default'):
        """
        Get RelatedStudent if it exists with user and period, else create.
        """
        if core_models.RelatedStudent.objects.using(db_alias).select_related('user', 'period')\
                .filter(user=user, period=period):
            related_student = core_models.RelatedStudent.objects.using(db_alias)\
                .select_related('user', 'period')\
                .get(user=user, period=period)
        else:
            related_student = mommy.prepare('core.RelatedStudent', user=user, period=period)
            related_student.save(using=db_alias)
        return related_student

    def get_or_create_candidate(self, assignment_group, related_student, candidate_kwargs=None, db_alias='default'):
        """
        Get Candidate if it exists with assignment_group and related_student, else create.
        """
        if not candidate_kwargs:
            candidate_kwargs = {}
        if core_models.Candidate.objects.using(db_alias)\
                .select_related('assignment_group', 'relatedstudent')\
                .filter(assignment_group_id=assignment_group.id, relatedstudent_id=related_student.id):
            candidate = core_models.Candidate.objects.using(db_alias)\
                .select_related('assignment_group', 'relatedstudent')\
                .get(assignment_group_id=assignment_group.id, relatedstudent_id=related_student.id)
        else:
            candidate = mommy.prepare('core.Candidate',
                                      relatedstudent=related_student,
                                      assignment_group=assignment_group, **candidate_kwargs)
            candidate.save(using=db_alias)
        return candidate

    def get_or_create_related_examiner(self, user, period, db_alias='default'):
        """
        Get RelatedExaminer if it exists with user and period, else create.
        """
        if core_models.RelatedExaminer.objects.using(db_alias).select_related('user', 'period')\
                .filter(user=user, period=period):
            related_examiner = core_models.RelatedExaminer.objects.using(db_alias)\
                .select_related('user', 'period')\
                .get(user=user, period=period)
        else:
            related_examiner = mommy.prepare('core.RelatedExaminer', user=user, period=period)
            related_examiner.save(using=db_alias)
        return related_examiner

    def get_or_create_examiner(self, assignment_group, related_examiner, examiner_kwargs, db_alias='default'):
        """
        Get Examiner if it exists with assignment_group and related_examiner, else create.
        """
        if not examiner_kwargs:
            examiner_kwargs = {}
        if core_models.Examiner.objects.using(db_alias)\
                .select_related('assignmentgroup', 'relatedexaminer')\
                .filter(assignmentgroup_id=assignment_group.id, relatedexaminer_id=related_examiner.id):
            examiner = core_models.Examiner.objects.using(db_alias)\
                .select_related('assignmentgroup', 'relatedexaminer')\
                .get(assignmentgroup_id=assignment_group.id, relatedexaminer_id=related_examiner.id)
        else:
            examiner = mommy.prepare('core.Examiner',
                                     relatedexaminer=related_examiner,
                                     assignmentgroup=assignment_group, **examiner_kwargs)
            examiner.save(using=db_alias)
        return examiner
