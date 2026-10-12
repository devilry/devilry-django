class DjangoOrmFilterMixin:
    """
    Mixin class for Django ORM filters.
    """

    def get_modelfield(self):
        """
        Get the name of the model field to filter on.

        This may not make sense for all filters, but it is a fairly
        common thing to need.

        Defaults to :meth:`cradmin_legacy.viewhelpers.listfilter.base.AbstractFilter.get_slug`.
        """
        return self.get_slug()
