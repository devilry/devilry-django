from djangorestframework.views import View
from djangorestframework.views import _remove_leading_indent

class SelfdocumentingRestView(View):
    def get_method_docs(self, methodname):
        method = getattr(self, methodname, None)
        if not method or not method.__doc__:
            return None
        docs = _remove_leading_indent(method.__doc__)
        return docs

    def get_description(self, html=False):
        description = _remove_leading_indent(self.__doc__ or '')
        method_docs = []
        for methodname in self.allowed_methods:
            methodname = methodname.lower()
            docs = self.get_method_docs(methodname)
            if docs:
                method_docs.append('## Post\n' + docs)
        if method_docs:
            description = description + '\n\n# Available methods\n' + '\n\n'.join(method_docs)
        return self.markup_description(description)
