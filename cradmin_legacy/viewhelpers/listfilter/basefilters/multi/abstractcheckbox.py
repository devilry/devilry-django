from cradmin_legacy.viewhelpers.listfilter.base.abstractfilter import AbstractFilter


class AbstractCheckboxFilter(AbstractFilter):
    """
    Abstract base class for any checkbox based multiselect filter.

    You only have to override :meth:`~AbstractCheckboxFilter.get_choices` and
    :meth:`~AbstractCheckboxFilter.filter`.
    """

    template_name = "cradmin_legacy/viewhelpers/listfilter/django/multi/checkbox/base.django.html"

    def get_choices(self):
        """
        Get choices as a list of of ``(value, label)`` pairs.
        """
        raise NotImplementedError()

    def get_choices_cached(self):
        if not hasattr(self, "_choices"):
            self._choices = self.get_choices()
        return self._choices

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
        - ``dom_id``: The DOM ID of the checkbox input field.

        Returns:
            A tuple with the list of dicts described above and the selected label.
        """
        selected_values = set(self.get_cleaned_values())
        choicesdata = []
        for value, label in self.get_choices_cached():
            is_selected = value in selected_values
            if is_selected:
                url = self.build_remove_values_url(values=[value])
            else:
                url = self.build_add_values_url(values=[value])
            choicesdata.append(
                {
                    "url": url,
                    "label": label,
                    "is_selected": is_selected,
                    "dom_id": f"{self.get_inputfield_dom_id()}_{value}",
                }
            )
        return choicesdata

    def get_context_data(self, request=None):
        context = super().get_context_data(request=None)
        context["choicesdata"] = self.get_choicesdata()
        return context

    def get_cleaned_values(self):
        cleaned_values = super().get_cleaned_values()
        choices = {value for value, label in self.get_choices_cached()}
        return [value for value in cleaned_values if value in choices]
