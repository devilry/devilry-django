Ext.data.JsonP.devilry_extjshelpers_assignmentgroup_DeliveryInfo({
  "subclasses": [

  ],
  "doc": "<p>Panel to show Delivery info.\nUses <a href=\"#/api/devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo\" rel=\"devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo\" class=\"docClass\">devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo</a>\nor <a href=\"#/api/devilry.extjshelpers.assignmentgroup.StaticFeedbackEditableInfo\" rel=\"devilry.extjshelpers.assignmentgroup.StaticFeedbackEditableInfo\" class=\"docClass\">devilry.extjshelpers.assignmentgroup.StaticFeedbackEditableInfo</a>\nto show and manage StaticFeedback (see <a href=\"#/api/devilry.extjshelpers.assignmentgroup.DeliveryInfo-cfg-canExamine\" rel=\"devilry.extjshelpers.assignmentgroup.DeliveryInfo-cfg-canExamine\" class=\"docClass\">canExamine</a>)</p>\n\n<pre><code> -------------------------------------------\n | Info about the delivery                 |\n |                                         |\n |                                         |\n -------------------------------------------\n | StaticFeedbackInfo                      |\n | or                                      |\n | StaticFeedbackEditableInfo              |\n |                                         |\n |                                         |\n |                                         |\n |                                         |\n -------------------------------------------\n</code></pre>\n",
  "docauthor": null,
  "singleton": false,
  "html_filename": "DeliveryInfo.html",
  "href": "DeliveryInfo.html#devilry-extjshelpers-assignmentgroup-DeliveryInfo",
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

    ],
    "css_var": [

    ],
    "cfg": [
      {
        "type": "Object",
        "owner": "devilry.extjshelpers.assignmentgroup.DeliveryInfo",
        "doc": "<p>Assignment id. Required for\n<a href=\"#/api/devilry.extjshelpers.assignmentgroup.StaticFeedbackEditableInfo\" rel=\"devilry.extjshelpers.assignmentgroup.StaticFeedbackEditableInfo\" class=\"docClass\">devilry.extjshelpers.assignmentgroup.StaticFeedbackEditableInfo</a>,\nwhich is used if the <code>canExamine</code> config is <code>true</code>.</p>\n",
        "html_filename": "DeliveryInfo.html",
        "href": "DeliveryInfo.html#devilry-extjshelpers-assignmentgroup-DeliveryInfo-cfg-assignmentid",
        "tagname": "cfg",
        "shortDoc": "Assignment id. ...",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 56,
        "inheritable": false,
        "alias": null,
        "name": "assignmentid",
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/DeliveryInfo.js",
        "deprecated": null
      },
      {
        "type": "Boolean",
        "owner": "devilry.extjshelpers.assignmentgroup.DeliveryInfo",
        "doc": "<p>Enable creation of new feedbacks? Defaults to <code>false</code>.</p>\n\n<p>If this is <code>true</code>,\n<a href=\"#/api/devilry.extjshelpers.assignmentgroup.StaticFeedbackEditableInfo\" rel=\"devilry.extjshelpers.assignmentgroup.StaticFeedbackEditableInfo\" class=\"docClass\">devilry.extjshelpers.assignmentgroup.StaticFeedbackEditableInfo</a>\nis used instead of\n<a href=\"#/api/devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo\" rel=\"devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo\" class=\"docClass\">devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo</a>.</p>\n\n<p>If this is <code>true</code>, the <code>assignmentid</code> config is <em>required</em>.</p>\n\n<p>When this is <code>true</code>, the authenticated user still needs to have\npermission to POST new feedbacks for the view to work.</p>\n",
        "html_filename": "DeliveryInfo.html",
        "href": "DeliveryInfo.html#devilry-extjshelpers-assignmentgroup-DeliveryInfo-cfg-canExamine",
        "tagname": "cfg",
        "shortDoc": "Enable creation of new feedbacks? Defaults to false. ...",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 40,
        "inheritable": false,
        "alias": null,
        "name": "canExamine",
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/DeliveryInfo.js",
        "deprecated": null
      },
      {
        "type": "Object",
        "owner": "devilry.extjshelpers.assignmentgroup.DeliveryInfo",
        "doc": "<p>A delivery object, such as <code>data</code> attribute of a\nrecord loaded from a Delivery store or model.</p>\n",
        "html_filename": "DeliveryInfo.html",
        "href": "DeliveryInfo.html#devilry-extjshelpers-assignmentgroup-DeliveryInfo-cfg-delivery",
        "tagname": "cfg",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 33,
        "inheritable": false,
        "alias": null,
        "name": "delivery",
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/DeliveryInfo.js",
        "deprecated": null
      },
      {
        "type": "Object",
        "owner": "devilry.extjshelpers.assignmentgroup.DeliveryInfo",
        "doc": "<p>FileMeta <code>Ext.data.Store</code>. (Required).\n<em>Note</em> that <code>filemetastore.proxy.extraParams</code> is changed by this\nclass.</p>\n",
        "html_filename": "DeliveryInfo.html",
        "href": "DeliveryInfo.html#devilry-extjshelpers-assignmentgroup-DeliveryInfo-cfg-filemetastore",
        "tagname": "cfg",
        "shortDoc": "FileMeta Ext.data.Store. ...",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 64,
        "inheritable": false,
        "alias": null,
        "name": "filemetastore",
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/DeliveryInfo.js",
        "deprecated": null
      },
      {
        "type": "Object",
        "owner": "devilry.extjshelpers.assignmentgroup.DeliveryInfo",
        "doc": "<p>FileMeta <code>Ext.data.Store</code>. (Required).\n<em>Note</em> that <code>filemetastore.proxy.extraParams</code> is changed by\n<a href=\"#/api/devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo\" rel=\"devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo\" class=\"docClass\">devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo</a>.</p>\n",
        "html_filename": "DeliveryInfo.html",
        "href": "DeliveryInfo.html#devilry-extjshelpers-assignmentgroup-DeliveryInfo-cfg-staticfeedbackstore",
        "tagname": "cfg",
        "shortDoc": "FileMeta Ext.data.Store. ...",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 72,
        "inheritable": false,
        "alias": null,
        "name": "staticfeedbackstore",
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/DeliveryInfo.js",
        "deprecated": null
      }
    ],
    "event": [

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
  "linenr": 2,
  "inheritable": false,
  "alias": null,
  "name": "devilry.extjshelpers.assignmentgroup.DeliveryInfo",
  "xtypes": [
    "deliveryinfo"
  ],
  "extends": "Ext.panel.Panel",
  "allMixins": [

  ],
  "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/DeliveryInfo.js",
  "deprecated": null
});