
# Django imports
from django import test

# CrAdmin imports
from django_cradmin import cradmin_testhelpers

# Devilry imports
from devilry.devilry_qualifiesforexam.views import qualifiesforexam_view


class TestQualifiesForExamView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = qualifiesforexam_view.QualificationBaseView