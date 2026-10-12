import calendar

import datetime
from django.utils import timezone
from django.utils.translation import gettext_lazy, pgettext_lazy

from cradmin_legacy.viewhelpers.listfilter.base.abstractfilter import AbstractFilter


class AbstractSelectFilter(AbstractFilter):
    """
    Abstract base class for any select filter.

    You only have to override :meth:`~AbstractSelectFilter.get_choices` and
    :meth:`~AbstractCheckboxFilter.filter`.
    """

    template_name = "cradmin_legacy/viewhelpers/listfilter/django/single/select/base.django.html"

    def get_choices(self):
        """
        Get choices as a list of of ``(value, label)`` pairs.
        """
        raise NotImplementedError()

    def get_default_is_selected_index(self, choicesdata):
        """
        Get the index of the default selected item in choicesdata.

        Called by :meth:`.get_choicesdata` when no choice matches
        the current cleaned value.

        See the docs for ``is_selected`` in :meth:`.get_choicesdata`
        for more details.

        Parameters:
            choicesdata (list): Same format as the list returned by :meth:`.get_choicesdata`.
        """

        return 0

    def __make_choicesdata_list(self, choices, selected_value):
        selected_value = self.get_cleaned_value()
        choicesdata = []
        found_selected_value = False
        for value, label in choices:
            if isinstance(label, (tuple, list)):
                optgroup_label = value
                optgroup_choices = label
                child_choicesdata, found_selected_value_in_child = self.__make_choicesdata_list(
                    choices=optgroup_choices, selected_value=selected_value
                )
                if found_selected_value_in_child:
                    found_selected_value = True
                choicesdata.append(
                    {"is_optgroup": True, "label": optgroup_label, "child_choicesdata": child_choicesdata}
                )
            else:
                is_selected = value == selected_value
                if is_selected:
                    found_selected_value = True
                url = self.build_set_values_url(values=[value])
                choicesdata.append({"url": url, "label": label, "is_selected": is_selected})
        return choicesdata, found_selected_value

    def get_choicesdata(self):
        """
        Get choices data as a list of dicts.

        This uses :meth:`.get_choices`, and turns it into
        a list of dicts where each dict has:

        - ``url``: The URL to load when making a choice.
          This is generated using
          :meth:`~cradmin_legacy.viewhelpers.listfilter.base.AbstractFilter.build_set_values_url`
          with the value from :meth:`.get_choices` as input.
        - ``label``: The label to show (taken directly from :meth:`.get_choices`.
        - ``is_selected`` (boolean): If the current value matches the value of a choice,
          that choice will be selected. If none of them matches, the first choice is selected.
          You can change this behavior by overriding :meth:`.get_default_is_selected_index`.

        Returns:
            A tuple with the list of dicts described above and the selected label.
        """
        # selected_value = self.get_cleaned_value()
        # choicesdata = []
        # found_selected_value = False
        # for value, label in self.get_choices():
        #     is_selected = value == selected_value
        #     if is_selected:
        #         found_selected_value = True
        #     url = self.build_set_values_url(values=[value])
        #     choicesdata.append({
        #         'url': url,
        #         'label': label,
        #         'is_selected': is_selected
        #     })
        choicesdata, found_selected_value = self.__make_choicesdata_list(
            choices=self.get_choices(), selected_value=self.get_cleaned_value()
        )
        if not found_selected_value and len(choicesdata) > 0:
            selected_index = self.get_default_is_selected_index(choicesdata=choicesdata)
            choicesdata[selected_index]["is_selected"] = True
        return choicesdata

    def get_context_data(self, request=None):
        context = super().get_context_data(request=None)
        context["choicesdata"] = self.get_choicesdata()
        return context


class AbstractBoolean(AbstractSelectFilter):
    """
    Abstract boolean filter.

    Subclasses should only need to implement
    :meth:`cradmin_legacy.viewhelpers.listfilter.basefilters.single.select.AbstractSelectFilter.filter`.

    See :class:`cradmin_legacy.viewhelpers.listfilter.django.single.select.Boolean`
    for a Django ORM implementation.
    """

    def get_do_not_apply_label(self):
        """
        Returns the label for the default "do not apply this filter"
        option. Defaults to empty string.
        """
        return ""

    def get_true_label(self):
        """
        Get the label for the ``True`` option. Defaults to ``Yes`` (translatable).
        """
        return gettext_lazy("Yes")

    def get_false_label(self):
        """
        Get the label for the ``False`` option. Defaults to ``No`` (translatable).
        """
        return gettext_lazy("No")

    def get_choices(self):
        return [
            ("", self.get_do_not_apply_label()),
            ("true", self.get_true_label()),
            ("false", self.get_false_label()),
        ]


