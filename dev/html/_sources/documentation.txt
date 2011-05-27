.. _developer-documentation:

=======================
How to document Devilry
=======================

Devilry is documented the Sphinx_ documentation generator. You need to learn
how to write *restructured text* and how to use the Sphinx-specific
*restructured text*-directives. All of this is documented on the Sphinx_ website.

The most relevant Sphinx documentation if you are just documenting a python
module is:

* `reStructuredText Primer <http://sphinx.pocoo.org/rest.html>`_
* `Module-specific markup <http://sphinx.pocoo.org/markup/desc.html>`_
* `Include documentation from docstrings <http://sphinx.pocoo.org/ext/autodoc.html>`_
* `Notes, warnings, seealso ... <http://sphinx.pocoo.org/markup/para.html>`_
* `Cross-references <http://sphinx.pocoo.org/markup/inline.html>`_

You can find lots of examples in the `devilry sourcecode`_.
The devilry data-model file, devilry.core.models.py_, is a good example.


How documentation is organized
==============================

Documentation lives ``docs/``. Each topic is in a separate file. New files must
be added to both *toctree* and the overview in ``index.rst``.


Required software
=================

You will need a newer version of Sphinx_, at least version 1.


Building the documentation
==========================

Run *make html* while cwd is ``docs/``.


.. _Sphinx: http://sphinx.pocoo.org/
.. _devilry.core.models.py: http://github.com/devilry/devilry-django/blob/master/devilry/core/models.py
.. _`devilry sourcecode`: http://github.com/devilry/devilry-django/tree/master/devilry/
