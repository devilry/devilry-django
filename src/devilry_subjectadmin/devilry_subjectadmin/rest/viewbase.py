from djangorestframework.views import View
from djangorestframework.compat import apply_markdown
from djangorestframework.views import _remove_leading_indent
from django.utils.safestring import mark_safe
from cStringIO import StringIO

class SelfdocumentingRestView(View):
    def get_method_docs(self, methodname):
        method = getattr(self, methodname, None)
        if not method or not method.__doc__:
            return None
        docs = _remove_leading_indent(method.__doc__)
        return docs

    def get_paramtable(self):
        out = StringIO()
        out.write('<table>')
        for field in self.get_bound_form():
            #print dir(field)
            #print dir(field.field)
            out.write('<tr>')
            if field.field.required:
                meta = 'required'
            else:
                meta = 'optional'
            out.write('<td><strong>{field.name}</strong><br/><small>{meta}</small></td>'.format(field=field,
                                                                               meta=meta))
            out.write('<td>{field.field.help_text}</td>'.format(field=field))
            out.write('</tr>')
            #print '{field.name!r} {field.field.help_text!r} {field.field.required!r}'.format(field=field)
        out.write('</table>')
        return out.getvalue()

    def get_description_templatevars(self):
        """
        Returns a dict of template variables given to the description. These
        parameters can be used in the docstrings using new-style string
        formatting (I.E.: ``{parametertable}``).

        This function only adds a single parameter by default:

            paramtable
                A HTML table generated from ``self.form``. Only available if
                ``self.form`` is available.
        """
        templatevars = {}
        if self.form:
            templatevars['parametertable'] = self.get_paramtable()
        return templatevars

    def get_description_markdown(self):
        description = _remove_leading_indent(self.__doc__ or '')
        method_docs = []
        for methodname in self.allowed_methods:
            methodname = methodname.lower()
            docs = self.get_method_docs(methodname)
            if docs:
                method_docs.append('# Post\n' + docs)
        if method_docs:
            description = description + '\n\n' + '\n\n'.join(method_docs)
        return description

    def get_description_html(self):
        description = self.get_description_markdown()
        return apply_markdown(description).format(**self.get_description_templatevars())

    def get_description(self, html=False):
        return mark_safe(self.get_description_html())
