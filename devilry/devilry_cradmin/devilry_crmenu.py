from django.urls import reverse
from django.template import defaultfilters
from cradmin_legacy import crapp, crinstance
from cradmin_legacy import crmenu
from cradmin_legacy.crinstance import reverse_cradmin_url


class BreadcrumbMenuItem(crmenu.MenuItem):
    template_name = 'devilry_cradmin/devilry_crmenu/breadcrumb-menuitem.django.html'

    def get_item_css_class(self):
        return 'cradmin-legacy-menu-item devilry-cradmin-legacy-menuitem-breadcrumb'


class AccountMenuItem(crmenu.MenuItem):
    template_name = 'devilry_cradmin/devilry_crmenu/account-menuitem.django.html'

    def __init__(self, user, url):
        self.user = user
        super(AccountMenuItem, self).__init__(label='', url=url)

    def get_item_css_class(self):
        return 'cradmin-legacy-menu-item devilry_accountbutton'

    def get_link_css_class(self):
        return 'devilry_accountbutton__link'


class Menu(crmenu.Menu):
    """
    Base class for all cradmin menus in Devilry.
    """
    template_name = 'devilry_cradmin/devilry_crmenu/menu.django.html'
    devilryrole = None

    def get_frontpage_breadcrumb_is_active(self):
        return False

    def build_menu(self):
        self.add_headeritem_object(BreadcrumbMenuItem(
            label='Devilry',
            url=reverse_cradmin_url(
                instanceid='devilry_frontpage',
                appname='frontpage',
                roleid=None,
                viewname=crapp.INDEXVIEW_NAME
            ),
            active=self.get_frontpage_breadcrumb_is_active()
        ))
        self.add_footeritem_object(
            AccountMenuItem(
                user=self.request.user,
                url=crinstance.reverse_cradmin_url(
                    instanceid='devilry_account',
                    appname='account'
                )
            )
        )
        # self.add_footeritem(
        #     label=self.request.user.get_displayname(),
        #     url=crinstance.reverse_cradmin_url(
        #         instanceid='devilry_account',
        #         appname='account'
        #     )
        # )

    def render(self, context):
        """
        Render the menu.

        Returns:
            The menu as HTML.
        """
        context['devilry_crmenu_devilryrole'] = self.devilryrole
        return super(Menu, self).render(context)
