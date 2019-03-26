from cradmin_legacy.viewhelpers import listbuilder


class UserTitleDescriptionMixin(object):
    def get_title(self):
        if self.user.fullname:
            return self.user.fullname
        else:
            return self.user.shortname

    def get_description(self):
        if self.user.fullname:
            return self.user.shortname
        else:
            return ''


class ItemValue(UserTitleDescriptionMixin,
                listbuilder.itemvalue.TitleDescription):
    valuealias = 'user'
