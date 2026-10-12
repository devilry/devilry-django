import re
from collections import OrderedDict

from django.apps import apps
from django.utils.translation import gettext_lazy

from cradmin_legacy import crapp, crinstance, crmenu
from cradmin_legacy.crinstance import reverse_cradmin_url
from cradmin_legacy.crsettings import get_setting
from cradmin_legacy.decorators import has_access_to_cradmin_instance
from cradmin_legacy.superuserui.crapps import djangoapp, djangomodel
from cradmin_legacy.superuserui.views import dashboardview


class ModelConfig:
    def __init__(self, model_class=None, menulabel=None, crapp_class=None):
        self.model_class = model_class
        self.menulabel = menulabel
        self.crapp_class = crapp_class
        self.djangoappconfig = None  # This is set in DjangoAppConfig.add_model()

    def get_model_class(self):
        if self.model_class:
            return self.model_class
        else:
            raise NotImplementedError(
                "You must override get_model_class() or provide the ``model_class`` parameter for __init__()."
            )

    def get_menulabel(self):
        if self.menulabel:
            return self.menulabel
        else:
            return self.get_model_class()._meta.verbose_name_plural.capitalize()

    def get_view_url(self, viewname, args=None, kwargs=None):
        return reverse_cradmin_url(
            instanceid=self.djangoappconfig.registry.id,
            appname=self.get_unique_identifier(),
            viewname=viewname,
            args=args,
            kwargs=kwargs,
        )

    def get_indexview_url(self):
        return self.get_view_url(viewname=crapp.INDEXVIEW_NAME)

    def get_foreignkeyselectview_url(self):
        return self.get_view_url(viewname="foreignkeyselect")

    def get_manytomanyselectview_url(self):
        return self.get_view_url(viewname="manytomanyselect")

    def get_unique_identifier(self):
        return f"{self.model_class._meta.app_label}_{self.model_class._meta.model_name}"

    def get_crapp_class(self):
        if self.crapp_class:
            return self.crapp_class
        else:
            return djangomodel.DjangoModelCrApp

    def make_crapp_class(self):
        me = self

        class App(self.get_crapp_class()):
            modelconfig = me

        return App

    def __str__(self):
        return self.get_menulabel()


class DjangoAppConfig:
    def __init__(self, app_label=None, menulabel=None, crapp_class=None):
        self.app_label = app_label
        self.menulabel = menulabel
        self.crapp_class = crapp_class
        self._modelconfigs = OrderedDict()
        self.registry = None  # This is set in Registry.add_djangoapp()

    def get_app_label(self):
        if self.app_label:
            return self.app_label
        else:
            raise NotImplementedError(
                "You must override get_app_label() or provide the ``app_label`` parameter for __init__()."
            )

    def get_indexview_url(self):
        return reverse_cradmin_url(instanceid=self.registry.id, appname=self.get_app_label())

    def get_menulabel(self):
        if self.menulabel:
            return self.menulabel
        else:
            return self.get_app_config().verbose_name.capitalize()

    def add_model(self, modelconfig):
        self._modelconfigs[modelconfig.get_model_class()] = modelconfig
        modelconfig.djangoappconfig = self
        self.registry._register_modelconfig(modelconfig=modelconfig)

    def get_app_config(self):
        return apps.get_app_config(self.get_app_label())

    def add_all_models(self):
        def get_model_verbose_name_plural(model_class):
            return model_class._meta.verbose_name_plural

        for model_class in sorted(self.get_app_config().get_models(), key=get_model_verbose_name_plural):
            self.add_model(ModelConfig(model_class=model_class))

    def iter_modelconfigs(self):
        return iter(self._modelconfigs.values())

    def get_crapp_class(self):
        if self.crapp_class:
            return self.crapp_class
        else:
            return djangoapp.DjangoAppCrApp

    def make_crapp_class(self):
        me = self

        class App(self.get_crapp_class()):
            djangoappconfig = me

        return App


