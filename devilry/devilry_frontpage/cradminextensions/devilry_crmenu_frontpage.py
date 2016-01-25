from devilry.devilry_cradmin import devilry_crmenu


class Menu(devilry_crmenu.Menu):
    devilryrole = None

    def get_frontpage_breadcrumb_is_active(self):
        return True
