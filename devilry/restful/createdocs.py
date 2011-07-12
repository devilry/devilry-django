"""
Autogenerate documentation RESTful APIs
"""
from os.path import join

from django.template import Context, Template
from devilry.simplified import SimplifiedModelApi




CREATE_DOCS = '''Create a {{doc.model_verbose_name}}.
'''
READ_DOCS = '''Retreive a {{doc.model_verbose_name}}.
'''
UPDATE_DOCS = '''Update a {{doc.model_verbose_name}}.
'''
DELETE_DOCS = '''Delete a {{doc.model_verbose_name}}.
'''
SEARCH_DOCS = '''Search for {{doc.model_verbose_name_plural}}.


Parameters
##########


query
-----
A string to search for.


{% if doc.filters %}

filters
---------------

A list of filters, where each filter is a map of with the following entries:

    field
        A field name.
    comp
        A comparison operator.
    value
        The value to filter on.

Generic example of a *filters* list:

    .. code-block:: javascript

        [{field:"last", comp:"=", value:"McDuck"},
         {field:"score", comp:">", value:40}]

Available filters:
    {% for fieldname, filterspec in doc.filters.filterspecs.iteritems %}
        {{ fieldname }}
            Supported comparison operators: {%for comp in filterspec.supported_comp%}``{{comp|safe}}``{%if not forloop.last%}, {%endif%}{%endfor%}.
    {% endfor %}

{%endif%}

orderby
-------
List of fieldnames. Order the result by these fields.
Fieldnames can be prefixed by ``'-'`` for descending ordering.
Example: TODO generate ordeby example.

start
-----
After query, filters and orderby have been executed, the result is limited to
the values from *start* to *start+limit*. Start defalts to ``0``.

limit
-----
Limit results to this number of items. Defaults to ``50``.

{% if doc.result_fieldgroups %}
result_fieldgroups
------------------
Adds additional fields to each item in the result.
{{doc.result_fieldgroups}}

The fields are documented in :class:`{{doc.modelmodulename}}.{{doc.modelclsname}}`.
Follow fields containing ``__`` through the corrensponding related attributes.
{% endif %}



{% if doc.search_fieldgroups %}
search_fieldgroups
------------------
Adds additional fields which are searched for the ``query`` string.

{{doc.search_fieldgroups}}

The fields are documented in :class:`{{doc.modelmodulename}}.{{doc.modelclsname}}`.
Follow fields containing ``__`` through the corrensponding related attributes.
{% endif %}



Return
######

TODO: Autogenereate return example(s) containing fields.


Notes for non-standard extensions
#################################

TODO: getdata_in_qrystring and X-header
'''






class Docstring(object):
    def __init__(self, docstring, restfulcls):
        self.docstring = Template(docstring)
        self.restfulcls = restfulcls
        simplified = restfulcls._meta.simplified

        self.modelclsname = simplified._meta.model.__name__
        self.modelmodulename = simplified._meta.model.__module__
        if self.modelmodulename.endswith('.' + self.modelclsname.lower()):
            self.modelmodulename = self.modelmodulename.rsplit('.', 1)[0]
        self.modelclspath = '{0}.{1}'.format(self.modelmodulename, self.modelclsname)

        self.model_verbose_name = simplified._meta.model._meta.verbose_name
        self.model_verbose_name_plural = simplified._meta.model._meta.verbose_name_plural
        self.result_fieldgroups = self._create_fieldgroup_overview(simplified._meta.resultfields.additional_fieldgroups)
        self.search_fieldgroups = self._create_fieldgroup_overview(simplified._meta.searchfields.additional_fieldgroups)

        #self._create_filterdocs()
        self.filters = simplified._meta.filters

        self.context = Context(dict(doc=self))

    #def _create_filterdocs(self):
        #docs = {}

        #for filterspec in self.restfulcls._meta.simplified._meta.filters.filterspecs.itervalues():
            #legal = '    ' + ', '.join(filterspec.supported_comp)
            #docs[filterspec.fieldname] = legal
        #self.filterdocs = docs

    def _create_fieldgroup_overview(self, fieldgroups):
        if not fieldgroups:
            return ''
        result = ['Available values are:', '']
        for fieldgroup, fieldgroupfields in fieldgroups.iteritems():
            result.append(fieldgroup)
            result.append('    Expands to the following fields: ' + ', '.join(fieldgroupfields))
        return '\n    '.join(result)

    def get_first_para(self):
        return str(self).split('\n\n')[0].replace('\n', ' ')

    def __str__(self):
        return self.docstring.render(self.context)




class Page(object):
    TPL = '''.. _{ref}:

=============================================================================
{httpmethod} {url}
=============================================================================

{docs}'''
    def __init__(self, refprefix, methodname, httpmethod, url, docs):
        self.httpmethod = httpmethod
        self.url = url
        self.docs = docs
        self.ref = '{0}_details_{1}'.format(refprefix, methodname) # id usable by rst :ref:
        self.filename = '{0}.rst'.format(self.ref)

    def __unicode__(self):
        return self.TPL.format(**self.__dict__)

    def get_filepath(self, directory):
        return join(directory, self.filename)

    def write_to_dir(self, directory):
        open(self.get_filepath(directory), 'wb').write(unicode(self).encode('utf-8'))



