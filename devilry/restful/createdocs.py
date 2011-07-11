"""
Autogenerate documentation RESTful APIs
"""
from os.path import join

from devilry.simplified import SimplifiedModelApi



CRUD_TO_HTTP = {'create': ('POST', False),
                'read': ('GET', True),
                'update': ('PUT', True),
                'delete': ('DELETE', True),
                'search': ('GET', False)}


class Page(object):
    TPL = '''.. _{refid}:

{httpmethod} {url}
##########################################################################

{docs}'''
    def __init__(self, refprefix, methodname, httpmethod, url, docs):
        self.refprefix = refprefix
        self.httpmethod = httpmethod
        self.url = url
        self.docs = docs
        self.refid = '{0}_details_{1}'.format(refprefix, methodname) # id usable by rst :ref:
        self.filename = '{0}.rst'.format(self.refid)

    def __unicode__(self):
        return self.TPL.format(**self.__dict__)

    def get_filepath(self, directory):
        return join(directory, self.filename)


class IndexItem(object):
    TPL = '{httpmethod} {url}\n    {first_para}'
    def __init__(self, refprefix, methodname, httpmethod, url, docs):
        self.httpmethod = httpmethod
        self.url = url
        self.first_para = docs.split('\n\n')[0]
        self.page = Page(refprefix, methodname, httpmethod, url, docs)

    def __unicode__(self):
        return self.TPL.format(**self.__dict__)


class IndexPage(object):
    TPL = '''

{simplifiedclsname}
###############################################################################

{indexitems}'''
    def __init__(self, restfulcls, indexitems):
        self.restfulcls = restfulcls
        self.simplifiedclsname = self.restfulcls._meta.simplified.__name__
        self.indexitems = indexitems

    def __unicode__(self):
        return self.TPL.format(simplifiedclsname=self.simplifiedclsname,
                               indexitems='\n'.join(unicode(i) for i in self.indexitems))

    def iterpages(self):
        for indexitem in self.indexitems:
            yield indexitem.page


class RestfulDocs(object):
    def iter_restfulcls_docs(self, restfulcls):
        for methodname in restfulcls._meta.simplified._meta.methods:
            if methodname.startswith('insecure_'):
                continue
            method = getattr(SimplifiedModelApi, methodname)
            docs = method.__doc__
            yield methodname, docs

    def _get_restfulcls_docprefix(self, restfulcls):
        appname = restfulcls.__module__.split('.')[-2] # Assume restful is in appdir.restful
        return '{0}_{1}'.format(appname, restfulcls.__name__.lower())

    def iter_restfulmanager_docs(self, restfulmanager):
        for restfulcls in restfulmanager.iter_restfulclasses():
            refprefix = self._get_restfulcls_docprefix(restfulcls)
            url = restfulcls.get_rest_url()
            indexitems = []
            for methodname, docs in self.iter_restfulcls_docs(restfulcls):
                httpmethod, hasid = CRUD_TO_HTTP[methodname]
                if hasid:
                    itemurl = '{0}**id**'.format(url)
                else:
                    itemurl = url
                indexitems.append(IndexItem(refprefix, methodname, httpmethod, itemurl, docs))
            yield IndexPage(restfulcls, indexitems)

    def restfulmanager_docs_to_rst(self, directory, indexpage):
        for page in indexpage.iterpages():
            open(page.get_filepath(directory), 'wb').write(unicode(page).encode('utf-8'))

    def create_in_directory(self, directory, restfulmanager):
        indexpages = []
        for indexpage in self.iter_restfulmanager_docs(restfulmanager):
            indexpages.append(indexpage)
            self.restfulmanager_docs_to_rst(directory, indexpage)
        indexpagedocs = '\n\n'.join(unicode(p) for p in indexpages)
        open(join(directory, 'index.rst'), 'wb').write(unicode(indexpagedocs).encode('utf-8'))


if __name__ == "__main__":
    from os.path import exists
    from os import mkdir
    from shutil import rmtree
    from devilry.apps.administrator.restful import administrator_restful

    directory = 'restfulapidocs'
    if exists(directory):
        #raise SystemExit('{0} exists. Delete it before running this script.')
        rmtree(directory)
    mkdir(directory)

    RestfulDocs().create_in_directory(directory, administrator_restful)
