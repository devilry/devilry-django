import re
from django.db.models import fields


class UmlClassLabel(object):
    table_tpl = '<\n<TABLE BORDER="0" CELLBORDER="1" CELLPADDING="6" '\
            'CELLSPACING="0">\n%s</TABLE>>'
    headrow_tpl = '  <TR><TD bgcolor="#669933" align="CENTER">'\
        '<FONT COLOR="#ffffff" point-size="12">%s</FONT></TD></TR>\n'
    partrow_tpl = '  <TR><TD bgcolor="#ffffff" balign="LEFT" align="LEFT">%s</TD></TR>\n'
    def __init__(self, classname, values=[], methods=[]):
        self.classname = classname
        self.values = values
        self.methods = methods

    def __str2__(self):
        label = [self.classname]
        def add(part):
            label.append('\\l'.join(part) + '\\l')
        if self.values:
            add(self.values)
        if self.methods:
            add(self.methods)
        return '"{%s}"' % '|'.join(label)

    def __str__(self):
        label = [self.headrow_tpl % self.classname]
        def add(part):
            label.append(self.partrow_tpl % '<BR/>\n'.join(part))
        if self.values:
            add(self.values)
        if self.methods:
            add(self.methods)
        return self.table_tpl % '\n'.join(label)


class Edge(object):
    def __init__(self, taillabel="", headlabel="", label='',
            arrowhead='none', color='#777777'):
        self.headlabel = headlabel
        self.taillabel = taillabel
        self.label = label
        self.arrowhead = arrowhead
        self.color = color

    def __str__(self):
        return ('edge[arrowhead="%(arrowhead)s", '
                'color="%(color)s", '
                'label="%(label)s", '
                'headlabel="%(headlabel)s", '
                'taillabel="%(taillabel)s"]') % self.__dict__

class Association(object):
    def __init__(self, a, b, edge):
        self.a = a
        self.b = b
        self.edge = edge

    def tostring(self, edgeop):
        edge = self.edge
        a = self.a
        b = self.b
        return '%(edge)s\n    %(a)s %(edgeop)s %(b)s' % vars()

class Node(object):
    def __init__(self, id, label):
        if id.lower() in ('node', 'edge', 'graph', 'digraph', 'subgraph'):
            self.id = '_' + id
        else:
            self.id = id
        self.label = label
    def __str__(self):
        return '%(id)s [label=%(label)s]' % self.__dict__


class Graph(object):
    tpl = """
%(graphtype)s G {
    fontname = "Lucida Grande"
    fontsize = 10

    node [
        fontname = "Lucida Grande"
        fontsize = 10
        shape = "plaintext"
    ]

    edge [
        fontname = "Lucida Grande"
        fontsize = 10
    ]

    %(items)s
}"""
    def __init__(self, *items):
        self.set_directed()
        self.items = list(items)

    def __str__(self):
        return self.tpl % dict(
                graphtype = self.graphtype,
                items = '\n\n    '.join(self.stritems()))

    def stritems(self):
        def formatitem(item):
            if isinstance(item, Association):
                return item.tostring(self.edgeop)
            else:
                return str(item)
        return [formatitem(i) for i in self.items]

    def set_directed(self):
        self.graphtype = 'digraph'
        self.edgeop = '->'
    #def set_undirected(self):
        #self.graphtype = 'raph'
        #self.edgeop = '--'

    def append(self, item):
        self.items.append(item)

    def extend(self, items):
        self.items.extend(items)


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

def recursive_get_models(model, pattern="*"):
    models = []
    searched = set()
    def recurse(curmodel):
        if curmodel in searched:
            return
        id = model_to_id(curmodel)
        if not re.match(pattern, id):
            return
        models.append(curmodel)
        searched.add(curmodel)
        for rel in curmodel._meta.get_all_related_objects():
            recurse(rel.model)
        for rel in curmodel._meta.get_all_related_many_to_many_objects():
            recurse(rel.model)
    recurse(model)
    return models
