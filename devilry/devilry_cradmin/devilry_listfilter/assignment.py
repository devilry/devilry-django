from django.db import models
from django.db.models.functions import Lower, Concat
from django.utils.translation import gettext_lazy, pgettext_lazy
from cradmin_legacy.viewhelpers import listfilter


class OrderBy(listfilter.django.single.select.AbstractOrderBy):
    def get_slug(self):
        return 'orderby'

    def get_label(self):
        return pgettext_lazy('orderby', 'Sort')

    def get_name_ordering_options(self):
        return [
            ('name_ascending', {
                'label': gettext_lazy('Name'),
                'order_by': [Lower(
                    Concat(
                        'parentnode__parentnode__short_name',
                        'parentnode__short_name',
                        'long_name',
                        output_field=models.CharField()
                    ))],
            }),
            ('name_descending', {
                'label': gettext_lazy('Name (descending)'),
                'order_by': [Lower(
                    Concat(
                        'parentnode__parentnode__short_name',
                        'parentnode__short_name',
                        'long_name',
                        output_field=models.CharField()
                    )).desc()],
            }),
        ]

    def get_ordering_options(self):
        return [
            ('', {
                'label': gettext_lazy('First deadline (newest first)'),
                'order_by': ['-first_deadline'],
            }),
            ('first_deadline_ascending', {
                'label': gettext_lazy('First deadline (oldest first)'),
                'order_by': ['first_deadline'],
            }),
            ('publishing_time_descending', {
                'label': gettext_lazy('Publishing time (newest first)'),
                'order_by': ['-publishing_time'],
            }),
            ('publishing_time_ascending', {
                'label': gettext_lazy('Publishing time (oldest first)'),
                'order_by': ['publishing_time'],
            })
        ] + self.get_name_ordering_options()


class OrderByFullPath(OrderBy):
    def get_name_ordering_options(self):
        return [
            ('name_ascending', {
                'label': gettext_lazy('Name (ascending)'),
                'order_by': [Lower(
                    Concat(
                        'parentnode__parentnode__short_name',
                        'parentnode__short_name',
                        'long_name',
                        output_field=models.CharField()
                    ))],
            }),
            ('name_descending', {
                'label': gettext_lazy('Name (descending)'),
                'order_by': [Lower(
                    Concat(
                        'parentnode__parentnode__short_name',
                        'parentnode__short_name',
                        'long_name',
                        output_field=models.CharField()
                    )).desc()],
            }),
        ]


class OrderByDeliveryTime(OrderByFullPath):
    def get_name_ordering_options(self):
        out = super().get_name_ordering_options()
        out.append(
            ('delivery_time_ascending', {
                'label': gettext_lazy('Delivery Time (ascending)'),
                'order_by': [
                        'assignmentgroups__cached_data__last_feedbackset__created_datetime',
                    ],
            }),
        )
        out.append(
            ('delivery_time_descending', {
                'label': gettext_lazy('Delivery Time (descending)'),
                'order_by': [
                        '-assignmentgroups__cached_data__last_feedbackset__created_datetime'
                    ],
            }),
        )
        return out


class AssignmentCheckboxFilter(listfilter.basefilters.multi.abstractcheckbox.AbstractCheckboxFilter):
    def __init__(self, **kwargs):
        self.view = kwargs.pop('view', None)
        super().__init__(**kwargs)

    def get_slug(self):
        return 'assignmentname'

    def get_label(self):
        return pgettext_lazy('assignment filter', 'Assignments')

    def get_choices(self):
        choices = [
            ('has-delivery', pgettext_lazy('assignment status', 'Has delivery')),
        ]
        return choices

    def filter(self, queryobject):
        from devilry.devilry_group.models import GroupComment
        cleaned_value = self.get_cleaned_value() or ''
        if cleaned_value == 'has-delivery':
            out = queryobject \
                    .exclude(assignmentgroups__feedbackset__groupcomment__visibility=GroupComment.VISIBILITY_PRIVATE) \
                    .filter(assignmentgroups__feedbackset__groupcomment__commentfile__isnull=False)
            return out
        else:
            return queryobject
