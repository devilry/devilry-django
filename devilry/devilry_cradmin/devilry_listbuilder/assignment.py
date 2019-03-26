from django.template.loader import render_to_string
from cradmin_legacy.viewhelpers import listbuilder


class ItemValueMixin(object):
    valuealias = 'assignment'

    def get_title(self):
        return self.assignment.long_name

    def get_description(self):
        return render_to_string('devilry_cradmin/devilry_listbuilder/assignment/description.django.html',
                                self.get_context_data())


class ItemValue(ItemValueMixin, listbuilder.itemvalue.TitleDescription):
    """
    ItemValue renderer for a single assignment.

    This is a base class that does not contain any role specific data.
    """
