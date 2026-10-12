from cradmin_legacy import crapp
from cradmin_legacy.superuserui.views import createview
from cradmin_legacy.superuserui.views import deleteview
from cradmin_legacy.superuserui.views import editview
from cradmin_legacy.superuserui.views import listview


class DjangoModelCrApp(crapp.App):
    """
    Cradmin App that provides list, create, update and delete views
    for a Django model.
    """

    #: The :class:`cradmin_legacy.superuserui.superuserui_registry.ModelConfig` this
    #: app belongs to.
    #: This is set automatically in
    #: :meth:`cradmin_legacy.superuserui.superuserui_registry.ModelConfig.make_crapp_class`
    modelconfig = None

    @classmethod
    def get_listview_class(cls):
        return listview.View

    @classmethod
    def get_foreignkeyselectview_class(cls):
        return listview.ForeignKeySelectView

    @classmethod
    def get_manytomanyselectview_class(cls):
        return listview.ManyToManySelectView

    @classmethod
    def get_editview_class(cls):
        return editview.View

    @classmethod
    def get_createview_class(cls):
        return createview.View

    @classmethod
    def get_deleteview_class(cls):
        return deleteview.View

    @classmethod
    def add_listview(cls, appurls):
        listview_class = cls.get_listview_class()
        if listview_class:
            appurls.append(crapp.Url(r"^$", listview_class.as_view(), name=crapp.INDEXVIEW_NAME))
            appurls.append(crapp.Url(r"^filter/(?P<filters_string>.+)?$", listview_class.as_view(), name="filter"))
        else:
            raise NotImplementedError(
                "You must return a view class from get_listview_class(). "
                "Note that it can be something other than a list view, "
                "such as an overview of with information/stats for the model."
            )

    @classmethod
    def add_foreignkeyselectview(cls, appurls):
        foreignkeyselectview_class = cls.get_foreignkeyselectview_class()
        if foreignkeyselectview_class:
            appurls.append(
                crapp.Url(r"^foreignkeyselect$", foreignkeyselectview_class.as_view(), name="foreignkeyselect")
            )
            appurls.append(
                crapp.Url(
                    r"^foreignkeyselect/filter/(?P<filters_string>.+)?$",
                    foreignkeyselectview_class.as_view(),
                    name="foreignkeyselect-filter",
                )
            )

    @classmethod
    def add_manytomanyselectview(cls, appurls):
        manytomanyselectview_class = cls.get_manytomanyselectview_class()
        if manytomanyselectview_class:
            appurls.append(
                crapp.Url(r"^manytomanyselect$", manytomanyselectview_class.as_view(), name="manytomanyselect")
            )
            appurls.append(
                crapp.Url(
                    r"^manytomanyselect/filter/(?P<filters_string>.+)?$",
                    manytomanyselectview_class.as_view(),
                    name="manytomanyselect-filter",
                )
            )

    @classmethod
    def add_createview(cls, appurls):
        createview_class = cls.get_createview_class()
        if createview_class:
            appurls.append(crapp.Url(r"^create/$", createview_class.as_view(), name="create"))

    @classmethod
    def add_editview(cls, appurls):
        editview_class = cls.get_editview_class()
        if editview_class:
            appurls.append(crapp.Url(r"^edit/(?P<pk>\d+)$", editview_class.as_view(), name="edit"))

    @classmethod
    def add_deleteview(cls, appurls):
        deleteview_class = cls.get_deleteview_class()
        if deleteview_class:
            appurls.append(crapp.Url(r"^delete/(?P<pk>\d+)$", deleteview_class.as_view(), name="delete"))

    @classmethod
    def get_appurls(cls):
        appurls = []
        cls.add_listview(appurls=appurls)
        cls.add_foreignkeyselectview(appurls=appurls)
        cls.add_manytomanyselectview(appurls=appurls)
        cls.add_createview(appurls=appurls)
        cls.add_editview(appurls=appurls)
        cls.add_deleteview(appurls=appurls)

        return appurls
