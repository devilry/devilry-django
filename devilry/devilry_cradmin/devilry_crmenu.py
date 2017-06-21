from django.core.urlresolvers import reverse
from django.template import defaultfilters
from django.utils.translation import ugettext_lazy
from django_cradmin import crapp, crinstance
from django_cradmin import crmenu
from django_cradmin.crinstance import reverse_cradmin_url


class BreadcrumbMenuItem(crmenu.MenuItem):
    template_name = 'devilry_cradmin/devilry_crmenu/breadcrumb-menuitem.django.html'

    def get_item_css_class(self):
        return 'django-cradmin-menu-item devilry-django-cradmin-menuitem-breadcrumb'


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
        self.add_footeritem(
            label=defaultfilters.truncatechars(self.request.user.get_displayname(), 15),
            url=crinstance.reverse_cradmin_url(
                instanceid='devilry_account',
                appname='account'
            )
        )

    def render(self, context):
        """
        Render the menu.

        Returns:
            The menu as HTML.
        """
        context['devilry_crmenu_devilryrole'] = self.devilryrole
        return super(Menu, self).render(context)
