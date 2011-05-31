from inspect import getmodule
import re

from django.utils.importlib import import_module
from django.db.models import fields
from django.db.models.base import ModelBase

from graphviz import UmlClassLabel, Association, Node, Edge


def fieldnames_to_labels(model):
    fieldnames = []
    for fn in model._meta.get_all_field_names():
        field = model._meta.get_field_by_name(fn)[0]
        #print fn, field, type(field)
        if isinstance(field, fields.related.ManyToManyField):
            #print fn, field
            pass
        elif isinstance(field, fields.related.RelatedObject):
            pass
        else:
            #print fn, field
            fieldnames.append('+ %s' % fn)
    return fieldnames


class GetIdMixin(object):
    def get_id(self, model):
        return '%s.%s' % (getmodule(model).__name__, model.__name__)

    def get_dotid(self, model):
        return self.get_id(model).replace('.', '_')


class ModelsToDot(list, GetIdMixin):
    def __init__(self, models, show_values=False):
        self.models = models
        self.show_values = show_values

        for model in models:
            node = self.model_to_dot(model)
            self.append(node)

    def add_associations(self):
        for model in self.models:
            self.add_association(model)

    def model_to_dot(self, model):
        meta = model._meta
        id = self.get_dotid(model)
        values = []
        if self.show_values:
            values = fieldnames_to_labels(model)
        label = UmlClassLabel(self.get_title(model), values=values)
        return Node(id, label)

    def add_association(self, model):
        for rel in model._meta.get_all_related_objects():
            #label = rel.var_name
            if rel.model in self.models:
                assoc = Association(self.get_dotid(model),
                        self.get_dotid(rel.model), Edge('1', '*'))
                self.append(assoc)
        for rel in model._meta.get_all_related_many_to_many_objects():
            label = rel.var_name
            #print label, dir(rel)
            if rel.model in self.models:
                #print model, dir(model._meta)
                assoc = Association(self.get_dotid(model),
                        self.get_dotid(rel.model), Edge('*', '*'))
                self.append(assoc)

    def get_title(self, model):
        return self.get_id(model)


class ModelsToDbDot(ModelsToDot):
    def get_title(self, model):
        return model._meta.db_table



class Models(set, GetIdMixin):
    def __init__(self, pattern, *models):
        super(Models, self).__init__(*models)
        self.patt = re.compile(pattern)

    def recursive_add_models(self, model):
        def recurse(curmodel):
            if curmodel in self:
                return
            self.add(curmodel)
            for rel in curmodel._meta.get_all_related_objects():
                if rel.model != curmodel:
                    recurse(rel.model)
            for rel in curmodel._meta.get_all_related_many_to_many_objects():
                if rel.model != curmodel:
                    recurse(rel.model)
        recurse(model)

    def add_installed_apps_models(self):
        from django.conf import settings

        for app in settings.INSTALLED_APPS:
            try:
                mod = import_module("%s.models" % app)
            except ImportError, e:
                continue
            for name in dir(mod):
                var = getattr(mod, name)
                if isinstance(var, ModelBase):
                    self.recursive_add_models(var)

    def add(self, model):
        if self.patt.match(self.get_id(model)):
            super(Models, self).add(model)


if __name__ == '__main__':
    models = Models('^(devilry|django\.contrib\.auth)\..*$')
    models.add_installed_apps_models()
    print models