class AbstractDateTime(AbstractSelectFilter):
    """
    Abstract DateTime filter.

    Subclasses should only need to implement
    :meth:`~.DateTime.filter_datetime_range`.

    See :class:`cradmin_legacy.viewhelpers.listfilter.django.single.select.DateTime`
    for a Django ORM implementation.
    """

    def get_do_not_apply_label(self):
        """
        Returns the label for the default "do not apply this filter"
        option. Defaults to empty string.
        """
        return ""

    def get_today_label(self):
        """
        Get the label for the "today" option.

        Defaults to ``Today`` (translatable).
        """
        return gettext_lazy("Today")

    def get_yesterday_label(self):
        """
        Get the label for the "today" option.

        Defaults to ``Today`` (translatable).
        """
        return gettext_lazy("Yesterday")

    def get_last_seven_days_label(self):
        """
        Get the label for the "today" option.

        Defaults to ``Today`` (translatable).
        """
        return gettext_lazy("Last seven days")

    def get_this_week_label(self):
        """
        Get the label for the "this_week" option.

        Defaults to ``This week`` (translatable).
        """
        return gettext_lazy("This week")

    def get_this_month_label(self):
        """
        Get the label for the "this_month" option.

        Defaults to ``This month`` (translatable).
        """
        return gettext_lazy("This month")

    def get_this_year_label(self):
        """
        Get the label for the "this_year" option.

        Defaults to ``This year`` (translatable).
        """
        return gettext_lazy("This year")

    def null_enabled(self):
        """
        Override this if you want ``null`` to be a valid option.
        """
        return False

    def get_is_null_label(self):
        """
        Get the label for the ``null`` option.

        Only used if :meth:`.null_enabled` is overridden to return ``True``.

        Defaults to ``Has no value`` (translatable).
        """
        return pgettext_lazy("listfilter AbstractDateTime", "Has no value")

    def get_is_not_null_label(self):
        """
        Get the label for the ``not null`` option.

        Only used if :meth:`.null_enabled` is overridden to return ``True``.

        Defaults to ``Has value`` (translatable).
        """
        return pgettext_lazy("listfilter AbstractDateTime", "Has value")

    def get_choices(self):
        choices = [
            ("", self.get_do_not_apply_label()),
            ("today", self.get_today_label()),
            ("yesterday", self.get_yesterday_label()),
            ("last_seven_days", self.get_last_seven_days_label()),
            ("this_week", self.get_this_week_label()),
            ("this_month", self.get_this_month_label()),
            ("this_year", self.get_this_year_label()),
        ]
        if self.null_enabled():
            choices.insert(1, ("is_not_null", self.get_is_not_null_label()))
            choices.insert(1, ("is_null", self.get_is_null_label()))
        return choices

    def filter_datetime_range(self, queryobject, start_datetime, end_datetime):
        """
        Filter out all items ``>= start_datetime`` and ``< end_datetime``.

        Parameters:
            queryobject: See :meth:`~cradmin_legacy.viewhelpers.listfilter.base.abstractfilter.AbstractFilter.filter`.
            start_datetime (datetime.datetime): Start datetime.
            end_datetime (datetime.datetime): End datetime.
        """
        raise NotImplementedError()

    def filter_within_date(self, queryobject, dateobject):
        next_day_dateobject = dateobject + datetime.timedelta(days=1)
        day_start = datetime.datetime.combine(dateobject, datetime.time())
        day_end = datetime.datetime.combine(next_day_dateobject, datetime.time())
        return self.filter_datetime_range(queryobject=queryobject, start_datetime=day_start, end_datetime=day_end)

    def filter_today(self, queryobject):
        today = timezone.now().date()
        return self.filter_within_date(queryobject=queryobject, dateobject=today)

    def filter_yesterday(self, queryobject):
        yesterday = timezone.now().date() - datetime.timedelta(days=1)
        return self.filter_within_date(queryobject=queryobject, dateobject=yesterday)

    def filter_last_seven_days(self, queryobject):
        now = timezone.now()
        today = now.date()
        seven_days_ago = today - datetime.timedelta(days=7)
        seven_days_ago_day_start = datetime.datetime.combine(seven_days_ago, datetime.time())
        return self.filter_datetime_range(
            queryobject=queryobject, start_datetime=seven_days_ago_day_start, end_datetime=now
        )

    def filter_this_week(self, queryobject):
        today = timezone.now().date()
        first_date_of_week = today - datetime.timedelta(days=today.weekday())
        first_date_of_next_of_week = first_date_of_week + datetime.timedelta(days=7)
        start_of_week = datetime.datetime.combine(first_date_of_week, datetime.time())
        end_of_week = datetime.datetime.combine(first_date_of_next_of_week, datetime.time())
        return self.filter_datetime_range(
            queryobject=queryobject, start_datetime=start_of_week, end_datetime=end_of_week
        )

    def filter_this_month(self, queryobject):
        today = timezone.now().date()
        first_date_of_month = today.replace(day=1)
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        first_date_of_next_month = first_date_of_month + datetime.timedelta(days=days_in_month)
        start_of_month = datetime.datetime.combine(first_date_of_month, datetime.time())
        end_of_month = datetime.datetime.combine(first_date_of_next_month, datetime.time())
        return self.filter_datetime_range(
            queryobject=queryobject, start_datetime=start_of_month, end_datetime=end_of_month
        )

    def filter_this_year(self, queryobject):
        today = timezone.now().date()
        first_date_of_year = today.replace(month=1, day=1)
        first_date_of_next_year = first_date_of_year.replace(year=today.year + 1)
        start_of_year = datetime.datetime.combine(first_date_of_year, datetime.time())
        end_of_year = datetime.datetime.combine(first_date_of_next_year, datetime.time())
        return self.filter_datetime_range(
            queryobject=queryobject, start_datetime=start_of_year, end_datetime=end_of_year
        )

    def filter_is_null(self, queryobject):
        """
        Filter so that only values that are NULL is included.

        Must be overridden in subclasses.
        """
        raise NotImplementedError()

    def filter_is_not_null(self, queryobject):
        """
        Filter so that only values that are not NULL is included.

        Must be overridden in subclasses.
        """
        raise NotImplementedError()

    def filter(self, queryobject):
        cleaned_value = self.get_cleaned_value()
        if cleaned_value == "today":
            return self.filter_today(queryobject=queryobject)
        elif cleaned_value == "yesterday":
            return self.filter_yesterday(queryobject=queryobject)
        elif cleaned_value == "last_seven_days":
            return self.filter_last_seven_days(queryobject=queryobject)
        elif cleaned_value == "this_week":
            return self.filter_this_week(queryobject=queryobject)
        elif cleaned_value == "this_month":
            return self.filter_this_month(queryobject=queryobject)
        elif cleaned_value == "this_year":
            return self.filter_this_year(queryobject=queryobject)
        elif cleaned_value == "is_null" and self.null_enabled():
            return self.filter_is_null(queryobject=queryobject)
        elif cleaned_value == "is_not_null" and self.null_enabled():
            return self.filter_is_not_null(queryobject=queryobject)
        return queryobject


