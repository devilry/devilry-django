from cradmin_legacy import crapp
from cradmin_legacy.superuserui.views import appdashboardview


class DjangoAppCrApp(crapp.App):
    """
    Cradmin App that provides an overview of a Django app.
    """

    #: The :class:`cradmin_legacy.superuserui.superuserui_registry.DjangoAppConfig` this
    #: app belongs to.
    #: This is set automatically in
    #: :meth:`cradmin_legacy.superuserui.superuserui_registry.DjangoAppConfig.make_crapp_class`
    djangoappconfig = None

    @classmethod
    def get_appdashboardview_class(cls):
        return appdashboardview.View

    @classmethod
    def get_appurls(cls):
        return [crapp.Url(r"^$", cls.get_appdashboardview_class().as_view(), name=crapp.INDEXVIEW_NAME)]
