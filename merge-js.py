from os import walk
from os.path import join, dirname
import re
import sys
import logging


logging.basicConfig(level=logging.INFO)


ignorefilepatt = re.compile('^.*?(configeditor.js|drafteditor.js|formatoverrides.js)$')
ignoredirpatt = re.compile('(deliverystore|extjshelpers.extjs)')

class JsFile(object):
    DEFINEPATT = re.compile(r"^Ext\.define\(.(.+?).\s*,", re.MULTILINE)
    EXTENDPATT = re.compile(r"^\s*extend\s*:\s*['\"](.+?)['\"]", re.MULTILINE|re.DOTALL)
    REQUIRESPATT = re.compile(r"^\s*requires\s*:\s*\[(.*?)\]", re.MULTILINE|re.DOTALL)
    MIXINSPATT = re.compile(r"^\s*mixins\s*:\s*{(.*?)}", re.MULTILINE|re.DOTALL)
    LISTSPLITPATT = re.compile(r'[\'"](.*?)[\'"]')

    def __init__(self, filepath):
        self.filecontent = open(filepath, 'rb').read()
        self.match_define()
        self.match_requires() # must be before extend and mixins, since they add to self.requires
        self.match_extend()
        self.match_mixins()
        self.requires = filter(lambda r: not r.startswith('Ext.'), self.requires)

    def match_define(self):
        m = self.DEFINEPATT.search(self.filecontent)
        if m:
            self.clsname = m.groups()[0]
        else:
            raise ValueError('{0}: no Ext.define(....) found.'.format(filepath))

    def match_requires(self):
        m = self.REQUIRESPATT.search(self.filecontent)
        if m:
            requiresstr = m.groups()[0]
            self.requires = self.LISTSPLITPATT.findall(requiresstr)
        else:
            self.requires = []

    def match_extend(self):
        m = self.EXTENDPATT.search(self.filecontent)
        if m:
            self.extend = m.groups()[0]
            self.requires.append(self.extend)
        else:
            self.extend = None

    def match_mixins(self):
        m = self.MIXINSPATT.search(self.filecontent)
        if m:
            mixinsstr = m.groups()[0]
            self.mixins = self.LISTSPLITPATT.findall(mixinsstr)
            self.requires += self.mixins
        else:
            self.mixins = []

    def __str__(self):
        return "{0}: {1} ({2})".format(self.clsname, self.extend, ','.join(self.requires))


def depsfullfilled(jsfile, jsfiles):
    for req in jsfile.requires:
        if req in jsfiles:
            return False
    return True

def orderJsFiles(jsfiles):
    ordered = []
    while jsfiles:
        for clsname in jsfiles.keys():
            jsfile = jsfiles[clsname]
            if depsfullfilled(jsfile, jsfiles):
                ordered.append(jsfile)
                del jsfiles[clsname]
    return ordered


jsfiles = {}
for root, dirs, files in walk(join(dirname(__file__), 'devilry', 'apps')):
    if ignoredirpatt.search(root):
        continue
    for filename in files:
        if filename.endswith('.js'):
            filepath = join(root, filename)
            if not ignorefilepatt.match(filename):
                try:
                    jsfile = JsFile(filepath)
                except ValueError, e:
                    logging.info(str(e))
                else:
                    jsfiles[jsfile.clsname] = jsfile


ordered = orderJsFiles(jsfiles)
#for j in ordered:
    #print j
open(sys.argv[1], 'wb').write('\n\n'.join([j.filecontent for j in ordered]))
