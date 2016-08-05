# # Python imports
# import mock
# import shutil
# from StringIO import StringIO
# from zipfile import ZipFile
# from model_mommy import mommy
# import time
#
# # Django imports
# from django.http import Http404
# from django.test import TestCase
# from django.conf import settings
# from django.core.files.base import ContentFile
# from django.utils import timezone
#
# from ievv_opensource.ievv_batchframework.models import BatchOperation
#
# # Devilry imports
# from devilry.devilry_group.views.download_files import feedbackfeed_download_files
# from devilry.devilry_group import models as group_models
# from devilry.devilry_group.views.download_files import batch_zip
#
#
# class TestCompressedGroupCommentFileDownload(TestCase):
#     def test_groupcomment_files_download(self):
#         # Test download of all files for GroupComment.
#         testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='dewey@example.com', fullname='Dewey Duck')
#         testcomment = mommy.make('devilry_group.GroupComment', user=testuser, user_role='student')
#         commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
#         commentfile.file.save('testfile.txt', ContentFile('testcontent'))
#
#         BatchOperation.objects.create_asyncronous(
#             context_object_id=testcomment.id,
#             operationtype='zip-groupcomment'
#         )
#
#         # Run celery task
#         batch_zip.get_zipped_response(testcomment)
#         while True:
#             if BatchOperation.objects.get(context_object_id=testcomment.id).result == BatchOperation.RESULT_SUCCESSFUL:
#                 break
#             else:
#                 print 'Not finished yet'
#             time.sleep(5)
#
#         batchoperation = BatchOperation.objects.get(context_object_id=testcomment.id)
#         # print batchoperation.output_data()
#
#         # testdownloader = feedbackfeed_download_files.CompressedGroupCommentFileDownload()
#         # mockrequest = mock.MagicMock()
#         # mockrequest.cradmin_role = testcomment.feedback_set.group
#         # mockrequest.user = testuser
#         # response = testdownloader.get(mockrequest, testcomment.id)
#         # zipfileobject = ZipFile(StringIO(response.content))
#         # filecontents = zipfileobject.read('testfile.txt')
#         # self.assertEquals(filecontents, 'testcontent')
