from haystack import indexes


class BaseIndex(indexes.SearchIndex):
    """
    This ensures that all indexes uses the same field for ``document=True``.
    It is also convenient to have the same superclass for all indexes.

    See: http://unfoldthat.com/2011/05/04/you-should-use-django-haystack-like-this.html
    """
    text = indexes.CharField(document=True, use_template=True)
    suggestions = indexes.CharField()

    def prepare(self, obj):
        prepared_data = super(BaseIndex, self).prepare(obj)
        prepared_data['suggestions'] = prepared_data['text']
        return prepared_data
