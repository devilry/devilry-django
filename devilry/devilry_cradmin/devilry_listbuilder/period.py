from __future__ import unicode_literals
from django_cradmin.viewhelpers import listbuilder


class AdminItemValueMixin(object):
    """
    Item value for a Period in the admin UI.
    """
    valuealias = 'period'
    template_name = 'devilry_cradmin/devilry_listbuilder/period/admin-itemvalue.django.html'

    def get_title(self):
        return self.period.long_name

    def get_description(self):
        return True  # Return True to get the description-content block to render.


class AdminItemValue(AdminItemValueMixin, listbuilder.itemvalue.TitleDescription):
    """
    ItemValue renderer for a single period for admins.
    """
    def get_base_css_classes_list(self):
        cssclasses = super(AdminItemValue, self).get_base_css_classes_list()
        cssclasses.append('devilry-cradmin-perioditemvalue-admin')
        return cssclasses


class StudentItemValueMixin(object):
    """
    Item value for a Period in the student UI.

    Requires the Period queryset to be annotated with:

    - :meth:`devilry.apps.core.models.PeriodQuerySet.extra_annotate_with_assignmentcount_for_studentuser`.
    - :meth:`devilry.apps.core.models.PeriodQuerySet.extra_annotate_with_user_qualifies_for_final_exam`.
    """
    valuealias = 'period'
    template_name = 'devilry_cradmin/devilry_listbuilder/period/student-itemvalue.django.html'

    def get_title(self):
        return self.period.long_name

    def get_description(self):
        return True  # Return True to get the description-content block to render.


class StudentItemValue(StudentItemValueMixin, listbuilder.itemvalue.TitleDescription):
    """
    ItemValue renderer for a single period for students.
    """
    def get_base_css_classes_list(self):
        cssclasses = super(StudentItemValue, self).get_base_css_classes_list()
        cssclasses.append('devilry-cradmin-perioditemvalue-student')
        return cssclasses
