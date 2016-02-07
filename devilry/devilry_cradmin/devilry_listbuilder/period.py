from django_cradmin.viewhelpers import listbuilder


class AdminItemValueMixin(object):
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


class StudentItemValueMixin(object):
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
