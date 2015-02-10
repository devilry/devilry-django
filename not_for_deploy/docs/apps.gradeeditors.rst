.. _apps.gradeeditors:


==================================================
:mod:`devilry.apps.gradeeditors` --- Grade editors
==================================================


Introduction
############

To make it easy for examiners to create all the information related to a grade,
Devilry use grade editors. Grade editors give examiners a unified
user-interface tailored for different kinds of grading systems.


What they do
#############

A grade editor is essentially very simple:

    Make it easy to create a :class:`devilry.apps.core.models.StaticFeedback`.

.. _gradeeditor-howtheystore:

How they store their data --- FeedbackDraft
###########################################

Since grade editors vary greatly, but :class:`devilry.apps.core.models.StaticFeedback` only have four fields
that they can save, grade editors store their actual data in
:class:`devilry.apps.gradeeditors.models.FeedbackDraft`. A draft has a text field,
``draft``, where a grade editors can store their data.


Grade editor specific storage format
------------------------------------
The ``draft`` field uses a draft-editor specific storage format. Since this plays
well with JavaScript, all out built-in grade editors uses JSON_ to encode this
data. However, *XML* would also be a good alternative, especially for complex
data where validation would become difficult with JSON.


From FeedbackDraft to StaticFeedback
------------------------------------
:class:`devilry.apps.core.models.StaticFeedback` is, as the name suggests,
unchangable. StaticFeedback objects can only be appended to a delivery. When a
:class:`devilry.apps.gradeeditors.models.FeedbackDraft` is published, it converts 
the grade-editor specific storage format in the ``draft``-field into XHTML for
``rendered_view`` attribute of :class:`devilry.apps.core.models.StaticFeedback`.

The draft is not deleted, so the original data is still available in the
grade-editor specific storage format, while a *view* of the data is available
as a *StaticFeedback*.

**Note**: ``rendered_view`` is not validated at this point. Howver, we plan to define a
subset of XHTML at some point in the future when we have a clearer picture of
what developers are able to create using the grade editor framework.



.. _gradeeditor-creating:

Creating a grade editor
#######################

In this guide, we will walk you through the creation of
``devilry.apps.asminimalaspossible_gradeeditor``. This is available in
``devilry/apps/asminimalaspossible_gradeeditor`` in the devilry source code.


Add to registry
----------------
First of all, we need to register the grade editor with :attr:`devilry.apps.gradeeditors.registry.gradeeditor_registry`.
To make the plugin register itself when the server starts, we put the registry code in
``devilry_plugin.py`` (see :ref:`plugins`):

.. literalinclude:: /../../devilry/apps/asminimalaspossible_gradeeditor/devilry_plugin.py


devilry_plugin.AsMinimalAsPossible code explained
-------------------------------------------------
Since we use JSON as the data format in ``asminimalaspossible_gradeeditor``, we
inherit from :class:`devilry.apps.gradeeditors.registry.JsonRegistryItem`, a
sublclass of ``RegistryItem``.

We set a ``title`` and ``description`` which administrators should be able to
read to get an understanding of what the grade editor provides. Furthermore, we
define:

gradeeditorid
    A unique id for this grade editor.
config_editor_url and validate_config(...)
    See :ref:`gradeeditor-configeditor` section below.
draft_editor_url and validate_draft(...)
    See :ref:`gradeeditor-drafteditor` section below.
draft_to_staticfeedback_kwargs(...)
    Convert a draft string in our grade editor specific format into a
    :class:`devilry.apps.core.models.StaticFeedback` as explained in
    :ref:`gradeeditor-howtheystore`.


.. _gradeeditor-configeditor:

Config editor
#############

The config editor makes it possible for administrators to configure the grade
editor. A gradeeditor is not required to provide a config editor.

The config editor has three components: view, storage and validation.

The view
--------
Its view is defined as a ExtJS JavaScript file configured through the
``config_editor_url`` attribute. This view is loaded as a child component of
the ConfigEditorWindow_ widget. This widget is available through the
``this.getMainWin()`` method.

Saving a config
---------------
The main window for config editor provides provides the
``saveConfig(configstring, onFailure)`` method that should be used to save the
config. ``saveConfig(...)`` method makes a request to the server which ends up
saving the :class:`devilry.apps.gradeeditor.models.Config` as long as
:meth:`devilry.apps.gradeeditor.models.Config.clean`.

Validation
----------
:meth:`devilry.apps.gradeeditor.models.Config.clean` uses uses the
``validate_config(...)`` method in the registry item that we defined in
``devilry_plugin.py`` in :ref:`gradeeditor-creating`.

Example code
------------
.. literalinclude:: /../src/devilry/devilry/apps/asminimalaspossible_gradeeditor/static/asminimalaspossible_gradeeditor/configeditor.js
    :language: javascript


.. _gradeeditor-drafteditor:

Draft editor
############

The draft editor works almost like a config editor. The primary difference is:

- ``getMainWin()`` returns a DraftEditorWindow_.
- The draft editor uses ``draft_editor_url`` and ``validate_draft(...)``.
- Drafts are saved as :class:`devilry.apps.gradeeditor.models.FeedbackDraft`.
- Drafts are appended, not overwritten (each time you save a draft, a new
  FeedbackDraft database record is saved).
- Drafts can be published using ``getMainWin().saveDraftAndPublish(...)``. This
  results in ``draft_to_staticfeedback_kwargs(...)`` beeing used to create a
  new :class:`devilry.apps.core.models.StaticFeedback`.

Example code
------------
.. literalinclude:: /../src/devilry/devilry/apps/asminimalaspossible_gradeeditor/static/asminimalaspossible_gradeeditor/drafteditor.js
    :language: javascript



Using the RESTful API to get data grade editor data
###################################################

It is common to use the ``StaticFeedback`` API to get data from a running
Devilry instance. This is explained in the `RESTful python bindings`_ page on our wiki.

If you want to have more detailes than the data provided by the
``StaticFeedback`` RESTful API, you can fetch data from the gradeeditor APIs
directly. Their URLs are::

    /gradeeditors/administrator/restfulsimplifiedconfig
    /gradeeditors/administrator/restfulsimplifiedfeedbackdraft

However one challenge is that drafts are *personal*. This means that you will
only be able to get drafts that you have made. We will provide an API for
administrators to get **all** drafts some time in the future.


API
####################

.. currentmodule:: devilry.apps.gradeeditors.registry

.. automodule:: devilry.apps.gradeeditors.registry

.. automodule:: devilry.apps.gradeeditors.models




.. _JSON: http://en.wikipedia.org/wiki/Json
.. _ConfigEditorWindow: javascript/index.html#/api/devilry.gradeeditors.ConfigEditorWindow
.. _DraftEditorWindow: javascript/index.html#/api/devilry.gradeeditors.DraftEditorWindow
.. _`RESTful python bindings`: https://github.com/devilry/devilry-django/wiki/Official-RESTful-Python-bindings
