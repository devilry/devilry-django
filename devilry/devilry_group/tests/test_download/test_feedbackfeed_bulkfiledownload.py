import datetime
import shutil
from StringIO import StringIO
from zipfile import ZipFile

from django import test
from django.core.files.base import ContentFile
from django.utils import timezone
from model_mommy import mommy

from devilry.devilry_comment.models import Comment
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import models as groupmodels
from devilry.devilry_group.views.download_files import feedbackfeed_bulkfiledownload


class BulkDownloadTestClass(feedbackfeed_bulkfiledownload.BulkFileDownloadBaseView):
    def get_queryset(self, request):
        return groupmodels.FeedbackSet.objects.all()

    def get_zipfilename(self, request):
        return 'testfile.zip'


class AbstractTestCase(test.TestCase):
    def tearDown(self):
        # Ignores errors if the path is not created.
        shutil.rmtree('devilry_testfiles/filestore/', ignore_errors=True)


class TestBulkFileDownloadBase(AbstractTestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_get_zipfile(self):
        assignmentgroup1 = mommy.make('core.AssignmentGroup',
                                      parentnode__parentnode__parentnode__short_name="test2100",
                                      parentnode__parentnode__short_name="spring2015",
                                      parentnode__short_name="oblig1")
        mommy.make('core.Candidate',
                   assignment_group=assignmentgroup1,
                   relatedstudent__user__shortname="testuser1")
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        feedbackset1 = mommy.make('devilry_group.FeedbackSet',
                                  group=assignmentgroup1,
                                  feedbackset_type=groupmodels.FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT,
                                  deadline_datetime=tomorrow)
        comment_fbs1_1 = mommy.make('devilry_group.GroupComment',
                                    feedback_set=feedbackset1,
                                    user_role=Comment.USER_ROLE_STUDENT)
        commentfile_fbs1_1 = mommy.make('devilry_comment.CommentFile',
                                        comment=comment_fbs1_1, filename='testfile1.txt')
        commentfile_fbs1_1.file.save('testfile1.txt', ContentFile('test'))

        testclass = BulkDownloadTestClass()
        response = testclass.get(None)
        zipfileobject = ZipFile(StringIO(response.content))
        filecontents = zipfileobject.read('test2100.spring2015.oblig1.testuser1/attempt1/testfile1.txt')
        self.assertEquals(filecontents, "test")

    def test_multiple_students_in_assignmentgroup(self):
        assignmentgroup1 = mommy.make('core.AssignmentGroup',
                                      parentnode__parentnode__parentnode__short_name="test2100",
                                      parentnode__parentnode__short_name="spring2015",
                                      parentnode__short_name="oblig1")
        mommy.make('core.Candidate',
                   assignment_group=assignmentgroup1,
                   relatedstudent__user__shortname="testuser1")
        mommy.make('core.Candidate',
                   assignment_group=assignmentgroup1,
                   relatedstudent__user__shortname="testuser2")
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        feedbackset1 = mommy.make('devilry_group.FeedbackSet',
                                  group=assignmentgroup1,
                                  feedbackset_type=groupmodels.FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT,
                                  deadline_datetime=tomorrow)
        comment_fbs1_1 = mommy.make('devilry_group.GroupComment',
                                    feedback_set=feedbackset1,
                                    user_role=Comment.USER_ROLE_STUDENT)
        commentfile_fbs1_1 = mommy.make('devilry_comment.CommentFile',
                                        comment=comment_fbs1_1, filename='testfile1.txt')
        commentfile_fbs1_1.file.save('testfile1.txt', ContentFile('test'))

        testclass = BulkDownloadTestClass()
        response = testclass.get(None)
        zipfileobject = ZipFile(StringIO(response.content))
        filecontents = zipfileobject.read('test2100.spring2015.oblig1.testuser1.testuser2/attempt1/testfile1.txt')
        self.assertEquals(filecontents, "test")

    def test_multiple_attempts(self):
        assignmentgroup1 = mommy.make('core.AssignmentGroup',
                                      parentnode__parentnode__parentnode__short_name="test2100",
                                      parentnode__parentnode__short_name="spring2015",
                                      parentnode__short_name="oblig1")
        mommy.make('core.Candidate',
                   assignment_group=assignmentgroup1,
                   relatedstudent__user__shortname="testuser1")
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        feedbackset1 = mommy.make('devilry_group.FeedbackSet',
                                  group=assignmentgroup1,
                                  feedbackset_type=groupmodels.FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT,
                                  deadline_datetime=tomorrow)
        comment_fbs1_1 = mommy.make('devilry_group.GroupComment',
                                    feedback_set=feedbackset1,
                                    user_role=Comment.USER_ROLE_STUDENT)
        commentfile_fbs1_1 = mommy.make('devilry_comment.CommentFile',
                                        comment=comment_fbs1_1, filename='testfile1.txt')
        commentfile_fbs1_1.file.save('testfile1.txt', ContentFile('test'))
        feedbackset2 = mommy.make('devilry_group.FeedbackSet',
                                  group=assignmentgroup1,
                                  feedbackset_type=groupmodels.FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT,
                                  deadline_datetime=tomorrow)
        comment_fbs2_1 = mommy.make('devilry_group.GroupComment',
                                    feedback_set=feedbackset2,
                                    user_role=Comment.USER_ROLE_STUDENT)
        commentfile_fbs2_1 = mommy.make('devilry_comment.CommentFile',
                                        comment=comment_fbs2_1, filename='testfile2.txt')
        commentfile_fbs2_1.file.save('testfile2.txt', ContentFile('test2'))

        testclass = BulkDownloadTestClass()
        response = testclass.get(None)
        zipfileobject = ZipFile(StringIO(response.content))
        filecontents = zipfileobject.read('test2100.spring2015.oblig1.testuser1/attempt1/testfile1.txt')
        self.assertEquals(filecontents, "test")
        filecontents = zipfileobject.read('test2100.spring2015.oblig1.testuser1/attempt2/testfile2.txt')
        self.assertEquals(filecontents, "test2")

    def test_multiple_files_same_attempt_same_name(self):
        assignmentgroup1 = mommy.make('core.AssignmentGroup',
                                      parentnode__parentnode__parentnode__short_name="test2100",
                                      parentnode__parentnode__short_name="spring2015",
                                      parentnode__short_name="oblig1")
        mommy.make('core.Candidate',
                   assignment_group=assignmentgroup1,
                   relatedstudent__user__shortname="testuser1")
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        feedbackset1 = mommy.make('devilry_group.FeedbackSet',
                                  group=assignmentgroup1,
                                  feedbackset_type=groupmodels.FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT,
                                  deadline_datetime=tomorrow)
        comment_fbs1_1 = mommy.make('devilry_group.GroupComment',
                                    feedback_set=feedbackset1,
                                    user_role=Comment.USER_ROLE_STUDENT)
        commentfile_fbs1_1 = mommy.make('devilry_comment.CommentFile',
                                        comment=comment_fbs1_1, filename='testfile1.txt')
        commentfile_fbs1_1.file.save('testfile1.txt', ContentFile('test'))

        comment_fbs1_2 = mommy.make('devilry_group.GroupComment',
                                    feedback_set=feedbackset1,
                                    user_role=Comment.USER_ROLE_STUDENT)
        commentfile_fbs1_2 = mommy.make('devilry_comment.CommentFile',
                                        comment=comment_fbs1_2, filename='testfile1.txt')
        commentfile_fbs1_2.file.save('testfile1.txt', ContentFile('test2'))

        testclass = BulkDownloadTestClass()
        response = testclass.get(None)
        zipfileobject = ZipFile(StringIO(response.content))
        filecontents = zipfileobject.read('test2100.spring2015.oblig1.testuser1/attempt1/testfile1.txt')
        self.assertEquals(filecontents, "test")
        filecontents = zipfileobject.read('test2100.spring2015.oblig1.testuser1/attempt1/testfile1-1.txt')
        self.assertEquals(filecontents, "test2")

    def test_multiple_files_same_comment_same_name(self):
        assignmentgroup1 = mommy.make('core.AssignmentGroup',
                                      parentnode__parentnode__parentnode__short_name="test2100",
                                      parentnode__parentnode__short_name="spring2015",
                                      parentnode__short_name="oblig1")
        mommy.make('core.Candidate',
                   assignment_group=assignmentgroup1,
                   relatedstudent__user__shortname="testuser1")
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        feedbackset1 = mommy.make('devilry_group.FeedbackSet',
                                  group=assignmentgroup1,
                                  feedbackset_type=groupmodels.FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT,
                                  deadline_datetime=tomorrow)

        comment_fbs1_2 = mommy.make('devilry_group.GroupComment',
                                    feedback_set=feedbackset1,
                                    user_role=Comment.USER_ROLE_STUDENT)
        commentfile_fbs1_2 = mommy.make('devilry_comment.CommentFile',
                                        comment=comment_fbs1_2, filename='testfile1.txt')
        commentfile_fbs1_2.file.save('testfile1.txt', ContentFile('test2'))
        commentfile_fbs1_2_2 = mommy.make('devilry_comment.CommentFile',
                                          comment=comment_fbs1_2, filename='testfile1.txt')
        commentfile_fbs1_2_2.file.save('testfile1.txt', ContentFile('test3'))

        testclass = BulkDownloadTestClass()
        response = testclass.get(None)
        zipfileobject = ZipFile(StringIO(response.content))
        filecontents = zipfileobject.read('test2100.spring2015.oblig1.testuser1/attempt1/testfile1.txt')
        self.assertEquals(filecontents, "test2")
        filecontents = zipfileobject.read('test2100.spring2015.oblig1.testuser1/attempt1/testfile1-1.txt')
        self.assertEquals(filecontents, "test3")

    def test_file_from_examiner(self):
        assignmentgroup1 = mommy.make('core.AssignmentGroup',
                                      parentnode__parentnode__parentnode__short_name="test2100",
                                      parentnode__parentnode__short_name="spring2015",
                                      parentnode__short_name="oblig1")
        mommy.make('core.Candidate',
                   assignment_group=assignmentgroup1,
                   relatedstudent__user__shortname="testuser1")
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        feedbackset1 = mommy.make('devilry_group.FeedbackSet',
                                  group=assignmentgroup1,
                                  feedbackset_type=groupmodels.FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT,
                                  deadline_datetime=tomorrow)
        comment_fbs1_1 = mommy.make('devilry_group.GroupComment',
                                    feedback_set=feedbackset1,
                                    user_role=Comment.USER_ROLE_EXAMINER)
        commentfile_fbs1_1 = mommy.make('devilry_comment.CommentFile',
                                        comment=comment_fbs1_1, filename='testfile1.txt')
        commentfile_fbs1_1.file.save('testfile1.txt', ContentFile('test'))

        testclass = BulkDownloadTestClass()
        response = testclass.get(None)
        zipfileobject = ZipFile(StringIO(response.content))
        filecontents = zipfileobject.read('test2100.spring2015.oblig1.testuser1/attempt1/from_examiner/testfile1.txt')
        self.assertEquals(filecontents, "test")

    def test_file_after_deadline(self):
        assignmentgroup1 = mommy.make('core.AssignmentGroup',
                                      parentnode__parentnode__parentnode__short_name="test2100",
                                      parentnode__parentnode__short_name="spring2015",
                                      parentnode__short_name="oblig1")
        mommy.make('core.Candidate',
                   assignment_group=assignmentgroup1,
                   relatedstudent__user__shortname="testuser1")
        yesterday = timezone.now() - datetime.timedelta(days=1)
        feedbackset1 = mommy.make('devilry_group.FeedbackSet',
                                  group=assignmentgroup1,
                                  feedbackset_type=groupmodels.FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT,
                                  deadline_datetime=yesterday)
        comment_fbs1_1 = mommy.make('devilry_group.GroupComment',
                                    feedback_set=feedbackset1,
                                    user_role=Comment.USER_ROLE_STUDENT)
        commentfile_fbs1_1 = mommy.make('devilry_comment.CommentFile',
                                        comment=comment_fbs1_1, filename='testfile1.txt')
        commentfile_fbs1_1.file.save('testfile1.txt', ContentFile('test'))

        testclass = BulkDownloadTestClass()
        response = testclass.get(None)
        zipfileobject = ZipFile(StringIO(response.content))
        filecontents = zipfileobject.read(
            'test2100.spring2015.oblig1.testuser1/attempt1/not_part_of_delivery/testfile1.txt')
        self.assertEquals(filecontents, "test")

    def test_multiple_assignmentgroups(self):
        assignmentgroup1 = mommy.make('core.AssignmentGroup',
                                      parentnode__parentnode__parentnode__short_name="test2100",
                                      parentnode__parentnode__short_name="spring2015",
                                      parentnode__short_name="oblig1")
        mommy.make('core.Candidate',
                   assignment_group=assignmentgroup1,
                   relatedstudent__user__shortname="testuser1")
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        feedbackset1 = mommy.make('devilry_group.FeedbackSet',
                                  group=assignmentgroup1,
                                  feedbackset_type=groupmodels.FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT,
                                  deadline_datetime=tomorrow)
        comment_fbs1 = mommy.make('devilry_group.GroupComment',
                                  feedback_set=feedbackset1,
                                  user_role=Comment.USER_ROLE_STUDENT)
        commentfile_fbs1 = mommy.make('devilry_comment.CommentFile',
                                      comment=comment_fbs1, filename='testfile1.txt')
        commentfile_fbs1.file.save('testfile1.txt', ContentFile('test'))

        assignmentgroup2 = mommy.make('core.AssignmentGroup',
                                      parentnode=assignmentgroup1.parentnode)
        mommy.make('core.Candidate',
                   assignment_group=assignmentgroup2,
                   relatedstudent__user__shortname="testuser2")
        feedbackset2 = mommy.make('devilry_group.FeedbackSet',
                                  group=assignmentgroup2,
                                  feedbackset_type=groupmodels.FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT,
                                  deadline_datetime=tomorrow)
        comment_fbs2 = mommy.make('devilry_group.GroupComment',
                                  feedback_set=feedbackset2,
                                  user_role=Comment.USER_ROLE_STUDENT)
        commentfile_fbs2 = mommy.make('devilry_comment.CommentFile',
                                      comment=comment_fbs2, filename='testfile2.txt')
        commentfile_fbs2.file.save('testfile1.txt', ContentFile('test2'))

        testclass = BulkDownloadTestClass()
        response = testclass.get(None)
        zipfileobject = ZipFile(StringIO(response.content))
        filecontents = zipfileobject.read('test2100.spring2015.oblig1.testuser1/attempt1/testfile1.txt')
        self.assertEquals(filecontents, "test")
        filecontents = zipfileobject.read('test2100.spring2015.oblig1.testuser2/attempt1/testfile2.txt')
        self.assertEquals(filecontents, "test2")
