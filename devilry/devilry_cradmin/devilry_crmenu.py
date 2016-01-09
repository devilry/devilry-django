from django.core.urlresolvers import reverse
from django_cradmin import crmenu


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

    def build_menu(self):
        self.add_headeritem_object(BreadcrumbMenuItem(
            label='Devilry',
            url=reverse('devilry_frontpage')
            # url=reverse_cradmin_url(
            #     instanceid='devilry_frontpage',
            #     appname='overview',
            #     roleid=self.request.user.id,
            #     viewname=crapp.INDEXVIEW_NAME
            # )
        ))

    def render(self, context):
        """
        Render the menu.

        Returns:
            The menu as HTML.
        """
        context['devilry_crmenu_devilryrole'] = self.devilryrole
        return super(Menu, self).render(context)
