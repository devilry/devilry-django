from django import forms
import fields


def _create_seachform(cls):
    """
    Create the form used on search(). Needs to be created for each
    restful class since orderby needs a fallbackvalue.
    """
    class SearchForm(forms.Form):
        query = forms.CharField(required=False)
        limit = fields.PositiveIntegerWithFallbackField(fallbackvalue=50)
        start = fields.PositiveIntegerWithFallbackField()
        orderby = fields.JsonListWithFallbackField(
                fallbackvalue=cls._meta.simplified._meta.ordering)
        result_fieldgroups = fields.JsonListWithFallbackField()
        search_fieldgroups = fields.JsonListWithFallbackField()
        filters = fields.JsonListWithFallbackField()
        filter = fields.JsonListWithFallbackField()
        sort = fields.JsonListWithFallbackField(fallbackvalue=None)
        exact_number_of_results = fields.PositiveIntegerWithFallbackField(fallbackvalue=None)
    cls.SearchForm = SearchForm
