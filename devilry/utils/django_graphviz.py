from inspect import getmodule
import re

from django.utils.importlib import import_module
from django.db.models import fields
from django.db.models.base import ModelBase

from graphviz import UmlClassLabel, Association, Node, Edge, UmlField



def fieldnames_to_labels(model):
    fieldnames = []
    for fn in model._meta.get_all_field_names():
        field = model._meta.get_field_by_name(fn)[0]
        if isinstance(field, fields.related.ManyToManyField):
            pass
        elif isinstance(field, fields.related.RelatedObject):
            pass
        else:
            fieldnames.append(UmlField(fn))
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
            node = self.model_to_dotnode(model)
            self.append(node)

    def model_to_dotnode(self, model):
        meta = model._meta
        id = self.get_dotid(model)
        values = []
        if self.show_values:
            values = fieldnames_to_labels(model)
        label = UmlClassLabel(self.get_title(model), values=values)
        return Node(id, label)

    def add_onetomany_association(self, model, related_obj):
        if not related_obj.model in self.models:
            return
        assoc = Association(self.get_dotid(model),
                self.get_dotid(related_obj.model), Edge('1', '*'))
        self.append(assoc)

    def add_manytomany_association(self, model, related_obj):
        #label = related_obj.var_name
        if not related_obj.model in self.models:
            return
        assoc = Association(self.get_dotid(model),
                self.get_dotid(related_obj.model), Edge('*', '*'))
        self.append(assoc)

    def add_association(self, model):
        for related_obj in model._meta.get_all_related_objects():
            self.add_onetomany_association(model, related_obj)
        for related_obj in model._meta.get_all_related_many_to_many_objects():
            self.add_manytomany_association(model, related_obj)

    def add_associations(self):
        for model in self.models:
            self.add_association(model)

    def get_title(self, model):
        return self.get_id(model)


class ModelsToDbDot(ModelsToDot):
    def get_title(self, model):
        return model._meta.db_table

    def manytomany_to_dotnode(self, field, id):
        values = []
        if self.show_values:
            values = [
                    UmlField(field.m2m_column_name()),
                    UmlField(field.m2m_reverse_name())]
        label = UmlClassLabel(field.m2m_db_table(), values=values)
        return Node(id, label)

    def add_manytomany_association(self, model, related_obj):
        if not related_obj.model in self.models:
            return
        """ Example from the relation to core.models.Node from User:
                           m2m_column_name: node_id
                              m2m_db_table: core_node_admins
                            m2m_field_name: node
                    m2m_reverse_field_name: user
                          m2m_reverse_name: user_id
             m2m_reverse_target_field_name: id
                     m2m_target_field_name: id

        (see also: python manage.py sqlall core)
        """
        field = related_obj.field
        table_name = field.m2m_db_table()
        node = self.manytomany_to_dotnode(field, table_name)
        self.append(node)
        #node = self.model_to_dotnode(model)
        assoc = Association(self.get_dotid(model),
                table_name, Edge('1', '*'))
        assoc = Association(table_name,
                self.get_dotid(related_obj.model), Edge('1', '*'))
        self.append(assoc)



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
