import shutil
import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.test import TestCase
from django.utils import timezone

from model_mommy import mommy

from devilry.apps.core.models import Subject, Period, Assignment, AssignmentGroup, PeriodTag, RelatedStudent, Candidate, \
    RelatedExaminer, Examiner
from devilry.devilry_account.models import SubjectPermissionGroup, PeriodPermissionGroup, PermissionGroupUser, \
    PermissionGroup
from devilry.devilry_comment.models import Comment, CommentFile
from devilry.devilry_group.models import FeedbackSet, GroupComment
from devilry.devilry_superadmin.delete_periods.period_delete import PeriodDelete


class TestPeriodDelete(TestCase):
    def tearDown(self):
        # Ignores errors if the path is not created.
        shutil.rmtree('devilry_testfiles/filestore/', ignore_errors=True)

    def test_end_time_not_less_than(self):
        mommy.make('core.Period', end_time=timezone.now() + timezone.timedelta(days=10))
        PeriodDelete(end_time_older_than_datetime=timezone.now()).delete()
        self.assertEqual(Period.objects.count(), 1)

    def test_only_deletes_periods_older_than_sanity(self):
        testperiod1 = mommy.make('core.Period', end_time=timezone.now() + timezone.timedelta(days=1))
        testperiod2 = mommy.make('core.Period', end_time=timezone.now() + timezone.timedelta(days=2))
        testperiod3 = mommy.make('core.Period', end_time=timezone.now() - timezone.timedelta(days=1))
        testperiod4 = mommy.make('core.Period', end_time=timezone.now() - timezone.timedelta(days=2))

        PeriodDelete(end_time_older_than_datetime=timezone.now()).delete()

        self.assertTrue(Period.objects.filter(id=testperiod1.id).exists())
        self.assertTrue(Period.objects.filter(id=testperiod2.id).exists())
        self.assertFalse(Period.objects.filter(id=testperiod3.id).exists())
        self.assertFalse(Period.objects.filter(id=testperiod4.id).exists())

    def test_does_not_delete_files_for_other_periods(self):
        testfeedbackset = mommy.make(
            'devilry_group.FeedbackSet',
            group__parentnode__parentnode__end_time=timezone.now() + timezone.timedelta(days=300))
        testcomment = mommy.make('devilry_group.GroupComment', feedback_set=testfeedbackset)
        commentfile = mommy.make('devilry_comment.CommentFile',
                                        comment=testcomment, filename='notdeleted.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        file_path = commentfile.file.path

        to_delete_testfeedbackset = mommy.make(
            'devilry_group.FeedbackSet',
            group__parentnode__parentnode__end_time=timezone.now())
        to_delete_testcomment = mommy.make('devilry_group.GroupComment', feedback_set=to_delete_testfeedbackset)
        to_delete_commentfile = mommy.make('devilry_comment.CommentFile',
                                        comment=to_delete_testcomment, filename='testfile.txt')
        to_delete_commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        to_delete_file_path = to_delete_commentfile.file.path

        self.assertTrue(os.path.exists(file_path))
        self.assertTrue(os.path.exists(to_delete_file_path))

        PeriodDelete(end_time_older_than_datetime=timezone.now() + timezone.timedelta(days=10)).delete()

        self.assertTrue(os.path.exists(file_path))
        self.assertFalse(os.path.exists(to_delete_file_path))

    def excludes_initially_empty_subjects(self):
        subject_without_period = mommy.make('core.Subject')
        mommy.make('core.Period', end_time=timezone.now())
        self.assertEqual(Subject.objects.count(), 2)
        self.assertEqual(Period.objects.count(), 1)
        PeriodDelete(end_time_older_than_datetime=timezone.now() + timezone.timedelta(days=10)).delete()
        self.assertEqual(Subject.objects.get(), subject_without_period)
        self.assertEqual(Period.objects.count(), 0)

    def does_subject_not_deleted_if_not_all_periods_are_deleted(self):
        testsubject = mommy.make('core.Subject')
        mommy.make('core.Period', parentnode=testsubject, end_time=timezone.now())
        period_not_deleted = mommy.make('core.Period', parentnode=testsubject,
                                        end_time=timezone.now() + timezone.timedelta(days=50))
        self.assertEqual(Subject.objects.count(), 1)
        self.assertEqual(Period.objects.count(), 2)
        PeriodDelete(end_time_older_than_datetime=timezone.now() + timezone.timedelta(days=10)).delete()
        self.assertEqual(Subject.objects.get(), testsubject)
        self.assertEqual(Period.objects.get(), period_not_deleted)

    def does_subject_deleted_if_all_periods_are_deleted(self):
        testsubject = mommy.make('core.Subject')
        mommy.make('core.Period', parentnode=testsubject, end_time=timezone.now())
        self.assertEqual(Subject.objects.count(), 1)
        self.assertEqual(Period.objects.count(), 1)
        PeriodDelete(end_time_older_than_datetime=timezone.now() + timezone.timedelta(days=10)).delete()
        self.assertEqual(Subject.objects.count(), 0)
        self.assertEqual(Period.objects.count(), 0)

    def test_deletes_stored_file_for_comment(self):
        testperiod = mommy.make('core.Period', end_time=timezone.now())
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = mommy.make('devilry_group.FeedbackSet', group=testgroup)
        testcomment = mommy.make('devilry_group.GroupComment', feedback_set=testfeedbackset)
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        file_path = commentfile.file.path
        self.assertTrue(os.path.exists(file_path))
        PeriodDelete(end_time_older_than_datetime=timezone.now() + timezone.timedelta(days=10)).delete()
        self.assertFalse(os.path.exists(file_path))

    def test_deletes_multiple_stored_files_for_comment(self):
        testperiod = mommy.make('core.Period', end_time=timezone.now())
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = mommy.make('devilry_group.FeedbackSet', group=testgroup)
        testcomment = mommy.make('devilry_group.GroupComment', feedback_set=testfeedbackset)
        commentfile1 = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile1.txt')
        commentfile1.file.save('testfile1.txt', ContentFile('testcontent'))
        commentfile2 = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile2.txt')
        commentfile2.file.save('testfile2.txt', ContentFile('testcontent'))
        file_path1 = commentfile1.file.path
        file_path2 = commentfile2.file.path
        self.assertTrue(os.path.exists(file_path1))
        self.assertTrue(os.path.exists(file_path2))
        PeriodDelete(end_time_older_than_datetime=timezone.now() + timezone.timedelta(days=10)).delete()
        self.assertFalse(os.path.exists(file_path1))
        self.assertFalse(os.path.exists(file_path2))
        self.assertEqual(GroupComment.objects.count(), 0)
        self.assertEqual(Comment.objects.count(), 0)
        self.assertEqual(CommentFile.objects.count(), 0)

    def test_deletes_stored_files_for_multiple_comments(self):
        testperiod = mommy.make('core.Period', end_time=timezone.now())
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = mommy.make('devilry_group.FeedbackSet', group=testgroup)
        testcomment1 = mommy.make('devilry_group.GroupComment', feedback_set=testfeedbackset)
        testcomment2 = mommy.make('devilry_group.GroupComment', feedback_set=testfeedbackset)
        commentfile1 = mommy.make('devilry_comment.CommentFile', comment=testcomment1, filename='testfile1.txt')
        commentfile1.file.save('testfile1.txt', ContentFile('testcontent'))
        commentfile2 = mommy.make('devilry_comment.CommentFile', comment=testcomment2, filename='testfile2.txt')
        commentfile2.file.save('testfile2.txt', ContentFile('testcontent'))
        file_path1 = commentfile1.file.path
        file_path2 = commentfile2.file.path
        self.assertTrue(os.path.exists(file_path1))
        self.assertTrue(os.path.exists(file_path2))
        PeriodDelete(end_time_older_than_datetime=timezone.now() + timezone.timedelta(days=10)).delete()
        self.assertFalse(os.path.exists(file_path1))
        self.assertFalse(os.path.exists(file_path2))
        self.assertEqual(GroupComment.objects.count(), 0)
        self.assertEqual(Comment.objects.count(), 0)
        self.assertEqual(CommentFile.objects.count(), 0)

    def test_deletes_multiple_stored_files_for_multiple_comments(self):
        testperiod = mommy.make('core.Period', end_time=timezone.now())
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testfeedbackset = mommy.make('devilry_group.FeedbackSet', group=testgroup)
        testcomment1 = mommy.make('devilry_group.GroupComment', feedback_set=testfeedbackset)
        testcomment2 = mommy.make('devilry_group.GroupComment', feedback_set=testfeedbackset)

        commentfile1_1 = mommy.make('devilry_comment.CommentFile', comment=testcomment1, filename='testfile1_1.txt')
        commentfile1_1.file.save('testfile1_1.txt', ContentFile('testcontent'))
        commentfile1_2 = mommy.make('devilry_comment.CommentFile', comment=testcomment1, filename='testfile1_2.txt')
        commentfile1_2.file.save('testfile1_2.txt', ContentFile('testcontent'))

        commentfile2_1 = mommy.make('devilry_comment.CommentFile', comment=testcomment2, filename='testfile2_1.txt')
        commentfile2_1.file.save('testfile2_1.txt', ContentFile('testcontent'))
        commentfile2_2 = mommy.make('devilry_comment.CommentFile', comment=testcomment2, filename='testfile2_2.txt')
        commentfile2_2.file.save('testfile2_2.txt', ContentFile('testcontent'))

        file_path1_1 = commentfile1_1.file.path
        file_path1_2 = commentfile1_2.file.path
        file_path2_1 = commentfile2_1.file.path
        file_path2_2 = commentfile2_2.file.path
        self.assertTrue(os.path.exists(file_path1_1))
        self.assertTrue(os.path.exists(file_path1_2))
        self.assertTrue(os.path.exists(file_path2_1))
        self.assertTrue(os.path.exists(file_path2_2))

        PeriodDelete(end_time_older_than_datetime=timezone.now() + timezone.timedelta(days=10)).delete()
        self.assertFalse(os.path.exists(file_path1_1))
        self.assertFalse(os.path.exists(file_path1_2))
        self.assertFalse(os.path.exists(file_path2_1))
        self.assertFalse(os.path.exists(file_path2_2))
        self.assertEqual(GroupComment.objects.count(), 0)
        self.assertEqual(Comment.objects.count(), 0)
        self.assertEqual(CommentFile.objects.count(), 0)

    def test_candidates_and_related_students_are_deleted(self):
        testperiod = mommy.make('core.Period', end_time=timezone.now())
        mommy.make('core.PeriodTag', period=testperiod)
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testrelatedstudent = mommy.make('core.RelatedStudent', period=testperiod)
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=testrelatedstudent)

        self.assertEqual(RelatedStudent.objects.count(), 1)
        self.assertEqual(Candidate.objects.count(), 1)
        PeriodDelete(end_time_older_than_datetime=timezone.now() + timezone.timedelta(days=10)).delete()
        self.assertEqual(RelatedStudent.objects.count(), 0)
        self.assertEqual(Candidate.objects.count(), 0)

    def test_examiners_and_related_examiners_are_deleted(self):
        testperiod = mommy.make('core.Period', end_time=timezone.now())
        mommy.make('core.PeriodTag', period=testperiod)
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testrelatedexaminer = mommy.make('core.RelatedExaminer', period=testperiod)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer=testrelatedexaminer)

        self.assertEqual(RelatedExaminer.objects.count(), 1)
        self.assertEqual(Examiner.objects.count(), 1)
        PeriodDelete(end_time_older_than_datetime=timezone.now() + timezone.timedelta(days=10)).delete()
        self.assertEqual(RelatedExaminer.objects.count(), 0)
        self.assertEqual(Examiner.objects.count(), 0)

    def test_assignment_groups_are_deleted(self):
        testperiod = mommy.make('core.Period', end_time=timezone.now())
        mommy.make('core.PeriodTag', period=testperiod)
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        mommy.make('core.AssignmentGroup', parentnode=testassignment)

        self.assertEqual(AssignmentGroup.objects.count(), 1)
        PeriodDelete(end_time_older_than_datetime=timezone.now() + timezone.timedelta(days=10)).delete()
        self.assertEqual(AssignmentGroup.objects.count(), 0)

    def test_feedbacksets_are_deleted(self):
        testperiod = mommy.make('core.Period', end_time=timezone.now())
        mommy.make('core.PeriodTag', period=testperiod)
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('devilry_group.FeedbackSet', group=testgroup)

        self.assertEqual(FeedbackSet.objects.count(), 1)
        PeriodDelete(end_time_older_than_datetime=timezone.now() + timezone.timedelta(days=10)).delete()
        self.assertEqual(FeedbackSet.objects.count(), 0)

    def test_sanity_delete_cascade(self):
        testsubject = mommy.make('core.Subject')
        subjectpermissiongroup = mommy.make('devilry_account.SubjectPermissionGroup', subject=testsubject)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=mommy.make(settings.AUTH_USER_MODEL),
                   permissiongroup=subjectpermissiongroup.permissiongroup)

        testperiod = mommy.make('core.Period', parentnode=testsubject, end_time=timezone.now())
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup', period=testperiod)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=mommy.make(settings.AUTH_USER_MODEL),
                   permissiongroup=periodpermissiongroup.permissiongroup)
        testrelatedexaminer = mommy.make('core.RelatedExaminer', period=testperiod)
        testrelatedstudent = mommy.make('core.RelatedStudent', period=testperiod)
        mommy.make('core.PeriodTag', period=testperiod)
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer=testrelatedexaminer)
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=testrelatedstudent)
        testfeedbackset = mommy.make('devilry_group.FeedbackSet', group=testgroup)
        mommy.make('devilry_group.GroupComment', feedback_set=testfeedbackset)

        self.assertEqual(Subject.objects.count(), 1)
        self.assertEqual(SubjectPermissionGroup.objects.count(), 1)
        self.assertEqual(Period.objects.count(), 1)
        self.assertEqual(RelatedExaminer.objects.count(), 1)
        self.assertEqual(RelatedStudent.objects.count(), 1)
        self.assertEqual(PeriodTag.objects.count(), 1)
        self.assertEqual(PeriodPermissionGroup.objects.count(), 1)
        self.assertEqual(PermissionGroupUser.objects.count(), 2)
        self.assertEqual(Assignment.objects.count(), 1)
        self.assertEqual(AssignmentGroup.objects.count(), 1)
        self.assertEqual(Examiner.objects.count(), 1)
        self.assertEqual(Candidate.objects.count(), 1)
        self.assertEqual(FeedbackSet.objects.count(), 1)
        self.assertEqual(GroupComment.objects.count(), 1)
        self.assertEqual(Comment.objects.count(), 1)

        PeriodDelete(end_time_older_than_datetime=timezone.now() + timezone.timedelta(days=10)).delete()

        self.assertEqual(Subject.objects.count(), 0)
        self.assertEqual(SubjectPermissionGroup.objects.count(), 0)
        self.assertEqual(Period.objects.count(), 0)
        self.assertEqual(RelatedExaminer.objects.count(), 0)
        self.assertEqual(RelatedStudent.objects.count(), 0)
        self.assertEqual(PeriodTag.objects.count(), 0)
        self.assertEqual(PeriodPermissionGroup.objects.count(), 0)
        self.assertEqual(Assignment.objects.count(), 0)
        self.assertEqual(AssignmentGroup.objects.count(), 0)
        self.assertEqual(Examiner.objects.count(), 0)
        self.assertEqual(Candidate.objects.count(), 0)
        self.assertEqual(FeedbackSet.objects.count(), 0)
        self.assertEqual(GroupComment.objects.count(), 0)
        self.assertEqual(Comment.objects.count(), 0)
        self.assertEqual(PermissionGroup.objects.count(), 2)
        self.assertEqual(PermissionGroupUser.objects.count(), 2)
