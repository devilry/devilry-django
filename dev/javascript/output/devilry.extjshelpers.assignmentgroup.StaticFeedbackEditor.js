Ext.data.JsonP.devilry_extjshelpers_assignmentgroup_StaticFeedbackEditor({
  "mixedInto": [

  ],
  "href": "StaticFeedbackEditor.html#devilry-extjshelpers-assignmentgroup-StaticFeedbackEditor",
  "allMixins": [

  ],
  "doc": "<p>Panel to show StaticFeedback info and create new static feedbacks.</p>\n",
  "singleton": false,
  "html_filename": "StaticFeedbackEditor.html",
  "code_type": "ext_define",
  "subclasses": [

  ],
  "superclasses": [
    "devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo"
  ],
  "protected": false,
  "tagname": "class",
  "mixins": [

  ],
  "members": {
    "cfg": [
      {
        "type": "Object",
        "href": "StaticFeedbackInfo.html#devilry-extjshelpers-assignmentgroup-StaticFeedbackInfo-cfg-delivery_recordcontainer",
        "owner": "devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo",
        "doc": "<p>A <a href=\"#/api/devilry.extjshelpers.SingleRecordContainer\" rel=\"devilry.extjshelpers.SingleRecordContainer\" class=\"docClass\">devilry.extjshelpers.SingleRecordContainer</a> for Delivery.</p>\n",
        "html_filename": "StaticFeedbackInfo.html",
        "protected": false,
        "tagname": "cfg",
        "static": false,
        "private": false,
        "inheritable": false,
        "alias": null,
        "name": "delivery_recordcontainer",
        "linenr": 22,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/StaticFeedbackInfo.js",
        "deprecated": null
      },
      {
        "type": "Object",
        "href": "StaticFeedbackEditor.html#devilry-extjshelpers-assignmentgroup-StaticFeedbackEditor-cfg-gradeeditor_config_recordcontainer",
        "owner": "devilry.extjshelpers.assignmentgroup.StaticFeedbackEditor",
        "doc": "<p>A <a href=\"#/api/devilry.extjshelpers.SingleRecordContainer\" rel=\"devilry.extjshelpers.SingleRecordContainer\" class=\"docClass\">devilry.extjshelpers.SingleRecordContainer</a> for GradeEditor Config.</p>\n",
        "html_filename": "StaticFeedbackEditor.html",
        "protected": false,
        "tagname": "cfg",
        "static": false,
        "private": false,
        "inheritable": false,
        "alias": null,
        "name": "gradeeditor_config_recordcontainer",
        "linenr": 13,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/StaticFeedbackEditor.js",
        "deprecated": null
      },
      {
        "type": "Boolean",
        "href": "StaticFeedbackEditor.html#devilry-extjshelpers-assignmentgroup-StaticFeedbackEditor-cfg-isAdministrator",
        "owner": "devilry.extjshelpers.assignmentgroup.StaticFeedbackEditor",
        "doc": "<p>Use the administrator RESTful interface to store drafts? If this is\n<code>false</code>, we use the examiner RESTful interface.</p>\n",
        "html_filename": "StaticFeedbackEditor.html",
        "protected": false,
        "tagname": "cfg",
        "static": false,
        "private": false,
        "inheritable": false,
        "alias": null,
        "name": "isAdministrator",
        "linenr": 19,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/StaticFeedbackEditor.js",
        "deprecated": null
      },
      {
        "type": "Object",
        "href": "StaticFeedbackInfo.html#devilry-extjshelpers-assignmentgroup-StaticFeedbackInfo-cfg-staticfeedbackstore",
        "owner": "devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo",
        "doc": "<p>FileMeta <code>Ext.data.Store</code>. (Required).\n<em>Note</em> that <code>filemetastore.proxy.extraParams</code> is changed by this\nclass.</p>\n",
        "html_filename": "StaticFeedbackInfo.html",
        "protected": false,
        "tagname": "cfg",
        "static": false,
        "private": false,
        "inheritable": false,
        "alias": null,
        "name": "staticfeedbackstore",
        "shortDoc": "FileMeta Ext.data.Store. ...",
        "linenr": 14,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/StaticFeedbackInfo.js",
        "deprecated": null
      }
    ],
    "event": [

    ],
    "property": [

    ],
    "method": [
      {
        "href": "StaticFeedbackEditor.html#devilry-extjshelpers-assignmentgroup-StaticFeedbackEditor-method-bodyWithNoFeedback",
        "owner": "devilry.extjshelpers.assignmentgroup.StaticFeedbackEditor",
        "params": [

        ],
        "doc": "<p>Overrides parent method to enable examiners to click to create feedback.</p>\n",
        "html_filename": "StaticFeedbackEditor.html",
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
        "name": "bodyWithNoFeedback",
        "shortDoc": "Overrides parent method to enable examiners to click to create feedback. ...",
        "linenr": 144,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/StaticFeedbackEditor.js",
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
  "name": "devilry.extjshelpers.assignmentgroup.StaticFeedbackEditor",
  "linenr": 1,
  "xtypes": [
    "staticfeedbackeditor"
  ],
  "component": false,
  "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/StaticFeedbackEditor.js",
  "deprecated": null,
  "extends": "devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo",
  "docauthor": null
});