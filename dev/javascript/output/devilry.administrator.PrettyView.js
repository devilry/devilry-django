Ext.data.JsonP.devilry_administrator_PrettyView({
  "subclasses": [
    "devilry.administrator.assignment.PrettyView",
    "devilry.administrator.period.PrettyView"
  ],
  "doc": "<p>A prettyview is a read-only view panel used to display a single model record.</p>\n",
  "docauthor": null,
  "singleton": false,
  "html_filename": "PrettyView.html",
  "href": "PrettyView.html#devilry-administrator-PrettyView",
  "code_type": "ext_define",
  "superclasses": [

  ],
  "tagname": "class",
  "mixins": [

  ],
  "protected": false,
  "static": false,
  "component": false,
  "members": {
    "property": [

    ],
    "method": [
      {
        "params": [
          {
            "type": "Object",
            "doc": "\n",
            "name": "record",
            "optional": false
          }
        ],
        "owner": "devilry.administrator.PrettyView",
        "doc": "<p>Set record. Triggers the loadmodel event.</p>\n",
        "html_filename": "PrettyView.html",
        "href": "PrettyView.html#devilry-administrator-PrettyView-method-setRecord",
        "tagname": "method",
        "shortDoc": "Set record. ...",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 127,
        "inheritable": false,
        "alias": null,
        "name": "setRecord",
        "return": {
          "type": "void",
          "doc": "\n"
        },
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/administrator/static/extjs_classes/administrator/PrettyView.js",
        "deprecated": null
      }
    ],
    "css_var": [

    ],
    "cfg": [
      {
        "type": "Object",
        "owner": "devilry.administrator.PrettyView",
        "doc": "<p>Optional list of menuitems for plugin actions.</p>\n",
        "html_filename": "PrettyView.html",
        "href": "PrettyView.html#devilry-administrator-PrettyView-cfg-",
        "tagname": "cfg",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 39,
        "inheritable": false,
        "alias": null,
        "name": "",
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/administrator/static/extjs_classes/administrator/PrettyView.js",
        "deprecated": null
      },
      {
        "type": "Object",
        "owner": "devilry.administrator.PrettyView",
        "doc": "<p>A <code>Ext.XTemplate</code> object for the body of this view. (Required).</p>\n",
        "html_filename": "PrettyView.html",
        "href": "PrettyView.html#devilry-administrator-PrettyView-cfg-bodyTpl",
        "tagname": "cfg",
        "shortDoc": "A Ext.XTemplate object for the body of this view. ...",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 20,
        "inheritable": false,
        "alias": null,
        "name": "bodyTpl",
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/administrator/static/extjs_classes/administrator/PrettyView.js",
        "deprecated": null
      },
      {
        "type": "Object",
        "owner": "devilry.administrator.PrettyView",
        "doc": "<p>The url to the dashboard. (Required). Used after delete to return to\nthe dashboard.</p>\n",
        "html_filename": "PrettyView.html",
        "href": "PrettyView.html#devilry-administrator-PrettyView-cfg-dashboardUrl",
        "tagname": "cfg",
        "shortDoc": "The url to the dashboard. ...",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 32,
        "inheritable": false,
        "alias": null,
        "name": "dashboardUrl",
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/administrator/static/extjs_classes/administrator/PrettyView.js",
        "deprecated": null
      },
      {
        "type": "Object",
        "owner": "devilry.administrator.PrettyView",
        "doc": "<p>The name of the <code>Ext.data.Model</code> to present in the body. (Required).</p>\n",
        "html_filename": "PrettyView.html",
        "href": "PrettyView.html#devilry-administrator-PrettyView-cfg-modelname",
        "tagname": "cfg",
        "shortDoc": "The name of the Ext.data.Model to present in the body. ...",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 8,
        "inheritable": false,
        "alias": null,
        "name": "modelname",
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/administrator/static/extjs_classes/administrator/PrettyView.js",
        "deprecated": null
      },
      {
        "type": "Object",
        "owner": "devilry.administrator.PrettyView",
        "doc": "<p>Unique ID of the object to load from the model. (Required).</p>\n",
        "html_filename": "PrettyView.html",
        "href": "PrettyView.html#devilry-administrator-PrettyView-cfg-objectid",
        "tagname": "cfg",
        "shortDoc": "Unique ID of the object to load from the model. ...",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 14,
        "inheritable": false,
        "alias": null,
        "name": "objectid",
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/administrator/static/extjs_classes/administrator/PrettyView.js",
        "deprecated": null
      },
      {
        "type": "Object",
        "owner": "devilry.administrator.PrettyView",
        "doc": "<p>Optional list of buttons for related actions.</p>\n",
        "html_filename": "PrettyView.html",
        "href": "PrettyView.html#devilry-administrator-PrettyView-cfg-relatedButtons",
        "tagname": "cfg",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 26,
        "inheritable": false,
        "alias": null,
        "name": "relatedButtons",
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/administrator/static/extjs_classes/administrator/PrettyView.js",
        "deprecated": null
      }
    ],
    "event": [
      {
        "params": [
          {
            "type": "Ext.model.Model",
            "doc": "<p>The record to edit.</p>\n",
            "name": "record",
            "optional": false
          },
          {
            "type": "Object",
            "doc": "<p>The options object passed to Ext.util.Observable.addListener.</p>\n",
            "tagname": "param",
            "name": "options"
          }
        ],
        "owner": "devilry.administrator.PrettyView",
        "doc": "<p>Fired when the edit button is clicked.</p>\n",
        "html_filename": "PrettyView.html",
        "href": "PrettyView.html#devilry-administrator-PrettyView-event-edit",
        "tagname": "event",
        "shortDoc": "Fired when the edit button is clicked. ...",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 55,
        "inheritable": false,
        "alias": null,
        "name": "edit",
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/administrator/static/extjs_classes/administrator/PrettyView.js",
        "deprecated": null
      },
      {
        "params": [
          {
            "type": "Ext.model.Model",
            "doc": "<p>The loaded record.</p>\n",
            "name": "record",
            "optional": false
          },
          {
            "type": "Object",
            "doc": "<p>The options object passed to Ext.util.Observable.addListener.</p>\n",
            "tagname": "param",
            "name": "options"
          }
        ],
        "owner": "devilry.administrator.PrettyView",
        "doc": "<p>Fired when the model record is loaded successfully.</p>\n",
        "html_filename": "PrettyView.html",
        "href": "PrettyView.html#devilry-administrator-PrettyView-event-loadmodel",
        "tagname": "event",
        "shortDoc": "Fired when the model record is loaded successfully. ...",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 48,
        "inheritable": false,
        "alias": null,
        "name": "loadmodel",
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/administrator/static/extjs_classes/administrator/PrettyView.js",
        "deprecated": null
      }
    ],
    "css_mixin": [

    ]
  },
  "alternateClassNames": [

  ],
  "author": null,
  "statics": {
    "property": [

    ],
    "method": [

    ],
    "css_var": [

    ],
    "cfg": [

    ],
    "event": [

    ],
    "css_mixin": [

    ]
  },
  "private": false,
  "mixedInto": [

  ],
  "linenr": 1,
  "inheritable": false,
  "alias": null,
  "name": "devilry.administrator.PrettyView",
  "xtypes": [

  ],
  "extends": "Ext.panel.Panel",
  "allMixins": [

  ],
  "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/administrator/static/extjs_classes/administrator/PrettyView.js",
  "deprecated": null
});