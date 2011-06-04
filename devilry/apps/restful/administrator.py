from django.forms import ModelForm


from ..simplified.administrator import Node
import fields
from restview import RestView
from base import SearchFormBase


class RestNode(RestView):
    SIMPCLASS = Node
    class SearchForm(SearchFormBase):
        orderby = fields.CharListWithFallbackField(
                fallbackvalue=Node.get_default_ordering())


    class ModelForm(ModelForm):
        class Meta:
            model = Node.CORE_MODEL
            fields = ('id', 'short_name', 'long_name', 'parentnode')
