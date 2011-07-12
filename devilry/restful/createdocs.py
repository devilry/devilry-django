"""
Autogenerate documentation RESTful APIs
"""
from os.path import join

from devilry.simplified import SimplifiedModelApi




CREATE_DOCS = '''Create a {modelclsname}.
'''
READ_DOCS = '''Retreive a {modelclsname}.
'''
UPDATE_DOCS = '''Update a {modelclsname}.
'''
DELETE_DOCS = '''Delete a {modelclsname}.
'''
SEARCH_DOCS = '''Search for {modelclsname_plural}.
'''






class Docstring(object):
    def __init__(self, docstring, restfulcls):
        self.docstring = docstring
        self.restfulcls = restfulcls
        self.modelclsname = restfulcls._meta.simplified._meta.model._meta.verbose_name
        self.modelclsname_plural = restfulcls._meta.simplified._meta.model._meta.verbose_name_plural

    def get_first_para(self):
        return str(self).split('\n\n')[0].replace('\n', ' ')

    def __str__(self):
        return self.docstring.format(**self.__dict__)




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
Index page for something
===============================================================

.. toctree::
    :hidden:

    {toctree}

{items}'''
    def __init__(self, indexpageitems, ref):
        self.items = '\n\n'.join(unicode(indexpageitem) for indexpageitem in indexpageitems)
        toctreerefs = []
        for indexpageitem in indexpageitems:
            for page in indexpageitem.iterpages():
                toctreerefs.append(page.ref)
        self.toctree = '\n    '.join(toctreerefs)
        self.ref = ref

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

    def create_in_directory(self, directory, indexpageref, restfulmanager):
        indexpageitems = []
        for indexpageitem in self.iter_restfulmanager_docs(restfulmanager):
            indexpageitems.append(indexpageitem)
            self.restfulmanager_docs_to_rstfiles(directory, indexpageitem)
        indexpage = IndexPage(indexpageitems, indexpageref)
        indexpage.write(join(directory, 'index.rst'))
