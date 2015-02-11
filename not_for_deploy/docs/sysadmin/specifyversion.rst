.. _specifyversion:

========================
How to specify a version
========================

The version of Devilry is defined by the base-template that you extend in your ``buildout.cfg``::

    [buildout]
    extends = https://raw.github.com/devilry/devilry-deploy/REVISION/buildout/buildout-base.cfg

This base-template is fetched from the ``devilry-deploy``-repository, and the
``REVISION`` is a git tag, branch or CommitID from that repo (NOT from the
devilry repo). We keep tags in sync with stables releases of Devilry, so if you
specify a tag from ``devilry-deploy`` (E.g.: ``1.2.1``), the
``buildout-base.cfg`` will be configured to use that version of Devilry.
