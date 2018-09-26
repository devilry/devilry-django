from django.utils.translation import ugettext_lazy
from django_cradmin.viewhelpers.listbuilder.itemvalue import TitleDescription


class WithResultValueRenderable(TitleDescription):
    """
    For rendering results number in list filter views.
    """
    def get_object_name_singular(self, num_matches):
        """
        String representation of the objects listed in singular form.
        """
        return 'object'

    def get_object_name_plural(self, num_matches):
        """
        String representation of the objects listed in plural form.
        """
        return 'objects'

    def get_title(self):
        num_matches = self.kwargs['num_matches']
        if num_matches == 1:
            object_name = self.get_object_name_singular(num_matches=num_matches)
        else:
            object_name = self.get_object_name_plural(num_matches=num_matches)
        return ugettext_lazy('Found %(result_num)s of %(total_num)s %(object_name)s') % {
            'result_num': self.kwargs['num_matches'],
            'total_num': self.kwargs['num_total'],
            'object_name': object_name
        }

    def get_base_css_classes_list(self):
        """
        Adds the ``django-cradmin-listbuilder-itemvalue-titledescription`` css class
        in addition to the classes added by the superclasses.
        """
        return []
