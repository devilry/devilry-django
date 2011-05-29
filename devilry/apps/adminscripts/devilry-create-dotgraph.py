#!/usr/bin/env python

from optparse import OptionParser
import logging
import re

from common import (setup_logging, load_devilry_plugins,
    add_settings_option, set_django_settings_module, add_quiet_opt,
    add_debug_opt)


p = OptionParser(
        usage = "%prog [options] <outfile>")
add_settings_option(p)
add_quiet_opt(p)
add_debug_opt(p)
(opt, args) = p.parse_args()
setup_logging(opt)

# Django must be imported after setting DJANGO_SETTINGS_MODULE
set_django_settings_module(opt)
from django.contrib.auth.models import User
from devilry.apps.core import models

def exit_help():
    p.print_help()
    raise SystemExit()
if len(args) != 1:
    exit_help()
setup_logging(opt)

outfile = args[0]


class UmlClassLabel(object):
    def __init__(self, classname, values=[], methods=[]):
        self.classname = classname
        self.values = values
        self.methods = methods

    def __str__(self):
        label = [self.classname]
        def add(part):
            label.append('\\l'.join(part) + '\\l')
        if self.values:
            add(self.values)
        if self.methods:
            add(self.methods)
        return '"{%s}"' % '|'.join(label)


class Edge(object):
    def __init__(self, headlabel="", taillabel="", arrowhead='none'):
        self.headlabel = headlabel
        self.taillabel = taillabel
        self.arrowhead = arrowhead

    def __str__(self):
        return ('edge[arrowhead="%(arrowhead)s", '
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
    fontname = "Bitstream Vera Sans"
    fontsize = 8

    node [
        fontname = "Bitstream Vera Sans"
        fontsize = 8
        shape = "record"
    ]

    edge [
        fontname = "Bitstream Vera Sans"
        fontsize = 8
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

def model_to_dot(modelcls, show_fields=False):
    meta = modelcls._meta
    id = model_to_id(modelcls)
    values = []
    if show_fields:
        values = ['+ %s' % f for f in meta.get_all_field_names()]
    label = UmlClassLabel(id, values=values)
    return Node(id, label)



print dir(models.Node)
print dir(models.Node._meta)
print
print models.Node._meta.db_table
print models.Node._meta.get_all_field_names()
meta = models.Node._meta
print meta.get_all_related_many_to_many_objects()
print meta.get_all_related_objects()
subrel = meta.get_all_related_objects()[1]
print dir(subrel)
print subrel.model, subrel.name
print

#print User._meta.get_all_related_many_to_many_objects()

def model_to_associations(model, models):
    associations = []
    for rel in model._meta.get_all_related_objects():
        assoc = Association(model_to_id(model),
                model_to_id(rel.model), Edge('1', '*'))
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
    print associations
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
    recurse(model)
    return models


modelkw = dict(show_fields=True)
node = model_to_dot(models.Node, **modelkw)
subject = model_to_dot(models.Subject, **modelkw)
period = model_to_dot(models.Period, **modelkw)
assignment = model_to_dot(models.Assignment, **modelkw)
assignmentgroup = model_to_dot(models.AssignmentGroup, **modelkw)
delivery = model_to_dot(models.Delivery, **modelkw)
deadline = model_to_dot(models.Deadline, **modelkw)

#models = models_to_dot([models.Node, models.Subject, models.Period,
    #models.Assignment, models.AssignmentGroup, models.Delivery,
    #models.Deadline])

#graph = Graph(*models
        #node, subject, period, assignment, assignmentgroup,
        #delivery, deadline,
        #Association(node, node, Edge('1', '*')),
        #Association(node, subject, Edge('1', '*')),
        #Association(subject, period, Edge('1', '*')),
        #Association(period, assignment, Edge('1', '*')),
        #Association(assignment, assignmentgroup, Edge('1', '*')),
        #Association(assignmentgroup, delivery, Edge('1', '*')),
        #Association(assignmentgroup, deadline, Edge('1', '*')),
        #Association(, , Edge('1', '*')))

devilry_models = recursive_get_models(models.Node, "^core_.*|grade.*$")
graph = Graph(*models_to_dot(devilry_models, show_fields=True))
print graph
open(outfile, 'wb').write(str(graph))
