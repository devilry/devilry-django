from django.utils.translation import gettext
from cradmin_legacy.viewhelpers import listbuilder

class Value(listbuilder.base.ItemValueRenderer):
    template_name = "devilry_admin/listbuilder/admindashboard_subject_listbuilder/value.django.html"
    valuealias = 'subject'
