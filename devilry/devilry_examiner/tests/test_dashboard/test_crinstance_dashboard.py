# import mock
# from django import test
# from django.conf import settings
# from model_mommy import mommy
#
# from devilry.devilry_examiner.views.dashboard import crinstance_dashboard
#
#
# class TestCradminInstanceDashboard(test.TestCase):
#     def test_get_rolequeryset_not_matching_requestuser(self):
#         requestuser = mommy.make(settings.AUTH_USER_MODEL)
#         mockrequest = mock.MagicMock()
#         mockrequest.user = mock.MagicMock()
#         mockrequest.user.id = requestuser.id + 1
#         crinstance = crinstance_dashboard.CrAdminInstance(request=mockrequest)
#         self.assertEqual(0, crinstance.get_rolequeryset().count())
#
#     def test_get_rolequeryset_matching_requestuser(self):
#         requestuser = mommy.make(settings.AUTH_USER_MODEL)
#         mockrequest = mock.MagicMock()
#         mockrequest.user = requestuser
#         crinstance = crinstance_dashboard.CrAdminInstance(request=mockrequest)
#         self.assertEqual(1, crinstance.get_rolequeryset().count())
