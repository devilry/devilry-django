from django_cradmin import crapp
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

    def render(self, context):
        """
        Render the menu.

        Returns:
            The menu as HTML.
        """
        context['devilry_crmenu_devilryrole'] = self.devilryrole
        return super(Menu, self).render(context)
