import json
from xml.sax.saxutils import quoteattr

from django.utils.safestring import mark_safe

from . import field
from . import container


class FilterListContainerMixin(object):
    template_name = "django_cradmin/uicontainer/filterlist/filterlist.django.html"

    def initialize(
        self,
        id_attribute="id",
        class_name=None,
        select_mode=None,
        auto_load_first_page=True,
        get_items_api_url=None,
        components=None,
        initially_selected_item_ids=None,
    ):
        self._id_attribute = id_attribute
        self._class_name = class_name
        self._select_mode = select_mode
        self._auto_load_first_page = auto_load_first_page
        self._get_items_api_url = get_items_api_url
        self._components = components or []
        self._initially_selected_item_ids = initially_selected_item_ids or []

    def get_config_dict(self):
        return {
            "idAttribute": self._id_attribute,
            "className": self._class_name,
            "selectMode": self._select_mode,
            "autoLoadFirstPage": self._auto_load_first_page,
            "getItemsApiUrl": self._get_items_api_url,
            "components": self._components,
            "initiallySelectedItemIds": self._initially_selected_item_ids,
        }

    @property
    def widget_config_json(self):
        return mark_safe(quoteattr(json.dumps(self.get_config_dict())))


class FilterListField(FilterListContainerMixin, field.BaseFieldRenderable):
    def __init__(
        self,
        id_attribute="id",
        class_name=None,
        select_mode=None,
        auto_load_first_page=True,
        get_items_api_url=None,
        components=None,
        initially_selected_item_ids=None,
        **kwargs,
    ):
        self.initialize(
            id_attribute=id_attribute,
            class_name=class_name,
            select_mode=select_mode,
            auto_load_first_page=auto_load_first_page,
            get_items_api_url=get_items_api_url,
            components=components,
            initially_selected_item_ids=initially_selected_item_ids,
        )
        super(FilterListField, self).__init__(**kwargs)

    def should_render_as_child_of_label(self):
        return False


class FilterListContainer(FilterListContainerMixin, container.AbstractContainerRenderable):
    def __init__(
        self,
        id_attribute="id",
        class_name=None,
        select_mode=None,
        auto_load_first_page=True,
        get_items_api_url=None,
        components=None,
        initially_selected_item_ids=None,
        **kwargs,
    ):
        self.initialize(
            id_attribute=id_attribute,
            class_name=class_name,
            select_mode=select_mode,
            auto_load_first_page=auto_load_first_page,
            get_items_api_url=get_items_api_url,
            components=components,
            initially_selected_item_ids=initially_selected_item_ids,
        )
        super(FilterListContainer, self).__init__(**kwargs)
