Ext.data.JsonP.devilry_gradeeditors_DraftEditorWindow({
  "mixedInto": [

  ],
  "href": "DraftEditorWindow.html#devilry-gradeeditors-DraftEditorWindow",
  "allMixins": [

  ],
  "doc": "<p>Draft editor window.</p>\n",
  "singleton": false,
  "html_filename": "DraftEditorWindow.html",
  "code_type": "ext_define",
  "subclasses": [

  ],
  "superclasses": [

  ],
  "protected": false,
  "tagname": "class",
  "mixins": [

  ],
  "members": {
    "cfg": [
      {
        "type": "Object",
        "href": "DraftEditorWindow.html#devilry-gradeeditors-DraftEditorWindow-cfg-deliveryid",
        "owner": "devilry.gradeeditors.DraftEditorWindow",
        "doc": "<p>ID of the Delivery where the feedback belongs. (Required).</p>\n",
        "html_filename": "DraftEditorWindow.html",
        "protected": false,
        "tagname": "cfg",
        "static": false,
        "private": false,
        "inheritable": false,
        "alias": null,
        "name": "deliveryid",
        "shortDoc": "ID of the Delivery where the feedback belongs. ...",
        "linenr": 21,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/gradeeditors/static/extjs_classes/gradeeditors/DraftEditorWindow.js",
        "deprecated": null
      },
      {
        "type": "Object",
        "href": "DraftEditorWindow.html#devilry-gradeeditors-DraftEditorWindow-cfg-gradeeditor_config",
        "owner": "devilry.gradeeditors.DraftEditorWindow",
        "doc": "<p>The data attribute of the record returned when loading the\ngrade-editor config. (Required).</p>\n",
        "html_filename": "DraftEditorWindow.html",
        "protected": false,
        "tagname": "cfg",
        "static": false,
        "private": false,
        "inheritable": false,
        "alias": null,
        "name": "gradeeditor_config",
        "shortDoc": "The data attribute of the record returned when loading the\ngrade-editor config. ...",
        "linenr": 34,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/gradeeditors/static/extjs_classes/gradeeditors/DraftEditorWindow.js",
        "deprecated": null
      },
      {
        "type": "Boolean",
        "href": "DraftEditorWindow.html#devilry-gradeeditors-DraftEditorWindow-cfg-isAdministrator",
        "owner": "devilry.gradeeditors.DraftEditorWindow",
        "doc": "<p>Use the administrator RESTful interface to store drafts? If this is\n<code>false</code>, we use the examiner RESTful interface.</p>\n",
        "html_filename": "DraftEditorWindow.html",
        "protected": false,
        "tagname": "cfg",
        "static": false,
        "private": false,
        "inheritable": false,
        "alias": null,
        "name": "isAdministrator",
        "linenr": 27,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/gradeeditors/static/extjs_classes/gradeeditors/DraftEditorWindow.js",
        "deprecated": null
      },
      {
        "type": "Object",
        "href": "DraftEditorWindow.html#devilry-gradeeditors-DraftEditorWindow-cfg-registryitem",
        "owner": "devilry.gradeeditors.DraftEditorWindow",
        "doc": "<p>The data attribute of the record returned when loading the\ngrade-editor registry item. (Required).</p>\n",
        "html_filename": "DraftEditorWindow.html",
        "protected": false,
        "tagname": "cfg",
        "static": false,
        "private": false,
        "inheritable": false,
        "alias": null,
        "name": "registryitem",
        "shortDoc": "The data attribute of the record returned when loading the\ngrade-editor registry item. ...",
        "linenr": 41,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/gradeeditors/static/extjs_classes/gradeeditors/DraftEditorWindow.js",
        "deprecated": null
      }
    ],
    "event": [

    ],
    "property": [

    ],
    "method": [
      {
        "href": "DraftEditorWindow.html#devilry-gradeeditors-DraftEditorWindow-method-getGradeEditorConfig",
        "owner": "devilry.gradeeditors.DraftEditorWindow",
        "params": [

        ],
        "doc": "<p>Get the grade editor configuration that is stored on the current\nassignment.</p>\n",
        "html_filename": "DraftEditorWindow.html",
        "protected": false,
        "tagname": "method",
        "static": false,
        "return": {
          "type": "void",
          "doc": "\n"
        },
        "private": false,
        "inheritable": false,
        "alias": null,
        "name": "getGradeEditorConfig",
        "shortDoc": "Get the grade editor configuration that is stored on the current\nassignment. ...",
        "linenr": 381,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/gradeeditors/static/extjs_classes/gradeeditors/DraftEditorWindow.js",
        "deprecated": null
      },
      {
        "href": "DraftEditorWindow.html#devilry-gradeeditors-DraftEditorWindow-method-saveDraft",
        "owner": "devilry.gradeeditors.DraftEditorWindow",
        "params": [
          {
            "type": "Object",
            "doc": "<p>The draftstring to save.</p>\n",
            "optional": false,
            "name": "draftstring"
          },
          {
            "type": "Object",
            "doc": "<p>Called when the save fails. The scope is the draft\n   editor that <code>saveDraft</code> was called from.</p>\n",
            "optional": false,
            "name": "onFailure"
          }
        ],
        "doc": "<p>Save the current draftstring.</p>\n",
        "html_filename": "DraftEditorWindow.html",
        "protected": false,
        "tagname": "method",
        "static": false,
        "return": {
          "type": "void",
          "doc": "\n"
        },
        "private": false,
        "inheritable": false,
        "alias": null,
        "name": "saveDraft",
        "shortDoc": "Save the current draftstring. ...",
        "linenr": 283,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/gradeeditors/static/extjs_classes/gradeeditors/DraftEditorWindow.js",
        "deprecated": null
      },
      {
        "href": "DraftEditorWindow.html#devilry-gradeeditors-DraftEditorWindow-method-saveDraftAndPublish",
        "owner": "devilry.gradeeditors.DraftEditorWindow",
        "params": [
          {
            "type": "Object",
            "doc": "<p>The draftstring to save.</p>\n",
            "optional": false,
            "name": "draftstring"
          },
          {
            "type": "Object",
            "doc": "<p>Called when the save fails. The scope is the draft\n   editor that <code>saveDraft</code> was called from.</p>\n",
            "optional": false,
            "name": "onFailure"
          }
        ],
        "doc": "<p>Save and publish draftstring.</p>\n",
        "html_filename": "DraftEditorWindow.html",
        "protected": false,
        "tagname": "method",
        "static": false,
        "return": {
          "type": "void",
          "doc": "\n"
        },
        "private": false,
        "inheritable": false,
        "alias": null,
        "name": "saveDraftAndPublish",
        "shortDoc": "Save and publish draftstring. ...",
        "linenr": 353,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/gradeeditors/static/extjs_classes/gradeeditors/DraftEditorWindow.js",
        "deprecated": null
      }
    ],
    "css_var": [

    ],
    "css_mixin": [

    ]
  },
  "static": false,
  "author": null,
  "private": false,
  "inheritable": false,
  "alias": null,
  "alternateClassNames": [

  ],
  "statics": {
    "cfg": [

    ],
    "event": [

    ],
    "property": [

    ],
    "method": [

    ],
    "css_var": [

    ],
    "css_mixin": [

    ]
  },
  "name": "devilry.gradeeditors.DraftEditorWindow",
  "linenr": 1,
  "xtypes": [
    "gradedrafteditormainwin"
  ],
  "component": false,
  "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/gradeeditors/static/extjs_classes/gradeeditors/DraftEditorWindow.js",
  "deprecated": null,
  "extends": "Ext.window.Window",
  "docauthor": null
});