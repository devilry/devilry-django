class UmlField(list):
    def __init__(self, name, fieldtype='', visibility='+'):
        self.name = name
        self.fieldtype = fieldtype
        self.visibility = visibility
    def __str__(self):
        return '%(visibility)s %(name)s: %(fieldtype)s' % self.__dict__


class UmlClassLabel(object):
    table_tpl = '<\n<TABLE BORDER="0" CELLBORDER="1" CELLPADDING="6" '\
            'CELLSPACING="0">\n%s</TABLE>>'
    headrow_tpl = '  <TR><TD bgcolor="#222222" align="CENTER">'\
        '<FONT COLOR="#ffffff" point-size="12">%s</FONT></TD></TR>\n'
    partrow_tpl = '  <TR><TD bgcolor="#ffffff" balign="LEFT" align="LEFT">%s</TD></TR>\n'
    def __init__(self, title, values=[], methods=[]):
        self.title = title
        self.values = values
        self.methods = methods

    def __str__(self):
        label = [self.headrow_tpl % self.title]
        def add(part):
            label.append(self.partrow_tpl % '<BR/>\n'.join(
                [str(x) for x in part]))
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


def pixels_to_inches(px, dpi=75):
    return px / float(dpi)


class Graph(object):
    tpl = """
%(graphtype)s G {
    fontname = "Lucida Grande"
    fontsize = 10
    %(size)s

    node [
        fontname = "Lucida Grande"
        fontsize = 10
        shape = "none"
    ]

    edge [
        fontname = "Lucida Grande"
        fontsize = 10
    ]

    %(items)s
}"""
    def __init__(self, items, width=None, height=None):
        self.set_directed()
        self.items = list(items)
        self.size = ''
        if width:
            w = pixels_to_inches(width)
            h = pixels_to_inches(height)
            self.size = 'size = "%.3f,%.3f"' % (w, h)

    def __str__(self):
        return self.tpl % dict(
                size = self.size,
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
