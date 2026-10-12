from django.db import models

from cradmin_legacy.viewhelpers.listfilter.basefilters.single import abstracttextinput
from cradmin_legacy.viewhelpers.listfilter.django.base import DjangoOrmFilterMixin


class Search(abstracttextinput.AbstractSearch, DjangoOrmFilterMixin):
    """
    A "filter" that lets the user search the queryset.

    Examples:

        A model for this example::

            class MyModel(models.Model):
                name = models.CharField(max_length=255)
                title = models.TextField()

        Create the filter::

            listfilter.django.single.textinput.Search(
                slug='search', label='Search',
                modelfields=['name', 'title'])
    """

    def __init__(self, *args, **kwargs):
        """
        Parameters are the same as for
        :class:`cradmin_legacy.viewhelpers.listfilter.base.abstractfilter.AbstractFilter`,
        but you can specify one extra parameter:

            - modelfields: List of model fields to search on.
        """
        self.modelfields = kwargs.pop("modelfields", None)
        super().__init__(*args, **kwargs)

    def get_modelfields(self):
        """
        Returns a list of the model fields you want to search on.

        Defaults to the ``modelfields`` parameter for :class:`.Search`.
        """
        if self.modelfields:
            return self.modelfields
        else:
            raise NotImplementedError("You must override get_modelfields() or use the modelfields parameter.")

    def get_lookup_suffix(self):
        """
        Get the query lookup suffix. Defaults to ``"__icontains"``.
        """
        return "__icontains"

    def make_q_object_for_value(self, modelfield, cleaned_value):
        """
        Make a :class:`django.db.models.Q` object for matching the
        given ``modelfield`` with the given ``cleaned_value``.

        Args:
            modelfield (str): The modelfield to search.
            cleaned_value: The value to search for (cleaned).

        Returns:
            django.db.models.Q: A Q object.
        """
        comparison_operator = self.get_lookup_suffix()
        kwargs = {f"{modelfield}{comparison_operator}": cleaned_value}
        return models.Q(**kwargs)

    def build_query(self, modelfields, cleaned_value):
        full_query = None
        for modelfield in modelfields:
            query = self.make_q_object_for_value(modelfield=modelfield, cleaned_value=cleaned_value)
            if full_query:
                full_query |= query
            else:
                full_query = query
        return full_query

    def filter(self, queryobject):
        modelfields = self.get_modelfields()
        cleaned_value = self.get_cleaned_value()
        if cleaned_value not in ("", None):
            queryobject = queryobject.filter(self.build_query(modelfields=modelfields, cleaned_value=cleaned_value))
        return queryobject


class IntSearch(abstracttextinput.IntInputFilterMixin, Search):
    """
    A "filter" that lets the user search the queryset for exact
    matches for integers.

    Examples:

        A model for this example::

            class MyModel(models.Model):
                name = models.CharField(max_length=255)
                age = models.IntegerField()
                height = models.IntegerField()

        Create the filter::

            listfilter.django.single.textinput.IntSearch(
                slug='search_ageheight',
                label='Search for age or height',
                modelfields=['age', 'height'])

    """

    def get_lookup_suffix(self):
        return "__exact"
