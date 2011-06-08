from django.forms import ModelForm


from ..simplified.administrator import Node
import fields
from restview import RestView
from base import SearchFormBase


class RestNode(RestView):
    SIMPCLASS = Node
    class SearchForm(SearchFormBase):
        orderby = fields.CharListWithFallbackField(
                fallbackvalue=Node._meta.ordering)

    class Form(ModelForm):
        class Meta:
            model = Node._meta.model
            fields = ('id', 'short_name', 'long_name', 'parentnode')
