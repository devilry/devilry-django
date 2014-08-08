#!/usr/bin/env python
# Create graphviz (dot) compatible graphs from django models.

from optparse import OptionParser
from common import getprogname


class CustOptParser(OptionParser):
    def format_epilog(self, formatter):
        return self.epilog


help_epilog = """
Examples
--------

Create PDF class diagram:
   {prog} --cls -o cls.dot && dot -Tpng -o cls.png cls.dot

Create PDF database diagram with all details:
   {prog} --show-fields -o db.dot && dot -Tpdf -o db.pdf db.dot

Create PNG class diagram with all details:
   {prog} --cls --show-fields -o cls.dot && dot -Tpng -o cls.png cls.dot

Create PNG and choose maximum size:
    {prog} -o db.dot --height 2000 --width 550 && dot -Tpng -o db.png db.dot
""".format(prog=getprogname())


default_filter = '^(devilry\.apps\.core\.models\.|django\.contrib\.auth\.models\.User).*$'
p = CustOptParser(
        usage = "%prog [options] <outfile>",
        prog = getprogname(),
        epilog = help_epilog)
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
        help='Filter the used models using a regex. Default: "{0}"'.format(default_filter))
p.add_option("--width", dest="width",
        default=None, type='int',
        help='Output width in pixels. Only used when --height is supplied.')
p.add_option("--height", dest="height",
        default=None, type='int',
        help='Output height in pixels. Only used when --width is supplied.')

(opt, args) = p.parse_args()

# Django must be imported after setting DJANGO_SETTINGS_MODULE
from devilry.utils.graphviz.dot import Graph
from devilry.utils.graphviz.sphinx import sphinx_format
from devilry.utils.graphviz.djangomodels import (ModelSet,
        ModelsToDbDiagramDot, ModelsToClassDiagramDot)

def exit_help():
    p.print_help()
    raise SystemExit()

models = ModelSet(opt.filter)
models.add_installed_apps_models()

if opt.classdiagram:
    dotitems = ModelsToClassDiagramDot(models, show_values=opt.show_fields)
else:
    dotitems = ModelsToDbDiagramDot(models, show_values=opt.show_fields)
dotitems.add_relations()

if opt.height and opt.width:
    graph = Graph(dotitems, opt.height, opt.width)
else:
    graph = Graph(dotitems)

dotcode = str(graph)
if opt.sphinx_format:
    dotcode = sphinx_format(dotcode)
#print graph

if opt.outfile:
    open(opt.outfile, 'wb').write(dotcode)
else:
    print dotcode
