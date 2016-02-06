from django_cradmin.viewhelpers import listbuilder


class PermissionGroupUserTitleDescriptionMixin(object):
    def get_title(self):
        if self.permissiongroupuser.user.fullname:
            return self.permissiongroupuser.user.fullname
        else:
            return self.permissiongroupuser.user.shortname

    def get_description(self):
        if self.permissiongroupuser.user.fullname:
            return self.permissiongroupuser.user.shortname
        else:
            return ''


class ItemValue(PermissionGroupUserTitleDescriptionMixin,
                listbuilder.itemvalue.TitleDescription):
    valuealias = 'permissiongroupuser'
