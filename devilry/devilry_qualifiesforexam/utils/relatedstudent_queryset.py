from devilry.apps.core.models.relateduser import RelatedStudent


def get_relatedstudents_queryset(period, extra_order_by_fields=None):
    """
    Get all the :class:`~.devilry.apps.core.models.RelatedStudent`s for ``period``.

    Args:
        period: The period to fetch ``RelatedStudent``s for.
        extra_order_by_fields: Optional list of fields to order the queryset by, in addition to ``user__shortname``.
            The fields should be in the format used by Django's ``order_by``-function.

    Returns:
        QuerySet: QuerySet for :class:`~.devilry.apps.core.models.RelatedStudent`
    """
    if not extra_order_by_fields:
        extra_order_by_fields = []
    queryset = (
        RelatedStudent.objects.filter(period=period)
        .select_related("user")
        .order_by(*extra_order_by_fields, "user__shortname")
    )
    return queryset