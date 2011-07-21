Ext.data.JsonP.devilry_extjshelpers_assignmentgroup_DeliveryInfo({
  "tagname": "class",
  "name": "devilry.extjshelpers.assignmentgroup.DeliveryInfo",
  "doc": "<p>Panel to show Delivery info.\nUses <a href=\"#/api/devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo\" rel=\"devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo\" class=\"docClass\">devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo</a>\nor <a href=\"#/api/devilry.extjshelpers.assignmentgroup.StaticFeedbackEditableInfo\" rel=\"devilry.extjshelpers.assignmentgroup.StaticFeedbackEditableInfo\" class=\"docClass\">devilry.extjshelpers.assignmentgroup.StaticFeedbackEditableInfo</a>\nto show and manage StaticFeedback (see <a href=\"#/api/devilry.extjshelpers.assignmentgroup.DeliveryInfo-cfg-canExamine\" rel=\"devilry.extjshelpers.assignmentgroup.DeliveryInfo-cfg-canExamine\" class=\"docClass\">canExamine</a>)</p>\n\n<pre><code> -------------------------------------------\n | Info about the delivery                 |\n |                                         |\n |                                         |\n -------------------------------------------\n | StaticFeedbackInfo                      |\n | or                                      |\n | StaticFeedbackEditableInfo              |\n |                                         |\n |                                         |\n |                                         |\n |                                         |\n -------------------------------------------\n</code></pre>\n",
  "extends": "Ext.panel.Panel",
  "mixins": [

  ],
  "alternateClassNames": [

  ],
  "xtypes": [
    "deliveryinfo"
  ],
  "author": null,
  "docauthor": null,
  "singleton": false,
  "code_type": "ext_define",
  "private": false,
  "protected": false,
  "static": false,
  "inheritable": false,
  "deprecated": null,
  "alias": null,
  "members": {
    "cfg": [
      {
        "tagname": "cfg",
        "name": "assignmentid",
        "owner": "devilry.extjshelpers.assignmentgroup.DeliveryInfo",
        "type": "Object",
        "doc": "<p>Assignment id. Required for\n<a href=\"#/api/devilry.extjshelpers.assignmentgroup.StaticFeedbackEditableInfo\" rel=\"devilry.extjshelpers.assignmentgroup.StaticFeedbackEditableInfo\" class=\"docClass\">devilry.extjshelpers.assignmentgroup.StaticFeedbackEditableInfo</a>,\nwhich is used if the <code>canExamine</code> config is <code>true</code>.</p>\n",
        "private": false,
        "protected": false,
        "static": false,
        "inheritable": false,
        "deprecated": null,
        "alias": null,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/DeliveryInfo.js",
        "linenr": 56,
        "html_filename": "DeliveryInfo.html",
        "href": "DeliveryInfo.html#devilry-extjshelpers-assignmentgroup-DeliveryInfo-cfg-assignmentid",
        "shortDoc": "Assignment id. ..."
      },
      {
        "tagname": "cfg",
        "name": "canExamine",
        "owner": "devilry.extjshelpers.assignmentgroup.DeliveryInfo",
        "type": "Boolean",
        "doc": "<p>Enable creation of new feedbacks? Defaults to <code>false</code>.</p>\n\n<p>If this is <code>true</code>,\n<a href=\"#/api/devilry.extjshelpers.assignmentgroup.StaticFeedbackEditableInfo\" rel=\"devilry.extjshelpers.assignmentgroup.StaticFeedbackEditableInfo\" class=\"docClass\">devilry.extjshelpers.assignmentgroup.StaticFeedbackEditableInfo</a>\nis used instead of\n<a href=\"#/api/devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo\" rel=\"devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo\" class=\"docClass\">devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo</a>.</p>\n\n<p>If this is <code>true</code>, the <code>assignmentid</code> config is <em>required</em>.</p>\n\n<p>When this is <code>true</code>, the authenticated user still needs to have\npermission to POST new feedbacks for the view to work.</p>\n",
        "private": false,
        "protected": false,
        "static": false,
        "inheritable": false,
        "deprecated": null,
        "alias": null,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/DeliveryInfo.js",
        "linenr": 40,
        "html_filename": "DeliveryInfo.html",
        "href": "DeliveryInfo.html#devilry-extjshelpers-assignmentgroup-DeliveryInfo-cfg-canExamine",
        "shortDoc": "Enable creation of new feedbacks? Defaults to false. ..."
      },
      {
        "tagname": "cfg",
        "name": "delivery",
        "owner": "devilry.extjshelpers.assignmentgroup.DeliveryInfo",
        "type": "Object",
        "doc": "<p>A delivery object, such as <code>data</code> attribute of a\nrecord loaded from a Delivery store or model.</p>\n",
        "private": false,
        "protected": false,
        "static": false,
        "inheritable": false,
        "deprecated": null,
        "alias": null,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/DeliveryInfo.js",
        "linenr": 33,
        "html_filename": "DeliveryInfo.html",
        "href": "DeliveryInfo.html#devilry-extjshelpers-assignmentgroup-DeliveryInfo-cfg-delivery"
      },
      {
        "tagname": "cfg",
        "name": "filemetastore",
        "owner": "devilry.extjshelpers.assignmentgroup.DeliveryInfo",
        "type": "Object",
        "doc": "<p>FileMeta <code>Ext.data.Store</code>. (Required).\n<em>Note</em> that <code>filemetastore.proxy.extraParams</code> is changed by this\nclass.</p>\n",
        "private": false,
        "protected": false,
        "static": false,
        "inheritable": false,
        "deprecated": null,
        "alias": null,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/DeliveryInfo.js",
        "linenr": 64,
        "html_filename": "DeliveryInfo.html",
        "href": "DeliveryInfo.html#devilry-extjshelpers-assignmentgroup-DeliveryInfo-cfg-filemetastore",
        "shortDoc": "FileMeta Ext.data.Store. ..."
      },
      {
        "tagname": "cfg",
        "name": "staticfeedbackstore",
        "owner": "devilry.extjshelpers.assignmentgroup.DeliveryInfo",
        "type": "Object",
        "doc": "<p>FileMeta <code>Ext.data.Store</code>. (Required).\n<em>Note</em> that <code>filemetastore.proxy.extraParams</code> is changed by\n<a href=\"#/api/devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo\" rel=\"devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo\" class=\"docClass\">devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo</a>.</p>\n",
        "private": false,
        "protected": false,
        "static": false,
        "inheritable": false,
        "deprecated": null,
        "alias": null,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/DeliveryInfo.js",
        "linenr": 72,
        "html_filename": "DeliveryInfo.html",
        "href": "DeliveryInfo.html#devilry-extjshelpers-assignmentgroup-DeliveryInfo-cfg-staticfeedbackstore",
        "shortDoc": "FileMeta Ext.data.Store. ..."
      }
    ],
    "property": [

    ],
    "method": [

    ],
    "event": [

    ],
    "css_var": [

    ],
    "css_mixin": [

    ]
  },
  "statics": {
    "cfg": [

    ],
    "property": [

    ],
    "method": [

    ],
    "event": [

    ],
    "css_var": [

    ],
    "css_mixin": [

    ]
  },
  "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/DeliveryInfo.js",
  "linenr": 2,
  "html_filename": "DeliveryInfo.html",
  "href": "DeliveryInfo.html#devilry-extjshelpers-assignmentgroup-DeliveryInfo",
  "component": false,
  "superclasses": [

  ],
  "subclasses": [

  ],
  "mixedInto": [

  ],
  "allMixins": [

  ]
});