class Registry:
    def __init__(self, id, urlpath_regex=r"^/superuser.*$"):
        self.id = id
        self.urlpath_regex = urlpath_regex
        self._djangoappconfigs = OrderedDict()
        self._modelconfigmap = {}

    def get_title(self):
        return gettext_lazy("Superuser UI")

    def iter_djangoappconfigs(self):
        return iter(self._djangoappconfigs.values())

    def add_djangoapp(self, djangoappconfig):
        self._djangoappconfigs[djangoappconfig.get_app_label()] = djangoappconfig
        djangoappconfig.registry = self
        return djangoappconfig

    def _register_modelconfig(self, modelconfig):
        """
        Called by :meth:`.DjangoAppConfig.add_model`.
        """
        self._modelconfigmap[modelconfig.get_model_class()] = modelconfig

    def make_menu_class(self):
        me = self

        class Menu(crmenu.Menu):
            def add_modelconfigs(self, appconfig, appmenuitem):
                for modelconfig in appconfig.iter_modelconfigs():
                    appmenuitem.add_childitem(
                        label=modelconfig.get_menulabel(),
                        url=self.appindex_url(modelconfig.get_unique_identifier()),
                        active=self.request.cradmin_app.appname == modelconfig.get_unique_identifier(),
                    )

            def add_appconfig(self, appconfig):
                childappnames = set()
                for modelconfig in appconfig.iter_modelconfigs():
                    childappnames.add(modelconfig.get_unique_identifier())
                appmenuitem = self.add_menuitem(
                    label=appconfig.get_menulabel(),
                    url=appconfig.get_indexview_url(),
                    active=self.request.cradmin_app.appname == appconfig.get_app_label(),
                    expanded=self.request.cradmin_app.appname in childappnames,
                )
                self.add_modelconfigs(appconfig=appconfig, appmenuitem=appmenuitem)

            def build_menu(self):
                for appconfig in me.iter_djangoappconfigs():
                    self.add_appconfig(appconfig=appconfig)

        return Menu

    def get_dashboardview_class(self):
        return dashboardview.View

    def get_modelconfig_for_model_class(self, model_class):
        return self._modelconfigmap.get(model_class, None)

    def make_cradmin_instance_class(self):  # noqa
        me = self

        class CrAdminInstance(crinstance.BaseCrAdminInstance):
            id = me.id
            menuclass = me.make_menu_class()

            def has_access(self):
                return self.request.user.is_superuser

            def get_cradmin_theme_path(self):
                return get_setting("CRADMIN_LEGACY_SUPERUSERUI_THEME_PATH", None)

            def get_superuserui_registry(self):
                return me

            def get_foreignkeyselectview_url(self, model_class):
                modelconfig = me.get_modelconfig_for_model_class(model_class=model_class)
                if modelconfig:
                    return modelconfig.get_foreignkeyselectview_url()
                else:
                    return None

            def get_manytomanyselectview_url(self, model_class):
                modelconfig = me.get_modelconfig_for_model_class(model_class=model_class)
                if modelconfig:
                    return modelconfig.get_manytomanyselectview_url()
                else:
                    return None

            @classmethod
            def get_apps(cls):
                apps = []
                for appconfig in me.iter_djangoappconfigs():
                    apps.append((appconfig.get_app_label(), appconfig.make_crapp_class()))
                    for modelconfig in appconfig.iter_modelconfigs():
                        apps.append((modelconfig.get_unique_identifier(), modelconfig.make_crapp_class()))
                return apps

            @classmethod
            def matches_urlpath(cls, urlpath):
                return re.match(me.urlpath_regex, urlpath)

            @classmethod
            def get_instance_frontpage_view(cls):
                return has_access_to_cradmin_instance(me.get_dashboardview_class().as_view())

        return CrAdminInstance


#: The default superuserui registry.
default = Registry(id="cradmin_legacy_superuserui_default")
