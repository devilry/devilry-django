
from ..simplified.administrator import Node
import fields
from restview import RestView
from base import SearchFormBase


class RestNode(Node, RestView):
    class SearchForm(SearchFormBase):
        orderby = fields.CharListWithFallbackField(
                fallbackvalue=Node.get_default_ordering())
