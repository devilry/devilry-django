from django.db import models

from cradmin_legacy import datetimeutils
from cradmin_legacy.viewhelpers.listfilter.basefilters.single import abstractselect
from cradmin_legacy.viewhelpers.listfilter.django.base import DjangoOrmFilterMixin


class Boolean(abstractselect.AbstractBoolean, DjangoOrmFilterMixin):
    """
    A boolean filter that works on any BooleanField.
    False and None is considered ``False``.

    Examples:

        A model for this example::

            class MyModel(models.Model):
                is_active = models.BooleanField(default=True)

        Create the filter::

            listfilter.django.single.select.Boolean(
                slug='is_active', label='Is active?')
    """

    def get_query(self, modelfield):
        return models.Q(**{modelfield: False}) | models.Q(**{f"{modelfield}__isnull": True})

    def filter(self, queryobject):
        modelfield = self.get_modelfield()
        cleaned_value = self.get_cleaned_value()
        query = self.get_query(modelfield)
        if cleaned_value == "true":
            queryobject = queryobject.exclude(query)
        elif cleaned_value == "false":
            queryobject = queryobject.filter(query)
        return queryobject


class IsNotNull(Boolean, DjangoOrmFilterMixin):
    """
    A subclass of :class:`.Boolean` that works with
    foreign keys and other fields where ``None`` means no
    value and anything else means that it has a value.

    Examples:

        A model for this example::

            class MyModel(models.Model):
                owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)

        Create the filter::

            listfilter.django.single.select.IsNotNull(
                slug='owner', label='Has owner?')
    """

    def get_query(self, modelfield):
        return models.Q(**{f"{modelfield}__isnull": True})


class DateTime(abstractselect.AbstractDateTime, DjangoOrmFilterMixin):
    """
    A datetime filter that works with Django DateTimeField.

    Examples:

        A model for this example::

            class MyModel(models.Model):
                created_datetime = models.DateTimeField(auto_now_add=True)

        Create the filter::

            listfilter.django.single.select.DateTime(
                slug='created_datetime', label='Created time')
    """

    def filter_datetime_range(self, queryobject, start_datetime, end_datetime):
        modelfield = self.get_modelfield()
        start_datetime = datetimeutils.make_aware_in_default_timezone(start_datetime)
        end_datetime = datetimeutils.make_aware_in_default_timezone(end_datetime)
        return queryobject.filter(
            **{
                f"{modelfield}__gte": start_datetime,
                f"{modelfield}__lt": end_datetime,
            }
        )


class NullDateTime(DateTime):
    """
    Just like :class:`.DateTime`, but adds an option for ``None``-values.

    Examples:

        A model for this example::

            class MyModel(models.Model):
                banned_datetime = models.DateTimeField(null=True, blank=True, default=None)

        Create the filter::

            listfilter.django.single.select.NullDateTime(
                slug='banned_datetime', label='Banned time')
    """

    def null_enabled(self):
        return True

    def filter_is_null(self, queryobject):
        modelfield = self.get_modelfield()
        return queryobject.filter(**{f"{modelfield}__isnull": True})

    def filter_is_not_null(self, queryobject):
        modelfield = self.get_modelfield()
        return queryobject.filter(**{f"{modelfield}__isnull": False})


class AbstractOrderBy(abstractselect.AbstractOrderBy, DjangoOrmFilterMixin):
    """
    A "filter" that lets the user select how the queryobject should be ordered.

    You only have to override the ``get_ordering_options()``-method from
    :meth:`~cradmin_legacy.viewhelpers.listfilter.basefilters.single.abstractselect.AbstractOrderBy`.

    Examples:

        A model for this example::

            class Person(models.Model):
                name = models.CharField(max_length=255)

        Create a subclass of AbstractOrderBy::

            class OrderPersonsFilter(listfilter.django.single.select.AbstractOrderBy):
                def get_ordering_options(self):
                    return [
                        ('name', {
                            'label': 'Name',
                            'order_by': ['name'],
                        }),
                        ('name (descending)', {
                            'label': 'Name (descending)',
                            'order_by': ['-name'],
                        }),
                    ]

        And create the filter::

            OrderPersonsFilter(slug='orderby', label='Order by')
    """

    def filter(self, queryobject):
        cleaned_value = self.get_cleaned_value() or ""
        if cleaned_value in self.ordering_options_dict:
            order_by = self.ordering_options_dict[cleaned_value]["order_by"]
            queryobject = queryobject.order_by(*order_by)
        return queryobject
