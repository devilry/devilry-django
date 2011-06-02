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
p.add_option("--minimal", dest="show_values",
        default=True, action='store_const', const=False,
        help="Only show titles, no fields.")
p.add_option("--sphinx-format", dest="sphinx_format",
        default=False, action='store_const', const=True,
        help="Format for sphinx.")
p.add_option('-o', "--out-file", dest="outfile",
        default=None,
        help='Output file. Defaults to printing to standard output.')
(opt, args) = p.parse_args()
setup_logging(opt)

# Django must be imported after setting DJANGO_SETTINGS_MODULE
set_django_settings_module(opt)
from devilry.utils.graphviz.dot import Graph
from devilry.utils.graphviz.sphinx import sphinx_format
from devilry.utils.graphviz.djangomodels import (ModelSet, ModelsToDbDiagramDot)

def exit_help():
    p.print_help()
    raise SystemExit()
setup_logging(opt)

models = ModelSet('^(devilry\.|django\.contrib\.auth\.).*$')
models.add_installed_apps_models()
dotitems = ModelsToDbDiagramDot(models, show_values=opt.show_values)
#dotitems = ModelsToClassDiagramDot(models, show_values=True)
dotitems.add_relations()
graph = Graph(*dotitems)

dotcode = str(graph)
if opt.sphinx_format:
    dotcode = sphinx_format(dotcode)
#print graph

if opt.outfile:
    open(opt.outfile, 'wb').write(dotcode)
else:
    print dotcode
