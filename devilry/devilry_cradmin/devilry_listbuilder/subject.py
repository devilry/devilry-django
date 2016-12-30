from __future__ import unicode_literals
from django_cradmin.viewhelpers import listbuilder


class AdminItemValueMixin(object):
    """
    Item value for a Subject in the admin UI.
    """
    valuealias = 'subject'
    template_name = 'devilry_cradmin/devilry_listbuilder/subject/admin-itemvalue.django.html'

    def get_title(self):
        return self.subject.long_name

    def get_description(self):
        return True  # Return True to get the description-content block to render.


class AdminItemValue(AdminItemValueMixin, listbuilder.itemvalue.TitleDescription):
    """
    ItemValue renderer for a single subject for admins used in the dashboard overview.
    """

    def get_base_css_classes_list(self):
        cssclasses = super(AdminItemValue, self).get_base_css_classes_list()
        cssclasses.append('devilry-cradmin-subjectitemvalue-admin')
        return cssclasses
