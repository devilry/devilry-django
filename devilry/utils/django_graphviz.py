from inspect import getmodule
import re

from django.utils.importlib import import_module
from django.db.models import fields
from django.db.models.base import ModelBase

from graphviz import UmlClassLabel, Association, Node, Edge


def model_to_id(model):
    return model._meta.db_table

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

def model_to_dot(modelcls, show_fields=False):
    meta = modelcls._meta
    id = model_to_id(modelcls)
    values = []
    if show_fields:
        values = fieldnames_to_labels(modelcls)
    label = UmlClassLabel(id, values=values)
    return Node(id, label)


def model_to_associations(model, models):
    associations = []
    for rel in model._meta.get_all_related_objects():
        #label = rel.var_name
        if rel.model in models:
            assoc = Association(model_to_id(model),
                    model_to_id(rel.model), Edge('1', '*'))
            associations.append(assoc)
    for rel in model._meta.get_all_related_many_to_many_objects():
        #label = rel.var_name
        if rel.model in models:
            assoc = Association(model_to_id(model),
                    model_to_id(rel.model), Edge('*', '*'))
            associations.append(assoc)
    return associations


def models_to_dot(models, show_fields=False):
    nodes = []
    nodesdct = {}
    associations = []
    for model in models:
        node = model_to_dot(model, show_fields)
        nodes.append(node)
        associations.extend(model_to_associations(model, models))
    return nodes + associations


class Models(set):
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

    def get_id(self, model):
        return '%s.%s' % (getmodule(model).__name__, model.__name__)

    def add(self, model):
        if self.patt.match(self.get_id(model)):
            super(Models, self).add(model)


if __name__ == '__main__':
    models = Models('^(devilry|django\.contrib\.auth)\..*$')
    models.add_installed_apps_models()
    print models
