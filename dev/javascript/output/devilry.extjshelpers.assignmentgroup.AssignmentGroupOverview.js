Ext.data.JsonP.devilry_extjshelpers_assignmentgroup_AssignmentGroupOverview({
  "subclasses": [

  ],
  "doc": "<p>Combines <a href=\"#/api/devilry.extjshelpers.assignmentgroup.AssignmentGroupInfo\" rel=\"devilry.extjshelpers.assignmentgroup.AssignmentGroupInfo\" class=\"docClass\">devilry.extjshelpers.assignmentgroup.AssignmentGroupInfo</a> and\n<a href=\"#/api/devilry.extjshelpers.assignmentgroup.DeliveryInfo\" rel=\"devilry.extjshelpers.assignmentgroup.DeliveryInfo\" class=\"docClass\">devilry.extjshelpers.assignmentgroup.DeliveryInfo</a>\ninto a complete AssignmentGroup reader and manager\n(if <a href=\"#/api/devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview-cfg-canExamine\" rel=\"devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview-cfg-canExamine\" class=\"docClass\">canExamine</a> is enabled).</p>\n\n<pre><code> -----------------------------------------------------------------\n |                     |                                         |\n |                     |                                         |\n |                     |                                         |\n | AssignmentGroupInfo | DeliveryInfo                            |\n |                     |                                         |\n |                     |                                         |\n |                     |                                         |\n |                     |                                         |\n -----------------------------------------------------------------\n</code></pre>\n",
  "docauthor": null,
  "singleton": false,
  "html_filename": "AssignmentGroupOverview.html",
  "href": "AssignmentGroupOverview.html#devilry-extjshelpers-assignmentgroup-AssignmentGroupOverview",
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
            "type": "Ext.model.Model",
            "doc": "<p>A Delivery record.</p>\n\n<p>Used by <a href=\"#/api/devilry.extjshelpers.assignmentgroup.DeliveryGrid\" rel=\"devilry.extjshelpers.assignmentgroup.DeliveryGrid\" class=\"docClass\">devilry.extjshelpers.assignmentgroup.DeliveryGrid</a> and\ninternally in this class.</p>\n",
            "name": "deliveryrecord",
            "optional": false
          }
        ],
        "owner": "devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview",
        "doc": "<p>Create a <a href=\"#/api/devilry.extjshelpers.assignmentgroup.DeliveryInfo\" rel=\"devilry.extjshelpers.assignmentgroup.DeliveryInfo\" class=\"docClass\">devilry.extjshelpers.assignmentgroup.DeliveryInfo</a>\ncontaining the given delivery and place it in the center area.</p>\n",
        "html_filename": "AssignmentGroupOverview.html",
        "href": "AssignmentGroupOverview.html#devilry-extjshelpers-assignmentgroup-AssignmentGroupOverview-method-setDelivery",
        "tagname": "method",
        "shortDoc": "Create a devilry.extjshelpers.assignmentgroup.DeliveryInfo\ncontaining the given delivery and place it in the center a...",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 149,
        "inheritable": false,
        "alias": null,
        "name": "setDelivery",
        "return": {
          "type": "void",
          "doc": "\n"
        },
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/AssignmentGroupOverview.js",
        "deprecated": null
      }
    ],
    "css_var": [

    ],
    "cfg": [
      {
        "type": "Object",
        "owner": "devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview",
        "doc": "<p>AssignmentGroup id. (Required).</p>\n",
        "html_filename": "AssignmentGroupOverview.html",
        "href": "AssignmentGroupOverview.html#devilry-extjshelpers-assignmentgroup-AssignmentGroupOverview-cfg-assignmentgroupid",
        "tagname": "cfg",
        "shortDoc": "AssignmentGroup id. ...",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 38,
        "inheritable": false,
        "alias": null,
        "name": "assignmentgroupid",
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/AssignmentGroupOverview.js",
        "deprecated": null
      },
      {
        "type": "Object",
        "owner": "devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview",
        "doc": "<p>AssignmentGroup <code>Ext.data.Model</code>. (Required).</p>\n",
        "html_filename": "AssignmentGroupOverview.html",
        "href": "AssignmentGroupOverview.html#devilry-extjshelpers-assignmentgroup-AssignmentGroupOverview-cfg-assignmentgroupmodel",
        "tagname": "cfg",
        "shortDoc": "AssignmentGroup Ext.data.Model. ...",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 44,
        "inheritable": false,
        "alias": null,
        "name": "assignmentgroupmodel",
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/AssignmentGroupOverview.js",
        "deprecated": null
      },
      {
        "type": "Boolean",
        "owner": "devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview",
        "doc": "<p>Enable creation of new feedbacks? Defaults to <code>false</code>.\nSee: <a href=\"#/api/devilry.extjshelpers.assignmentgroup.DeliveryInfo-cfg-canExamine\" rel=\"devilry.extjshelpers.assignmentgroup.DeliveryInfo-cfg-canExamine\" class=\"docClass\">devilry.extjshelpers.assignmentgroup.DeliveryInfo.canExamine</a>.</p>\n\n<p>When this is <code>true</code>, the authenticated user still needs to have\npermission to POST new feedbacks for the view to work.</p>\n",
        "html_filename": "AssignmentGroupOverview.html",
        "href": "AssignmentGroupOverview.html#devilry-extjshelpers-assignmentgroup-AssignmentGroupOverview-cfg-canExamine",
        "tagname": "cfg",
        "shortDoc": "Enable creation of new feedbacks? Defaults to false. ...",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 80,
        "inheritable": false,
        "alias": null,
        "name": "canExamine",
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/AssignmentGroupOverview.js",
        "deprecated": null
      },
      {
        "type": "Object",
        "owner": "devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview",
        "doc": "<p>Deadline <code>Ext.data.Store</code>. (Required).\n<em>Note</em> that <code>deadlinestore.proxy.extraParams</code> is changed by\n<a href=\"#/api/devilry.extjshelpers.assignmentgroup.DeadlineListing\" rel=\"devilry.extjshelpers.assignmentgroup.DeadlineListing\" class=\"docClass\">devilry.extjshelpers.assignmentgroup.DeadlineListing</a>.</p>\n",
        "html_filename": "AssignmentGroupOverview.html",
        "href": "AssignmentGroupOverview.html#devilry-extjshelpers-assignmentgroup-AssignmentGroupOverview-cfg-deadlinestore",
        "tagname": "cfg",
        "shortDoc": "Deadline Ext.data.Store. ...",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 56,
        "inheritable": false,
        "alias": null,
        "name": "deadlinestore",
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/AssignmentGroupOverview.js",
        "deprecated": null
      },
      {
        "type": "Object",
        "owner": "devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview",
        "doc": "<p>Delivery  <code>Ext.data.Model</code>. (Required).</p>\n",
        "html_filename": "AssignmentGroupOverview.html",
        "href": "AssignmentGroupOverview.html#devilry-extjshelpers-assignmentgroup-AssignmentGroupOverview-cfg-deliverymodel",
        "tagname": "cfg",
        "shortDoc": "Delivery  Ext.data.Model. ...",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 50,
        "inheritable": false,
        "alias": null,
        "name": "deliverymodel",
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/AssignmentGroupOverview.js",
        "deprecated": null
      },
      {
        "type": "Object",
        "owner": "devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview",
        "doc": "<p>FileMeta <code>Ext.data.Store</code>. (Required).\n<em>Note</em> that <code>filemetastore.proxy.extraParams</code> is changed by\n<a href=\"#/api/devilry.extjshelpers.assignmentgroup.DeliveryInfo\" rel=\"devilry.extjshelpers.assignmentgroup.DeliveryInfo\" class=\"docClass\">devilry.extjshelpers.assignmentgroup.DeliveryInfo</a>.</p>\n",
        "html_filename": "AssignmentGroupOverview.html",
        "href": "AssignmentGroupOverview.html#devilry-extjshelpers-assignmentgroup-AssignmentGroupOverview-cfg-filemetastore",
        "tagname": "cfg",
        "shortDoc": "FileMeta Ext.data.Store. ...",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 64,
        "inheritable": false,
        "alias": null,
        "name": "filemetastore",
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/AssignmentGroupOverview.js",
        "deprecated": null
      },
      {
        "type": "Object",
        "owner": "devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview",
        "doc": "<p>FileMeta <code>Ext.data.Store</code>. (Required).\n<em>Note</em> that <code>filemetastore.proxy.extraParams</code> is changed by\n<a href=\"#/api/devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo\" rel=\"devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo\" class=\"docClass\">devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo</a>.</p>\n",
        "html_filename": "AssignmentGroupOverview.html",
        "href": "AssignmentGroupOverview.html#devilry-extjshelpers-assignmentgroup-AssignmentGroupOverview-cfg-staticfeedbackstore",
        "tagname": "cfg",
        "shortDoc": "FileMeta Ext.data.Store. ...",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 72,
        "inheritable": false,
        "alias": null,
        "name": "staticfeedbackstore",
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/AssignmentGroupOverview.js",
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
  "linenr": 1,
  "inheritable": false,
  "alias": null,
  "name": "devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview",
  "xtypes": [
    "assignmentgroupoverview"
  ],
  "extends": "Ext.panel.Panel",
  "allMixins": [

  ],
  "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/AssignmentGroupOverview.js",
  "deprecated": null
});