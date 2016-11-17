# from django.db import models
# from devilry.devilry_qualifiesforexam.models import Status
# from devilry.apps.core.models import Assignment
#
#
# class SubsetPluginSetting(models.Model):
#     status = models.OneToOneField(Status, primary_key=True,
#                                   related_name="%(app_label)s_%(class)s")
#
#
# class SelectedAssignment(models.Model):
#     subset = models.ForeignKey(SubsetPluginSetting)
#     assignment = models.ForeignKey(Assignment)
