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
# from ievv_opensource.ievv_batchframework import batchregistry
#
# # Devilry imports
# from devilry.devilry_group.views.download_files import feedbackfeed_download_files
# from devilry.devilry_group import tasks
# from devilry.devilry_group import models as group_models
#
#
# class DummyAction(batchregistry.Action):
#     def execute(self):
#         return 'test'
#
#
# class TestCompressedGroupCommentFileDownload(TestCase):
#
#     # def setUp(self):
#     #     self.registry = batchregistry.Registry()
#
#     def test_batchframework(self):
#         testcomment = mommy.make('devilry_group.GroupComment',
#                                  user_role='student',
#                                  user__shortname='testuser@example.com')
#         commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
#         commentfile.file.save('testfile.txt', ContentFile('testcontent'))
#
#         batchregistry.Registry.get_instance().add_actiongroup(
#             batchregistry.ActionGroup(
#                 name='batchframework_groupcomment',
#                 mode=batchregistry.ActionGroup.MODE_SYNCHRONOUS,
#                 actions=[
#                     tasks.GroupCommentCompressAction
#                 ]))
#         result = batchregistry.Registry.get_instance().run(actiongroup_name='batchframework_groupcomment',
#                                                            context_object=testcomment,
#                                                            test='test')
#         # print result.actiongroupresult
#         self.assertEquals(1, 1)
