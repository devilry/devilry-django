

class RegistryItem(object):
    modelclass = None

    def to_doctype_object(self, modelobject):
        raise NotImplementedError()

    def get_all_modelobjects(self):
        raise NotImplementedError()


class Registry(object):
    def __init__(self):
        self.model_to_doc_type_map = {}

    def add(self, registryitem):
        self.model_to_doc_type_map[registryitem.modelclass] = registryitem

    def index(self, modelobject):
        registryitem = self.model_to_doc_type_map[modelobject.__class__]
        doctype_object = registryitem.to_doctype_object(
            modelobject=modelobject)
        doctype_object.save()

    def reindex_all(self):
        for registryitem in self.model_to_doc_type_map.itervalues():
            for modelobject in registryitem.get_all_modelobjects():
                self.index(modelobject)

registry = Registry()