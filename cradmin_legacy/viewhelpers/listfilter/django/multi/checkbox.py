from cradmin_legacy.viewhelpers.listfilter.basefilters.multi import abstractcheckbox
from cradmin_legacy.viewhelpers.listfilter.django.base import DjangoOrmFilterMixin


class RelatedModelOrFilter(abstractcheckbox.AbstractCheckboxFilter, DjangoOrmFilterMixin):
    """
    Filter on values from a related model (one-to-many or many-to-many).

    Allows the user to select the values from a list of checkboxes --- the values
    are defined by you. The query is an OR query, meaning that each selected
    value potentially increases the number of items shown instead of limiting it.

    You just have to override
    :meth:`~cradmin_legacy.viewhelpers.listfilter.basefilters.multi.abstractcheckbox.AbstractCheckboxFilter.get_choices`
    and :meth:`get_filter_attribute`.

    Examples:

        One-to-many relationship::

            class Person(models.Model):
                pass

            class Tag(models.Model):
                person = models.ForeignKey(Person, related_name='tags', on_delete=models.CASCADE)
                tag = models.SlugField()

            class TagFilter(listfilter.django.multi.checkbox.RelatedModel):
                def get_choices(self):
                    return [
                        (tag, tag)
                        for tag in Tag.objects.values_list('tag', flat=True).distinct()
                    ]

                def get_filter_attribute(self):
                    return 'tags__tag'

        Many-to-many relationship::

            class Tag(models.Model):
                tag = models.SlugField()

            class Person(models.Model):
                tags = models.ManyToManyField(Tag)

            class TagFilter(listfilter.django.multi.checkbox.RelatedModel):
                def get_choices(self):
                    return [
                        (tag, tag)
                        for tag in Tag.objects.values_list('tag', flat=True).distinct()
                    ]

                def get_filter_attribute(self):
                    return 'tags__tag'

        These examples are fairly simple. You may want to adjust get_choices() to
        only get tags actually in use or by some other query, but this should
        be a good starting point.
    """

    def get_filter_attribute(self):
        """
        Get the attribute to filter on.

        Lets say you have a ``Person`` model and a Tag model with a
        foreignkey from Tag to Person named ``person`` with ``related_name="tags"``.
        If you want to filter your Person model by tag, you would return ``tags__tag``
        (assuming ``tag`` is the attribute you want to filter by).

        The same goes for many-to-many relationships, but there you
        would call your ManyToManyField ``tags``, and still return the same value.
        """
        raise NotImplementedError()

    def filter(self, queryobject):
        cleaned_values = self.get_cleaned_values()
        if cleaned_values:
            queryobject = queryobject.filter(**{f"{self.get_filter_attribute()}__in": cleaned_values})
        return queryobject
