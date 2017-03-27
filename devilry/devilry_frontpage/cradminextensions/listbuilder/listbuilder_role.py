from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy, pgettext_lazy
from django_cradmin import crapp
from django_cradmin.crinstance import reverse_cradmin_url
from django_cradmin.viewhelpers import listbuilder

from devilry.devilry_cradmin import devilry_listbuilder


class AbstractRoleItemValue(listbuilder.itemvalue.TitleDescription):
    valuealias = 'user'

    def get_devilryrole(self):
        raise NotImplementedError()

    def get_extra_css_classes_list(self):
        return [
            'devilry-frontpage-listbuilder-roleselect-itemvalue',
            'devilry-frontpage-listbuilder-roleselect-itemvalue-{}'.format(self.get_devilryrole()),
        ]


class StudentRoleItemValue(AbstractRoleItemValue):
    """
    Listbuilder ItemValue renderer for information about the student devilryrole.
    """
    def get_devilryrole(self):
        return 'student'

    def get_title(self):
        return pgettext_lazy('role', 'Student')

    def get_description(self):
        return pgettext_lazy('roleselect',
                             'Upload deliveries or see your delivery and feedback history.')


class ExaminerRoleItemValue(AbstractRoleItemValue):
    """
    Listbuilder ItemValue renderer for information about the examiner devilryrole.
    """
    def get_devilryrole(self):
        return 'examiner'

    def get_title(self):
        return pgettext_lazy('role', 'Examiner')

    def get_description(self):
        return pgettext_lazy('roleselect',
                             'Give students feedback on their deliveries as examiner.')


class AnyAdminRoleItemValue(AbstractRoleItemValue):
    """
    Listbuilder ItemValue renderer for information about the anyadmin devilryrole.
    """
    def get_devilryrole(self):
        return 'anyadmin'

    def get_title(self):
        return pgettext_lazy('role', 'Administrator')

    def get_description(self):
        return pgettext_lazy('roleselect',
                             'Manage departments, courses, semesters and assignments.')


class AbstractRoleItemFrame(devilry_listbuilder.common.GoForwardLinkItemFrame):
    valuealias = 'user'

    def get_url(self):
        raise NotImplementedError()

    def get_devilryrole(self):
        raise NotImplementedError()

    def get_extra_css_classes_list(self):
        return [
            'devilry-frontpage-listbuilder-roleselect-itemframe',
            'devilry-frontpage-listbuilder-roleselect-itemframe-{}'.format(self.get_devilryrole()),
        ]


class StudentRoleItemFrame(AbstractRoleItemFrame):
    """
    Listbuilder ItemFrame renderer for the student devilryrole.
    """
    def get_devilryrole(self):
        return 'student'

    def get_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_student',
            appname='dashboard',
            roleid=None,
            viewname=crapp.INDEXVIEW_NAME)


class ExaminerRoleItemFrame(AbstractRoleItemFrame):
    """
    Listbuilder ItemFrame renderer for the examiner devilryrole.
    """
    def get_devilryrole(self):
        return 'examiner'

    def get_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_examiner',
            appname='assignmentlist',
            roleid=None,
            viewname=crapp.INDEXVIEW_NAME)


class AnyAdminRoleItemFrame(AbstractRoleItemFrame):
    """
    Listbuilder ItemFrame renderer for the anyadmin devilryrole.
    """
    def get_devilryrole(self):
        return 'anyadmin'

    def get_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_admin',
            appname='overview',
            roleid=None,
            viewname=crapp.INDEXVIEW_NAME)


class RoleSelectList(listbuilder.lists.RowList):
    def __init__(self, user):
        super(RoleSelectList, self).__init__()
        self.user = user
        self.__build_list()

    def __append_student_item(self):
        item = StudentRoleItemFrame(inneritem=StudentRoleItemValue(value=self.user))
        self.append(item)

    def __append_examiner_item(self):
        item = ExaminerRoleItemFrame(inneritem=ExaminerRoleItemValue(value=self.user))
        self.append(item)

    def __append_anyadmin_item(self):
        item = AnyAdminRoleItemFrame(inneritem=AnyAdminRoleItemValue(value=self.user))
        self.append(item)

    def __build_list(self):
        user_model = get_user_model()
        self.user_is_student = user_model.objects.user_is_student(self.user)
        self.user_is_examiner = user_model.objects.user_is_examiner(self.user)
        self.user_is_anyadmin = user_model.objects.user_is_admin_or_superuser(self.user)
        self.user_has_no_roles = True
        if self.user_is_student:
            self.__append_student_item()
            self.user_has_no_roles = False
        if self.user_is_examiner:
            self.__append_examiner_item()
            self.user_has_no_roles = False
        if self.user_is_anyadmin:
            self.__append_anyadmin_item()
            self.user_has_no_roles = False

    def get_extra_css_classes_list(self):
        return ['devilry-frontpage-roleselectlist']