class IndexItem(object):
    TPL = '''
    <tr>
        <th><a href="{pageref}.html">{httpmethod}&nbsp;{prettyrestfulurl}</a></th>
        <td>{first_para}</td>
    </tr>'''
    def __init__(self, refprefix, methodname, httpmethod, url, docs):
        self.httpmethod = httpmethod
        self.url = url
        self.prettyrestfulurl = url
        if url.endswith('id'):
            self.prettyrestfulurl = self.prettyrestfulurl[:-2]
            self.prettyrestfulurl += '<span class="restfulid">id</span>'
        self.first_para = docs.get_first_para()
        self.page = Page(refprefix, methodname, httpmethod, url, docs)

    def __unicode__(self):
        return self.TPL.format(pageref=self.page.ref, **self.__dict__)


class IndexPageItem(object):
    TPL = '''
{modelclsname}
-------------------------------------------------------------------------

.. raw:: html

    <table class="restfulindex">
        <thead>
            <tr>
                <th>Resource</th>
                <td>Description</td>
            </tr>
        </thead>
        <tbody>
            {indexitems}
        </tbody>
    </table>
'''
    def __init__(self, restfulcls, indexitems):
        self.restfulcls = restfulcls
        self.simplifiedclsname = self.restfulcls._meta.simplified.__name__
        self.modelclsname = self.restfulcls._meta.simplified._meta.model.__name__
        self.indexitems = indexitems

    def __unicode__(self):
        return self.TPL.format(simplifiedclsname=self.simplifiedclsname,
                               modelclsname=self.modelclsname,
                               indexitems='\n    '.join(unicode(i) for i in self.indexitems))

    def iterpages(self):
        for indexitem in self.indexitems:
            yield indexitem.page




class IndexPage(object):
    TPL = '''.. _{ref}:

===============================================================
{indextitle}
===============================================================

.. toctree::
    :hidden:

    {toctree}

{items}'''
    def __init__(self, indexpageitems, ref, indextitle):
        self.items = '\n\n'.join(unicode(indexpageitem) for indexpageitem in indexpageitems)
        toctreerefs = []
        for indexpageitem in indexpageitems:
            for page in indexpageitem.iterpages():
                toctreerefs.append(page.ref)
        self.toctree = '\n    '.join(toctreerefs)
        self.ref = ref
        self.indextitle = indextitle

    def __unicode__(self):
        return self.TPL.format(**self.__dict__)

    def write(self, filepath):
        open(filepath, 'wb').write(unicode(self).encode('utf-8'))



class RestfulDocs(object):
    CRUD_TO_HTTP = {'create': ('POST', False, CREATE_DOCS),
                    'read': ('GET', True, READ_DOCS),
                    'update': ('PUT', True, UPDATE_DOCS),
                    'delete': ('DELETE', True, DELETE_DOCS),
                    'search': ('GET', False, SEARCH_DOCS)}
    def iter_restfulcls_methods(self, restfulcls):
        for methodname in restfulcls._meta.simplified._meta.methods:
            if methodname.startswith('insecure_'):
                continue
            method = getattr(SimplifiedModelApi, methodname)
            yield methodname

    def _get_restfulcls_docprefix(self, restfulcls):
        appname = restfulcls.__module__.split('.')[-2] # Assume restful is in appdir.restful
        return '{0}_{1}'.format(appname, restfulcls.__name__.lower())

    def iter_restfulmanager_docs(self, restfulmanager):
        for restfulcls in restfulmanager.iter_restfulclasses():
            refprefix = self._get_restfulcls_docprefix(restfulcls)
            url = restfulcls.get_rest_url()
            indexitems = []
            for methodname in self.iter_restfulcls_methods(restfulcls):
                httpmethod, hasid, docs = self.CRUD_TO_HTTP[methodname]
                if hasid:
                    itemurl = '{0}id'.format(url)
                else:
                    itemurl = url
                indexitems.append(IndexItem(refprefix, methodname, httpmethod, itemurl, Docstring(docs, restfulcls)))
            yield IndexPageItem(restfulcls, indexitems)

    def restfulmanager_docs_to_rstfiles(self, directory, indexpageitem):
        for page in indexpageitem.iterpages():
            page.write_to_dir(directory)

    def create_in_directory(self, directory, indexpageref, indextitle, restfulmanager):
        indexpageitems = []
        for indexpageitem in self.iter_restfulmanager_docs(restfulmanager):
            indexpageitems.append(indexpageitem)
            self.restfulmanager_docs_to_rstfiles(directory, indexpageitem)
        indexpage = IndexPage(indexpageitems, indexpageref, indextitle)
        indexpage.write(join(directory, 'index.rst'))
