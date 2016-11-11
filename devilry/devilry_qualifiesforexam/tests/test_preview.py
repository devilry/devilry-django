# 3rd party imports
from devilry.devilry_qualifiesforexam.views import qualification_preview_view
from model_mommy import mommy

# Django imports
from django import test

# CrAdmin imports
from django_cradmin import cradmin_testhelpers

# Devilry imports
from devilry.project.common import settings


class TestQualificationPreviewViewPost(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = qualification_preview_view.QualificationPreviewView

    def test_post_save_status_all_students_qualify(self):
        self.assertTrue(True)
