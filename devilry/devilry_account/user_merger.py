from devilry.devilry_group.models import FeedbackSet
from devilry.devilry_comment.models import Comment
from devilry.devilry_qualifiesforexam.models import QualifiesForFinalExam
from devilry.apps.core.models import Candidate, Examiner, RelatedStudent, RelatedExaminer
from django.db import transaction

from devilry.devilry_account.models import MergedUser, PermissionGroupUser


class UserMerger:
    """
    Handles merging a ``source_user`` into a ``target_user``.

    The strategy is:

    """
    def __init__(self, source_user, target_user, pretend=True):
        self.pretend = pretend
        self.merged_user = MergedUser(
            source_user=source_user,
            target_user=target_user,
            summary_json={}
        )

    @property
    def source_user(self):
        return self.merged_user.source_user

    @property
    def target_user(self):
        return self.merged_user.target_user

    @property
    def summary(self):
        return self.merged_user.summary_json

    def _merge_user_objects(self):
        pass

    def _merge_permission_group_user_objects(self):
        permissiongroupusers = PermissionGroupUser.objects.filter(user=self.source_user)
        self.summary['PermissionGroupUser'] = {
            'note': 'Administrator permission groups. Update user foreign key so source user is replaced with target user.',
            'permission_group_user_count': permissiongroupusers.count(),
            'details': {
                'permission_group_users_updated': [
                    {
                        'permissiongroupuser_id': permissiongroupuser.id,
                        'group_name': permissiongroupuser.permissiongroup.name
                    }
                    for permissiongroupuser in permissiongroupusers.order_by('permissiongroup__name').select_related('permissiongroup')
                ]
            }
        }
        if not self.pretend:
            permissiongroupusers.update(user=self.target_user)

    def _merge_relatedstudent_objects(self):
        summary = {
            'note': (
                'Students on a period. Merge source RelatedStudent and all sub-objects '
                '(Candidates and QualifiesForFinalExams) into target RelatedStudent.'
            ),
            'relatedstudents_with_user_fk_changed_count': 0,
            'merged_relatedstudents_and_subobjects_count': 0,
            'details': {
                'merged_candidates': [],
                'merged_qualifiesforfinalexams': [],
                'relatedstudents_with_user_fk_changed': []
            }
        }
        for source_relatedstudent in RelatedStudent.objects.filter(user=self.source_user).select_related('period'):
            target_relatedstudent = RelatedStudent.objects\
                .filter(user=self.target_user, period=source_relatedstudent.period).first()
            if target_relatedstudent:

                # Candidates
                candidates = Candidate.objects.filter(relatedstudent=source_relatedstudent)\
                    .select_related('assignment_group__parentnode')
                if not self.pretend:
                    candidates.update(
                        relatedstudent=target_relatedstudent
                    )
                for candidate in candidates:
                    summary['details']['merged_candidates'].append({
                        'candidate_id': candidate.id,
                        'assignment': candidate.assignment_group.assignment.get_path()
                    })

                # QualifiesForFinalExam
                qualifiesforfinalexams = QualifiesForFinalExam.objects.filter(relatedstudent=source_relatedstudent)\
                    .select_related('relatedstudent__period')
                if not self.pretend:
                    qualifiesforfinalexams.update(
                        relatedstudent=target_relatedstudent
                    )
                for qualifiesforfinalexam in qualifiesforfinalexams:
                    summary['details']['merged_qualifiesforfinalexams'].append({
                        'qualifiesforfinalexam_id': qualifiesforfinalexam.id,
                        'period': qualifiesforfinalexam.relatedstudent.period.get_path()
                    })


                # All subobjects has been moved - delete the relatedstudent
                if not self.pretend:
                    source_relatedstudent.delete()
                summary['merged_relatedstudents_and_subobjects_count'] += 1
            else:
                if not self.pretend:
                    source_relatedstudent.user = self.target_user
                    source_relatedstudent.save()
                summary['relatedstudents_with_user_fk_changed_count'] += 1
                summary['details']['relatedstudents_with_user_fk_changed'].append({
                    'relatedstudent_id': source_relatedstudent.id,
                    'period': source_relatedstudent.period.get_path()
                })
        self.summary['RelatedStudent'] = summary

    def _merge_relatedexaminer_objects(self):
        summary = {
            'note': (
                'Students on a period. Merge source RelatedExaminer and all sub-objects '
                '(Examiners) into target RelatedExaminer.'
            ),
            'relatedexaminers_with_user_fk_changed_count': 0,
            'merged_relatedexaminers_and_subobjects_count': 0,
            'details': {
                'merged_examiners': [],
                'merged_qualifiesforfinalexams': [],
                'relatedexaminers_with_user_fk_changed': []
            }
        }
        for source_relatedexaminer in RelatedExaminer.objects.filter(user=self.source_user).select_related('period'):
            target_releatedexaminer = RelatedExaminer.objects\
                .filter(user=self.target_user, period=source_relatedexaminer.period).first()
            if target_releatedexaminer:

                # Candidates
                examiners = Examiner.objects.filter(relatedexaminer=source_relatedexaminer)\
                    .select_related('assignmentgroup__parentnode')
                if not self.pretend:
                    examiners.update(
                        relatedexaminer=target_releatedexaminer
                    )
                for examiner in examiners:
                    summary['details']['merged_examiners'].append({
                        'examiner_id': examiner.id,
                        'assignment': examiner.assignmentgroup.assignment.get_path()
                    })

                # All subobjects has been moved - delete the relatedexaminer
                if not self.pretend:
                    source_relatedexaminer.delete()
                summary['merged_relatedexaminers_and_subobjects_count'] += 1
            else:
                if not self.pretend:
                    source_relatedexaminer.user = self.target_user
                    source_relatedexaminer.save()
                summary['relatedexaminers_with_user_fk_changed_count'] += 1
                summary['details']['relatedexaminers_with_user_fk_changed'].append({
                    'relatedexaminer_id': source_relatedexaminer.id,
                    'period': source_relatedexaminer.period.get_path()
                })
        self.summary['RelatedExaminer'] = summary

    def _merge_comment_objects(self):
        comments = Comment.objects.filter(user=self.source_user)
        self.summary['Comment'] = {
            'note': (
                'Comments made by the source user - foreign key moved to the target user.'
            ),
            'moved_comments_count': comments.count(),
        }
        if not self.pretend:
            comments.update(user=self.target_user)

    def _merge_feedbackset_objects(self):
        feedbacksets_published_by = FeedbackSet.objects.filter(grading_published_by=self.source_user)
        feedbacksets_created_by = FeedbackSet.objects.filter(created_by=self.source_user)
        feedbacksets_last_updated_by = FeedbackSet.objects.filter(last_updated_by=self.source_user)
        self.summary['FeedbackSet'] = {
            'note': (
                'Feedback sets created, updated or published by the source user. Foreign keys moved to the target user.'
            ),
            'published_by_count': feedbacksets_published_by.count(),
            'created_by_count': feedbacksets_created_by.count(),
            'last_updated_by_count': feedbacksets_last_updated_by.count(),
        }
        if not self.pretend:
            feedbacksets_published_by.update(grading_published_by=self.target_user)
            feedbacksets_created_by.update(created_by=self.target_user)
            feedbacksets_last_updated_by.update(last_updated_by=self.target_user)

    def _merge(self):
        self._merge_permission_group_user_objects()
        self._merge_relatedstudent_objects()
        self._merge_relatedexaminer_objects()
        self._merge_comment_objects()
        self._merge_feedbackset_objects()
        if not self.pretend:
            self.merged_user.save()

    def merge(self):
        if self.pretend:
            self._merge()
        else:
            with transaction.atomic():
                self._merge()
