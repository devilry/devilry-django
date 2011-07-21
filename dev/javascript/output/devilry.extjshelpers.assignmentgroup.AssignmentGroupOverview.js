Ext.data.JsonP.devilry_extjshelpers_assignmentgroup_AssignmentGroupOverview({
  "tagname": "class",
  "name": "devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview",
  "doc": "<p>Combines <a href=\"#/api/devilry.extjshelpers.assignmentgroup.AssignmentGroupInfo\" rel=\"devilry.extjshelpers.assignmentgroup.AssignmentGroupInfo\" class=\"docClass\">devilry.extjshelpers.assignmentgroup.AssignmentGroupInfo</a> and\n<a href=\"#/api/devilry.extjshelpers.assignmentgroup.DeliveryInfo\" rel=\"devilry.extjshelpers.assignmentgroup.DeliveryInfo\" class=\"docClass\">devilry.extjshelpers.assignmentgroup.DeliveryInfo</a>\ninto a complete AssignmentGroup reader and manager\n(if <a href=\"#/api/devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview-cfg-canExamine\" rel=\"devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview-cfg-canExamine\" class=\"docClass\">canExamine</a> is enabled).</p>\n\n<pre><code> -----------------------------------------------------------------\n |                     |                                         |\n |                     |                                         |\n |                     |                                         |\n | AssignmentGroupInfo | DeliveryInfo                            |\n |                     |                                         |\n |                     |                                         |\n |                     |                                         |\n |                     |                                         |\n -----------------------------------------------------------------\n</code></pre>\n",
  "extends": "Ext.panel.Panel",
  "mixins": [

  ],
  "alternateClassNames": [

  ],
  "xtypes": [
    "assignmentgroupoverview"
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
        "name": "assignmentgroupid",
        "owner": "devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview",
        "type": "Object",
        "doc": "<p>AssignmentGroup id. (Required).</p>\n",
        "private": false,
        "protected": false,
        "static": false,
        "inheritable": false,
        "deprecated": null,
        "alias": null,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/AssignmentGroupOverview.js",
        "linenr": 38,
        "html_filename": "AssignmentGroupOverview.html",
        "href": "AssignmentGroupOverview.html#devilry-extjshelpers-assignmentgroup-AssignmentGroupOverview-cfg-assignmentgroupid",
        "shortDoc": "AssignmentGroup id. ..."
      },
      {
        "tagname": "cfg",
        "name": "assignmentgroupmodel",
        "owner": "devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview",
        "type": "Object",
        "doc": "<p>AssignmentGroup <code>Ext.data.Model</code>. (Required).</p>\n",
        "private": false,
        "protected": false,
        "static": false,
        "inheritable": false,
        "deprecated": null,
        "alias": null,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/AssignmentGroupOverview.js",
        "linenr": 44,
        "html_filename": "AssignmentGroupOverview.html",
        "href": "AssignmentGroupOverview.html#devilry-extjshelpers-assignmentgroup-AssignmentGroupOverview-cfg-assignmentgroupmodel",
        "shortDoc": "AssignmentGroup Ext.data.Model. ..."
      },
      {
        "tagname": "cfg",
        "name": "canExamine",
        "owner": "devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview",
        "type": "Boolean",
        "doc": "<p>Enable creation of new feedbacks? Defaults to <code>false</code>.\nSee: <a href=\"#/api/devilry.extjshelpers.assignmentgroup.DeliveryInfo-cfg-canExamine\" rel=\"devilry.extjshelpers.assignmentgroup.DeliveryInfo-cfg-canExamine\" class=\"docClass\">devilry.extjshelpers.assignmentgroup.DeliveryInfo.canExamine</a>.</p>\n\n<p>When this is <code>true</code>, the authenticated user still needs to have\npermission to POST new feedbacks for the view to work.</p>\n",
        "private": false,
        "protected": false,
        "static": false,
        "inheritable": false,
        "deprecated": null,
        "alias": null,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/AssignmentGroupOverview.js",
        "linenr": 80,
        "html_filename": "AssignmentGroupOverview.html",
        "href": "AssignmentGroupOverview.html#devilry-extjshelpers-assignmentgroup-AssignmentGroupOverview-cfg-canExamine",
        "shortDoc": "Enable creation of new feedbacks? Defaults to false. ..."
      },
      {
        "tagname": "cfg",
        "name": "deadlinestore",
        "owner": "devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview",
        "type": "Object",
        "doc": "<p>Deadline <code>Ext.data.Store</code>. (Required).\n<em>Note</em> that <code>deadlinestore.proxy.extraParams</code> is changed by\n<a href=\"#/api/devilry.extjshelpers.assignmentgroup.DeadlineListing\" rel=\"devilry.extjshelpers.assignmentgroup.DeadlineListing\" class=\"docClass\">devilry.extjshelpers.assignmentgroup.DeadlineListing</a>.</p>\n",
        "private": false,
        "protected": false,
        "static": false,
        "inheritable": false,
        "deprecated": null,
        "alias": null,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/AssignmentGroupOverview.js",
        "linenr": 56,
        "html_filename": "AssignmentGroupOverview.html",
        "href": "AssignmentGroupOverview.html#devilry-extjshelpers-assignmentgroup-AssignmentGroupOverview-cfg-deadlinestore",
        "shortDoc": "Deadline Ext.data.Store. ..."
      },
      {
        "tagname": "cfg",
        "name": "deliverymodel",
        "owner": "devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview",
        "type": "Object",
        "doc": "<p>Delivery  <code>Ext.data.Model</code>. (Required).</p>\n",
        "private": false,
        "protected": false,
        "static": false,
        "inheritable": false,
        "deprecated": null,
        "alias": null,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/AssignmentGroupOverview.js",
        "linenr": 50,
        "html_filename": "AssignmentGroupOverview.html",
        "href": "AssignmentGroupOverview.html#devilry-extjshelpers-assignmentgroup-AssignmentGroupOverview-cfg-deliverymodel",
        "shortDoc": "Delivery  Ext.data.Model. ..."
      },
      {
        "tagname": "cfg",
        "name": "filemetastore",
        "owner": "devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview",
        "type": "Object",
        "doc": "<p>FileMeta <code>Ext.data.Store</code>. (Required).\n<em>Note</em> that <code>filemetastore.proxy.extraParams</code> is changed by\n<a href=\"#/api/devilry.extjshelpers.assignmentgroup.DeliveryInfo\" rel=\"devilry.extjshelpers.assignmentgroup.DeliveryInfo\" class=\"docClass\">devilry.extjshelpers.assignmentgroup.DeliveryInfo</a>.</p>\n",
        "private": false,
        "protected": false,
        "static": false,
        "inheritable": false,
        "deprecated": null,
        "alias": null,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/AssignmentGroupOverview.js",
        "linenr": 64,
        "html_filename": "AssignmentGroupOverview.html",
        "href": "AssignmentGroupOverview.html#devilry-extjshelpers-assignmentgroup-AssignmentGroupOverview-cfg-filemetastore",
        "shortDoc": "FileMeta Ext.data.Store. ..."
      },
      {
        "tagname": "cfg",
        "name": "staticfeedbackstore",
        "owner": "devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview",
        "type": "Object",
        "doc": "<p>FileMeta <code>Ext.data.Store</code>. (Required).\n<em>Note</em> that <code>filemetastore.proxy.extraParams</code> is changed by\n<a href=\"#/api/devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo\" rel=\"devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo\" class=\"docClass\">devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo</a>.</p>\n",
        "private": false,
        "protected": false,
        "static": false,
        "inheritable": false,
        "deprecated": null,
        "alias": null,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/AssignmentGroupOverview.js",
        "linenr": 72,
        "html_filename": "AssignmentGroupOverview.html",
        "href": "AssignmentGroupOverview.html#devilry-extjshelpers-assignmentgroup-AssignmentGroupOverview-cfg-staticfeedbackstore",
        "shortDoc": "FileMeta Ext.data.Store. ..."
      }
    ],
    "property": [

    ],
    "method": [
      {
        "tagname": "method",
        "name": "setDelivery",
        "owner": "devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview",
        "doc": "<p>Create a <a href=\"#/api/devilry.extjshelpers.assignmentgroup.DeliveryInfo\" rel=\"devilry.extjshelpers.assignmentgroup.DeliveryInfo\" class=\"docClass\">devilry.extjshelpers.assignmentgroup.DeliveryInfo</a>\ncontaining the given delivery and place it in the center area.</p>\n",
        "params": [
          {
            "type": "Ext.model.Model",
            "name": "deliveryrecord",
            "doc": "<p>A Delivery record.</p>\n\n<p>Used by <a href=\"#/api/devilry.extjshelpers.assignmentgroup.DeliveryGrid\" rel=\"devilry.extjshelpers.assignmentgroup.DeliveryGrid\" class=\"docClass\">devilry.extjshelpers.assignmentgroup.DeliveryGrid</a> and\ninternally in this class.</p>\n",
            "optional": false
          }
        ],
        "return": {
          "type": "void",
          "doc": "\n"
        },
        "private": false,
        "protected": false,
        "static": false,
        "inheritable": false,
        "deprecated": null,
        "alias": null,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/AssignmentGroupOverview.js",
        "linenr": 152,
        "html_filename": "AssignmentGroupOverview.html",
        "href": "AssignmentGroupOverview.html#devilry-extjshelpers-assignmentgroup-AssignmentGroupOverview-method-setDelivery",
        "shortDoc": "Create a devilry.extjshelpers.assignmentgroup.DeliveryInfo\ncontaining the given delivery and place it in the center a..."
      }
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
  "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/assignmentgroup/AssignmentGroupOverview.js",
  "linenr": 1,
  "html_filename": "AssignmentGroupOverview.html",
  "href": "AssignmentGroupOverview.html#devilry-extjshelpers-assignmentgroup-AssignmentGroupOverview",
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