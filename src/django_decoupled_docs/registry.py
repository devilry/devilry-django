from django.conf import settings



class DocProxy(object):
    def __init__(self, **languages):
        self.urls = {}
        self.addmany(**languages)

    def addmany(self, **languages):
        for languagecode, url in languages.iteritems():
            self.add_for_language(languagecode, url)

    def add_for_language(self, languagecode, url):
        self.urls[languagecode] = url

    def __getitem__(self, languagecode):
        return self.urls[languagecode]



class VersionedReadTheDocsDocProxyBase(DocProxy):
    #: The name of the project (the first path of the URL). Must be difined in subclasses.
    projectname = None

    def add_for_language(self, languagecode, path):
        url = 'http://{projectname}.readthedocs.org/{languagecode}/{version}/{path}'.format(
            projectname=self.projectname,
            languagecode=languagecode,
            version=self.get_current_version(),
            path=path)
        super(VersionedReadTheDocsDocProxyBase, self).add_for_language(languagecode, url)

    def get_current_version(self):
        return 'latest'



class DocumentationRegistry(object):
    def __init__(self):
        self._defaults = {}
        self._overrides = {}

    def _get_document(self, registrydict, documentid, languagecode):
        proxy = registrydict[documentid]
        return proxy[languagecode]

    def get(self, documentid, languagecode):
        documenturl = None
        default_languagecode = getattr(settings, 'DJANGO_DECOUPLED_DOCS_DEFAULT_LANGUAGECODE', 'en')
        for lang in (languagecode, default_languagecode):
            try:
                documenturl = self._get_document(self._overrides, documentid, lang)
            except KeyError:
                try:
                    documenturl = self._get_document(self._defaults, documentid, lang)
                except KeyError:
                    pass
        return documenturl

    def add(self, documentid, proxy):
        self._defaults[documentid] = proxy

    def override(self, documentid, proxy):
        self._overrides[documentid] = proxy


documentationregistry = DocumentationRegistry()