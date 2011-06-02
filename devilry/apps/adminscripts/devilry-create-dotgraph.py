#!/usr/bin/env python

from optparse import OptionParser

from common import (setup_logging,
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
from devilry.utils.graphviz import Graph
from devilry.utils.django_graphviz import (ModelSet, ModelsToDbDiagramDot,
        ModelsToClassDiagramDot)

def exit_help():
    p.print_help()
    raise SystemExit()
if len(args) != 1:
    exit_help()
setup_logging(opt)
outfile = args[0]

models = ModelSet('^(devilry\.|django\.contrib\.auth\.).*$')
models.add_installed_apps_models()
dotitems = ModelsToDbDiagramDot(models, show_values=True)
dotitems.add_relations()
graph = Graph(*dotitems)
#print graph
open(outfile, 'wb').write(str(graph))
