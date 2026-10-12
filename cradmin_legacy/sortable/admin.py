from django.contrib import admin


class SortableModelAdmin(admin.ModelAdmin):
    """
    ModelAdmin that automatically sets the ``sort_index`` of newly added items
    last in their parent. It also makes ``sort_index`` read-only by default.

    Used just like ``django.contrib.admin.ModelAdmin``.
    """

    #: If this is ``True`` , we make the ``sort_index`` field
    #: read-only. Override this to avoid this magic (typically for debugging).
    make_sort_index_readonly = False

    def save_model(self, request, obj, form, change):
        """
        Overridden to set the sortindex on save if the pk is None.
        """
        if obj.sort_index is None:
            if obj.pk is None:
                self.model.objects.set_newitem_sort_index_to_last(obj)
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        """
        Overridden to make the sortindex readonly if :obj:`.make_sort_index_readonly`
        is ``True``.
        """
        readonly_fields = super().get_readonly_fields(request, obj=obj)
        if self.make_sort_index_readonly:
            readonly_fields = list(readonly_fields)
            if "sort_index" not in readonly_fields:
                readonly_fields.append("sort_index")
        return readonly_fields
