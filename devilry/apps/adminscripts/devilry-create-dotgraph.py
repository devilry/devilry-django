#!/usr/bin/env python

from optparse import OptionParser
from sys import argv

from common import (setup_logging,
    add_settings_option, set_django_settings_module, add_quiet_opt,
    add_debug_opt)

class CustOptParser(OptionParser):
    def format_epilog(self, formatter):
        return self.epilog


help_epilog = """
Examples
--------

Create PDF class diagram:
   %(prog)s --cls -o cls.dot && dot -Tpng -o cls.png cls.dot

Create PDF database diagram with all details:
   %(prog)s --show-fields -o db.dot && dot -Tpdf -o db.pdf db.dot

Create PNG class diagram with all details:
   %(prog)s --cls --show-fields -o cls.dot && dot -Tpng -o cls.png cls.dot
""" % dict(prog=argv[0])


default_filter = '^(devilry\.apps\.core\.models\.|django\.contrib\.auth\.models\.User).*$'
p = CustOptParser(
        usage = "%prog [options] <outfile>",
        epilog = help_epilog)
add_settings_option(p)
add_quiet_opt(p)
add_debug_opt(p)
p.add_option("--sphinx-format", dest="sphinx_format",
        default=False, action='store_const', const=True,
        help="Format for sphinx.")
p.add_option("--cls", dest="classdiagram",
        default=False, action='store_const', const=True,
        help="Create class diagram. Default is database diagram.")
p.add_option("--show-fields", dest="show_fields",
        default=False, action='store_const', const=True,
        help="Show fields.")
p.add_option('-o', "--out-file", dest="outfile",
        default=None,
        help='Output file. Defaults to printing to standard output.')
p.add_option("--filter", dest="filter",
        default=default_filter,
        help='Filter the used models using a regex. Default: "%s"' % default_filter)

(opt, args) = p.parse_args()
setup_logging(opt)

# Django must be imported after setting DJANGO_SETTINGS_MODULE
set_django_settings_module(opt)
from devilry.utils.graphviz.dot import Graph
from devilry.utils.graphviz.sphinx import sphinx_format
from devilry.utils.graphviz.djangomodels import (ModelSet,
        ModelsToDbDiagramDot, ModelsToClassDiagramDot)

def exit_help():
    p.print_help()
    raise SystemExit()
setup_logging(opt)

models = ModelSet(opt.filter)
models.add_installed_apps_models()

if opt.classdiagram:
    dotitems = ModelsToClassDiagramDot(models, show_values=opt.show_fields)
else:
    dotitems = ModelsToDbDiagramDot(models, show_values=opt.show_fields)
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
