from builtins import object
from builtins import range

from django.core.exceptions import ValidationError
from django.db import models
from django.db import transaction
from django.utils.translation import gettext_lazy

from django_cradmin.utils.nulls_last_queryset import NullsLastQuerySet


class SortableQuerySetBase(NullsLastQuerySet):
    """
    QuerySet for :class:`.SortableManagerBase`.

    You must use this as a base class if you want to create
    a custom queryset class for models extending :class:`.SortableBase`.
    """

    parent_attribute = None

    def __set_extra_item_attrs_before_save(self, item, item_attrs_dict):
        """
        Sets values to attributes defined in the `item_attrs_dict`.

        Does nothing if `item_attrs_dict` is `None`.

        Args:
            item: Sortable model instance.
            item_attrs_dict: A dict of attribute names mapped to values.
        """
        if item_attrs_dict is not None:
            for key, val in item_attrs_dict.items():
                setattr(item, key, val)

    def __save(self, item, item_attrs_dict):
        """
        Private wrapper-method for saving that makes sure extra attributes are set on the item before save.

        Use this method instead of calling item.save() directly.
        """
        self.__set_extra_item_attrs_before_save(item, item_attrs_dict)
        item.save()

    def _get_filtered_by_parentobject_queryset(self, parentobject, none_values_order_by):
        filter_kwargs = {self.parent_attribute: parentobject}
        order_by = ["sort_index"]
        if none_values_order_by:
            order_by.extend(none_values_order_by)
        return self.filter(**filter_kwargs).order_by(*order_by)

    def _get_siblings_queryset(self, item, none_values_order_by):
        """
        Get the queryset for all the items with the same parent as the given
        item.
        """
        parentobject = getattr(item, self.parent_attribute)
        queryset = self._get_filtered_by_parentobject_queryset(parentobject, none_values_order_by)
        return queryset

    def _get_last_sortindex_within_parentobject(self, item, none_values_order_by):
        lastitem = self._get_siblings_queryset(item, none_values_order_by).last()
        if lastitem:
            return lastitem.sort_index + 1
        else:
            return 0

    def set_newitem_sort_index_to_last(self, item, none_values_order_by=None):
        """
        Sets ``item.sort_index`` to the sort_index of the last item
        in the parent + 1. Does not save.

        ONLY USE THIS FOR NEWLY CREATED ITEMS.
        """
        if item.sort_index is not None or item.pk is not None:
            raise ValueError(
                "set_newitem_sort_index_to_last should only be used "
                "when creating new items. sort_index or pk is something "
                "other than None, which indicates that this is not a new "
                "item - thus the ValueError."
            )
        item.sort_index = self._get_last_sortindex_within_parentobject(item, none_values_order_by)

    def __increase_sort_index_in_range(self, queryset, items, from_index, to_index, distance=1, item_attrs_dict=None):
        """
        Used by sort_before to increase the sort_index of all items in the given range
        """
        attrs_dict = item_attrs_dict or {}
        increase_index_for_items = [item.id for item in items[from_index:to_index]]
        queryset.filter(id__in=increase_index_for_items).update(
            sort_index=models.F("sort_index") + distance, **attrs_dict
        )

    def __decrease_sort_index_in_range(self, queryset, items, from_index, to_index, distance=1, item_attrs_dict=None):
        """
        Used by sort_before to decrease the sort_index of all items in the given range
        """
        attrs_dict = item_attrs_dict or {}
        decrease_index_for_items = [item.id for item in items[from_index:to_index]]
        queryset.filter(id__in=decrease_index_for_items).update(
            sort_index=models.F("sort_index") - distance, **attrs_dict
        )

    def __fix_sort_order(self, item, sort_before_id, none_values_order_by, item_attrs_dict):
        """
        Iterate over all the items and remove any gaps, fix any duplicate
        sort indexes and find the correct sort index for the item.

        Parameters:
            item: The item to insert in the list.
            sort_before_id: ID of the item that you want to insert ``item`` before.
            item_attrs_dict:

        Returns:
            A tuple (itemsqueryset, sort_before_index, original_item_index):

            - ``itemsqueryset`` is a queryset with all the items within the
              :obj:`.parentobject`, sorted by ``sort_index``, without any gaps
              or duplicate sort indexes.
            - ``detected_item_sort_index``: The detected new sort index for the item.
              If this is ``None``, the item should be sorted last.
            - ``original_item_index``: The sort index of the ``item``. This may not
              be the same as ``item.sort_index`` if the item has been moved up or
              down because of gaps or duplicate sort indexes.
        """
        itemsqueryset = self._get_siblings_queryset(item, none_values_order_by)
        detected_item_sort_index = None
        original_item_index = None
        for index in range(0, len(itemsqueryset)):
            current_item = itemsqueryset[index]
            if current_item.sort_index is None:
                current_item.sort_index = index
                self.__save(current_item, item_attrs_dict)
            else:
                if index < current_item.sort_index:
                    # Found gap, need to move rest of list <size-of-gap> step(s) down
                    self.__decrease_sort_index_in_range(
                        itemsqueryset,
                        itemsqueryset,
                        index,
                        len(itemsqueryset),
                        current_item.sort_index - index,
                        item_attrs_dict=item_attrs_dict,
                    )
                    itemsqueryset = self._get_siblings_queryset(item, none_values_order_by).all()
                if index > current_item.sort_index:
                    # Found duplicate sort_index, need to move rest of list one step up
                    self.__increase_sort_index_in_range(
                        itemsqueryset, itemsqueryset, index, len(itemsqueryset), item_attrs_dict=item_attrs_dict
                    )
                    itemsqueryset = self._get_siblings_queryset(item, none_values_order_by).all()

            if item.id == current_item.id:
                original_item_index = current_item.sort_index
            elif sort_before_id is not None and current_item.id == sort_before_id:
                detected_item_sort_index = current_item.sort_index
        return itemsqueryset, detected_item_sort_index, original_item_index

    def __sort_last(self, itemsqueryset, item, original_item_index, item_attrs_dict):
        if original_item_index is not None:
            # fill gap left when moving item to end
            self.__decrease_sort_index_in_range(
                itemsqueryset,
                itemsqueryset,
                original_item_index + 1,
                len(itemsqueryset),
                item_attrs_dict=item_attrs_dict,
            )
            item.sort_index = len(itemsqueryset) - 1
        else:
            item.sort_index = len(itemsqueryset)
        self.__save(item, item_attrs_dict)

    def __sort_not_last(self, itemsqueryset, item, detected_item_sort_index, original_item_index, item_attrs_dict):
        if original_item_index is None:
            # new item, move rest of list one step up, and place the new item
            self.__increase_sort_index_in_range(
                itemsqueryset,
                itemsqueryset,
                detected_item_sort_index,
                len(itemsqueryset),
                item_attrs_dict=item_attrs_dict,
            )
            item.sort_index = detected_item_sort_index
        elif original_item_index < detected_item_sort_index:
            # Move up, and fill gap left behind by moving items in the gap down
            self.__decrease_sort_index_in_range(
                itemsqueryset,
                itemsqueryset,
                original_item_index + 1,
                detected_item_sort_index,
                item_attrs_dict=item_attrs_dict,
            )
            item.sort_index = detected_item_sort_index - 1
        elif original_item_index > detected_item_sort_index:
            # Move down, and fill/create gap by moving other objects up
            self.__increase_sort_index_in_range(
                itemsqueryset,
                itemsqueryset,
                detected_item_sort_index,
                original_item_index,
                item_attrs_dict=item_attrs_dict,
            )
            item.sort_index = detected_item_sort_index
        else:
            # Item is already in the correct place
            # - Return without saving
            return
        self.__save(item, item_attrs_dict)

    def sort_before(self, item, sort_before_id, none_values_order_by=None, item_attrs_dict=None):
        """
        Sort a given item before the item with id `sort_before_id`,
        or last if `sort_before_id` is ``None``.

        Fetches all items in the same container, and makes changes in the ordering.
        Only the required updates are made.

        Parameters:
            item: A sortable item.
            sort_before_id: The item-ID to sort the item before.
            none_values_order_by: A list of values to order by for items where the sort_index is None.
                Standard Django-ORM ordering.
            item_attrs_dict (dict): A dictionary of extra attributes to set on all
                items that are sorted.
        """
        with transaction.atomic():
            itemsqueryset, detected_item_sort_index, original_item_index = self.__fix_sort_order(
                item, sort_before_id, none_values_order_by, item_attrs_dict=item_attrs_dict
            )

            if detected_item_sort_index is None:
                self.__sort_last(
                    itemsqueryset=itemsqueryset,
                    item=item,
                    original_item_index=original_item_index,
                    item_attrs_dict=item_attrs_dict,
                )
            else:
                self.__sort_not_last(
                    itemsqueryset=itemsqueryset,
                    item=item,
                    detected_item_sort_index=detected_item_sort_index,
                    original_item_index=original_item_index,
                    item_attrs_dict=item_attrs_dict,
                )

    def sort_last(self, item, none_values_order_by=None, item_attrs_dict=None):
        """
        Just a shortcut for::

            self.sort_before(item, sort_before_id=None)

        See ``sort_before`` docstring more info about the arguments.
        """
        self.sort_before(
            item, sort_before_id=None, none_values_order_by=none_values_order_by, item_attrs_dict=item_attrs_dict
        )


def validate_sort_index(value):
    if value < 0:
        raise ValidationError("Sort index must be 0 or higher.")


class SortableBase(models.Model):
    """
    Used with :class:`.SortableQuerySetBase` to make models sortable.
    """

    #: Sort index - ``0`` or higher.
    sort_index = models.PositiveIntegerField(
        blank=True, null=True, default=None, verbose_name=gettext_lazy("Sort index"), validators=[validate_sort_index]
    )

    class Meta(object):
        abstract = True