class AbstractOrderBy(AbstractSelectFilter):
    """
    Abstract order by filter --- lets the user select how the queryobject should be ordered.

    Subclasses should only need to implement
    :meth:`cradmin_legacy.viewhelpers.listfilter.basefilters.single.select.AbstractSelectFilter.filter`.

    See :class:`cradmin_legacy.viewhelpers.listfilter.django.single.select.AbstractOrderBy`
    for a Django ORM implementation.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ordering_options = self.get_ordering_options()
        self.ordering_options_dict = self.__make_ordering_options_dict(self.ordering_options)

    def __make_ordering_options_dict(self, ordering_options):
        ordering_options_dict = {}
        for value, option in ordering_options:
            if isinstance(option, (list, tuple)):
                optgroup_options_list = option
                ordering_options_dict.update(self.__make_ordering_options_dict(optgroup_options_list))
            else:
                ordering_options_dict[value] = option
        return ordering_options_dict

    def get_ordering_options(self):
        """
        Get the ordering options - must be overridden in subclasses.

        You must override this instead of ``get_choices()``.

        Should return a list of ``(value, options)`` pairs where
        ``value`` is the same as in :meth:`.AbstractSelectFilter.get_choices`
        and ``options`` is a dict with:

        - ``label``: The label for the ordering option (shown to the user).
        - ``order_by``: A list with the same format as ``*args`` for
            ``QuerySet.order_by()``.

        Examples:

            Lets say we have something with ``title`` and ``publishing_time``,
            and we want to order by ``publishing_time`` descending by default::

                def get_ordering_options(self):
                    return [
                        ('', {
                            'label': 'Publishing time (newest first)',
                            'order_by': ['-publishing_time'],
                        }),
                        ('publishing_time_asc', {
                            'label': 'Publishing time (oldest first)',
                            'order_by': ['publishing_time'],
                        }),
                        ('title', {
                            'label': 'Title',
                            'order_by': ['title'],
                        }),
                    ]

        """
        raise NotImplementedError()

    def __make_choices(self, ordering_options_list):
        choices = []
        for value, option in ordering_options_list:
            if isinstance(option, (list, tuple)):
                optgroup_label = value
                optgroup_options_list = option
                choices.append((optgroup_label, self.__make_choices(optgroup_options_list)))
            else:
                choices.append((value, option["label"]))
        return choices

    def get_choices(self):
        return self.__make_choices(self.ordering_options)
