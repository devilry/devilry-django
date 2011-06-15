#!/usr/bin/env python
from os.path import join
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'devilry.projects.dev.settings'
from devilry.utils.graphviz.dot import Graph
from devilry.utils.graphviz.sphinx import sphinx_format
from devilry.utils.graphviz.djangomodels import (ModelSet, ModelsToDbDiagramDot)


def create_graph(name, modelpatt, show_values=True):
    allmodels = ModelSet(modelpatt)
    allmodels.add_installed_apps_models()

    dotitems = ModelsToDbDiagramDot(allmodels, show_values=show_values)
    dotitems.add_relations()
    graph = Graph(*dotitems)
    outfile = join('dotgraphs', '%s.dot.rst' % name)
    open(outfile, 'wb').write(sphinx_format(str(graph)))

create_graph('all', '^(devilry\.|django\.contrib\.auth\.).*$')
