from cradmin_legacy.viewhelpers import listbuilder


class AbstractSubjectOrPeriodPermissionGroupItemValue(listbuilder.itemvalue.TitleDescription):
    template_name = 'devilry_cradmin/devilry_listbuilder/' \
                    'permissiongroup/subjectorperiodpermissiongroup-itemvalue.django.html'

    def get_title(self):
        return str(self.value)

    def get_users(self):
        users = [permissiongroupuser.user
                 for permissiongroupuser in self.value.permissiongroup.permissiongroupuser_set.all()]
        return users

    def get_base_css_classes_list(self):
        cssclasses = super(AbstractSubjectOrPeriodPermissionGroupItemValue, self).get_base_css_classes_list()
        cssclasses.append('devilry-cradmin-subjectorperiodpermissiongroup-itemvalue')
        return cssclasses


class SubjectPermissionGroupItemValue(AbstractSubjectOrPeriodPermissionGroupItemValue):
    valuealias = 'subjectpermissiongroup'

    def get_base_css_classes_list(self):
        cssclasses = super(SubjectPermissionGroupItemValue, self).get_base_css_classes_list()
        cssclasses.append('devilry-cradmin-subjectpermissiongroup-itemvalue')
        return cssclasses


class PeriodPermissionGroupItemValue(AbstractSubjectOrPeriodPermissionGroupItemValue):
    valuealias = 'periodpermissiongroup'

    def get_base_css_classes_list(self):
        cssclasses = super(PeriodPermissionGroupItemValue, self).get_base_css_classes_list()
        cssclasses.append('devilry-cradmin-periodpermissiongroup-itemvalue')
        return cssclasses


class SubjectAndPeriodPermissionGroupList(listbuilder.lists.RowList):
    def get_default_frame_renderer_class(self):
        return listbuilder.itemframe.DefaultSpacingItemFrame

    def add_periodpermissiongroups(self, periodpermissiongroups):
        self.extend_with_values(value_iterable=periodpermissiongroups,
                                value_renderer_class=PeriodPermissionGroupItemValue)

    def add_subjectpermissiongroups(self, subjectpermissiongroups):
        self.extend_with_values(value_iterable=subjectpermissiongroups,
                                value_renderer_class=SubjectPermissionGroupItemValue)

    def get_base_css_classes_list(self):
        cssclasses = super(SubjectAndPeriodPermissionGroupList, self).get_base_css_classes_list()
        cssclasses.append('devilry-cradmin-subjectandperiodpermissiongroup-list')
        return cssclasses
