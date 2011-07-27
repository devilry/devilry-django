Ext.data.JsonP.devilry_administrator_AdministratorSearchWidget({
  "subclasses": [

  ],
  "doc": "<p>SearchWidget used in every page in the entire administrator interface.</p>\n\n<p>Enables users to search for everything (like the dashboard) or just within\nthe current item.</p>\n",
  "docauthor": null,
  "singleton": false,
  "html_filename": "AdministratorSearchWidget.html",
  "href": "AdministratorSearchWidget.html#devilry-administrator-AdministratorSearchWidget",
  "code_type": "ext_define",
  "superclasses": [
    "devilry.extjshelpers.searchwidget.SearchWidget"
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
        "type": "String",
        "owner": "devilry.administrator.AdministratorSearchWidget",
        "doc": "<p><code>Ext.XTemplate</code> for Assignment rows.</p>\n",
        "html_filename": "AdministratorSearchWidget.html",
        "href": "AdministratorSearchWidget.html#devilry-administrator-AdministratorSearchWidget-cfg-assignmentRowTpl",
        "tagname": "cfg",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 37,
        "inheritable": false,
        "alias": null,
        "name": "assignmentRowTpl",
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/administrator/static/extjs_classes/administrator/AdministratorSearchWidget.js",
        "deprecated": null
      },
      {
        "type": "String",
        "owner": "devilry.administrator.AdministratorSearchWidget",
        "doc": "<p><code>Ext.XTemplate</code> for AssignmentGroup rows.</p>\n",
        "html_filename": "AdministratorSearchWidget.html",
        "href": "AdministratorSearchWidget.html#devilry-administrator-AdministratorSearchWidget-cfg-assignmentgroupRowTpl",
        "tagname": "cfg",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 43,
        "inheritable": false,
        "alias": null,
        "name": "assignmentgroupRowTpl",
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/administrator/static/extjs_classes/administrator/AdministratorSearchWidget.js",
        "deprecated": null
      },
      {
        "type": "String",
        "owner": "devilry.administrator.AdministratorSearchWidget",
        "doc": "<p><code>Ext.XTemplate</code> for Delivery rows.</p>\n",
        "html_filename": "AdministratorSearchWidget.html",
        "href": "AdministratorSearchWidget.html#devilry-administrator-AdministratorSearchWidget-cfg-deliveryRowTpl",
        "tagname": "cfg",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 49,
        "inheritable": false,
        "alias": null,
        "name": "deliveryRowTpl",
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/administrator/static/extjs_classes/administrator/AdministratorSearchWidget.js",
        "deprecated": null
      },
      {
        "type": "String",
        "owner": "devilry.administrator.AdministratorSearchWidget",
        "doc": "<p><code>Ext.XTemplate</code> for Node rows.</p>\n",
        "html_filename": "AdministratorSearchWidget.html",
        "href": "AdministratorSearchWidget.html#devilry-administrator-AdministratorSearchWidget-cfg-nodeRowTpl",
        "tagname": "cfg",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 19,
        "inheritable": false,
        "alias": null,
        "name": "nodeRowTpl",
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/administrator/static/extjs_classes/administrator/AdministratorSearchWidget.js",
        "deprecated": null
      },
      {
        "type": "String",
        "owner": "devilry.administrator.AdministratorSearchWidget",
        "doc": "<p><code>Ext.XTemplate</code> for Period rows.</p>\n",
        "html_filename": "AdministratorSearchWidget.html",
        "href": "AdministratorSearchWidget.html#devilry-administrator-AdministratorSearchWidget-cfg-periodRowTpl",
        "tagname": "cfg",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 31,
        "inheritable": false,
        "alias": null,
        "name": "periodRowTpl",
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/administrator/static/extjs_classes/administrator/AdministratorSearchWidget.js",
        "deprecated": null
      },
      {
        "type": "Object",
        "owner": "devilry.extjshelpers.searchwidget.SearchWidget",
        "doc": "<p>The <a href=\"#/api/devilry.extjshelpers.searchwidget.SearchResults\" rel=\"devilry.extjshelpers.searchwidget.SearchResults\" class=\"docClass\">devilry.extjshelpers.searchwidget.SearchResults</a>, use\nwhen searching.</p>\n",
        "html_filename": "SearchWidget.html",
        "href": "SearchWidget.html#devilry-extjshelpers-searchwidget-SearchWidget-cfg-searchResultItems",
        "tagname": "cfg",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 34,
        "inheritable": false,
        "alias": null,
        "name": "searchResultItems",
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/searchwidget/SearchWidget.js",
        "deprecated": null
      },
      {
        "type": "String",
        "owner": "devilry.administrator.AdministratorSearchWidget",
        "doc": "<p><code>Ext.XTemplate</code> for Subject rows.</p>\n",
        "html_filename": "AdministratorSearchWidget.html",
        "href": "AdministratorSearchWidget.html#devilry-administrator-AdministratorSearchWidget-cfg-subjectRowTpl",
        "tagname": "cfg",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 25,
        "inheritable": false,
        "alias": null,
        "name": "subjectRowTpl",
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/administrator/static/extjs_classes/administrator/AdministratorSearchWidget.js",
        "deprecated": null
      },
      {
        "type": "String",
        "owner": "devilry.administrator.AdministratorSearchWidget",
        "doc": "<p>Url prefix. Should be the absolute URL path to /administrator/.</p>\n",
        "html_filename": "AdministratorSearchWidget.html",
        "href": "AdministratorSearchWidget.html#devilry-administrator-AdministratorSearchWidget-cfg-urlPrefix",
        "tagname": "cfg",
        "shortDoc": "Url prefix. ...",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 13,
        "inheritable": false,
        "alias": null,
        "name": "urlPrefix",
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/administrator/static/extjs_classes/administrator/AdministratorSearchWidget.js",
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
  "name": "devilry.administrator.AdministratorSearchWidget",
  "xtypes": [

  ],
  "extends": "devilry.extjshelpers.searchwidget.SearchWidget",
  "allMixins": [

  ],
  "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/administrator/static/extjs_classes/administrator/AdministratorSearchWidget.js",
  "deprecated": null
});