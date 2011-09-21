Ext.data.JsonP.devilry_administrator_AdministratorSearchWidget({
  "mixedInto": [

  ],
  "href": "AdministratorSearchWidget.html#devilry-administrator-AdministratorSearchWidget",
  "allMixins": [

  ],
  "doc": "<p>SearchWidget used in every page in the entire administrator interface.</p>\n\n<p>Enables users to search for everything (like the dashboard) or just within\nthe current item.</p>\n",
  "singleton": false,
  "html_filename": "AdministratorSearchWidget.html",
  "code_type": "ext_define",
  "subclasses": [

  ],
  "superclasses": [
    "devilry.extjshelpers.searchwidget.SearchWidget"
  ],
  "protected": false,
  "tagname": "class",
  "mixins": [

  ],
  "members": {
    "cfg": [
      {
        "type": "String",
        "href": "AdministratorSearchWidget.html#devilry-administrator-AdministratorSearchWidget-cfg-assignmentRowTpl",
        "owner": "devilry.administrator.AdministratorSearchWidget",
        "doc": "<p><code>Ext.XTemplate</code> for Assignment rows.</p>\n",
        "html_filename": "AdministratorSearchWidget.html",
        "protected": false,
        "tagname": "cfg",
        "static": false,
        "private": false,
        "inheritable": false,
        "alias": null,
        "name": "assignmentRowTpl",
        "linenr": 37,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/administrator/static/extjs_classes/administrator/AdministratorSearchWidget.js",
        "deprecated": null
      },
      {
        "type": "String",
        "href": "AdministratorSearchWidget.html#devilry-administrator-AdministratorSearchWidget-cfg-assignmentgroupRowTpl",
        "owner": "devilry.administrator.AdministratorSearchWidget",
        "doc": "<p><code>Ext.XTemplate</code> for AssignmentGroup rows.</p>\n",
        "html_filename": "AdministratorSearchWidget.html",
        "protected": false,
        "tagname": "cfg",
        "static": false,
        "private": false,
        "inheritable": false,
        "alias": null,
        "name": "assignmentgroupRowTpl",
        "linenr": 43,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/administrator/static/extjs_classes/administrator/AdministratorSearchWidget.js",
        "deprecated": null
      },
      {
        "type": "String",
        "href": "AdministratorSearchWidget.html#devilry-administrator-AdministratorSearchWidget-cfg-deliveryRowTpl",
        "owner": "devilry.administrator.AdministratorSearchWidget",
        "doc": "<p><code>Ext.XTemplate</code> for Delivery rows.</p>\n",
        "html_filename": "AdministratorSearchWidget.html",
        "protected": false,
        "tagname": "cfg",
        "static": false,
        "private": false,
        "inheritable": false,
        "alias": null,
        "name": "deliveryRowTpl",
        "linenr": 49,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/administrator/static/extjs_classes/administrator/AdministratorSearchWidget.js",
        "deprecated": null
      },
      {
        "type": "String",
        "href": "AdministratorSearchWidget.html#devilry-administrator-AdministratorSearchWidget-cfg-nodeRowTpl",
        "owner": "devilry.administrator.AdministratorSearchWidget",
        "doc": "<p><code>Ext.XTemplate</code> for Node rows.</p>\n",
        "html_filename": "AdministratorSearchWidget.html",
        "protected": false,
        "tagname": "cfg",
        "static": false,
        "private": false,
        "inheritable": false,
        "alias": null,
        "name": "nodeRowTpl",
        "linenr": 19,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/administrator/static/extjs_classes/administrator/AdministratorSearchWidget.js",
        "deprecated": null
      },
      {
        "type": "String",
        "href": "AdministratorSearchWidget.html#devilry-administrator-AdministratorSearchWidget-cfg-periodRowTpl",
        "owner": "devilry.administrator.AdministratorSearchWidget",
        "doc": "<p><code>Ext.XTemplate</code> for Period rows.</p>\n",
        "html_filename": "AdministratorSearchWidget.html",
        "protected": false,
        "tagname": "cfg",
        "static": false,
        "private": false,
        "inheritable": false,
        "alias": null,
        "name": "periodRowTpl",
        "linenr": 31,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/administrator/static/extjs_classes/administrator/AdministratorSearchWidget.js",
        "deprecated": null
      },
      {
        "type": "Object",
        "href": "SearchWidget.html#devilry-extjshelpers-searchwidget-SearchWidget-cfg-searchResultItems",
        "owner": "devilry.extjshelpers.searchwidget.SearchWidget",
        "doc": "<p>The <a href=\"#/api/devilry.extjshelpers.searchwidget.SearchResults\" rel=\"devilry.extjshelpers.searchwidget.SearchResults\" class=\"docClass\">devilry.extjshelpers.searchwidget.SearchResults</a>, use\nwhen searching.</p>\n",
        "html_filename": "SearchWidget.html",
        "protected": false,
        "tagname": "cfg",
        "static": false,
        "private": false,
        "inheritable": false,
        "alias": null,
        "name": "searchResultItems",
        "linenr": 34,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/searchwidget/SearchWidget.js",
        "deprecated": null
      },
      {
        "type": "String",
        "href": "AdministratorSearchWidget.html#devilry-administrator-AdministratorSearchWidget-cfg-subjectRowTpl",
        "owner": "devilry.administrator.AdministratorSearchWidget",
        "doc": "<p><code>Ext.XTemplate</code> for Subject rows.</p>\n",
        "html_filename": "AdministratorSearchWidget.html",
        "protected": false,
        "tagname": "cfg",
        "static": false,
        "private": false,
        "inheritable": false,
        "alias": null,
        "name": "subjectRowTpl",
        "linenr": 25,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/administrator/static/extjs_classes/administrator/AdministratorSearchWidget.js",
        "deprecated": null
      },
      {
        "type": "String",
        "href": "AdministratorSearchWidget.html#devilry-administrator-AdministratorSearchWidget-cfg-urlPrefix",
        "owner": "devilry.administrator.AdministratorSearchWidget",
        "doc": "<p>Url prefix. Should be the absolute URL path to /administrator/.</p>\n",
        "html_filename": "AdministratorSearchWidget.html",
        "protected": false,
        "tagname": "cfg",
        "static": false,
        "private": false,
        "inheritable": false,
        "alias": null,
        "name": "urlPrefix",
        "shortDoc": "Url prefix. ...",
        "linenr": 13,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/administrator/static/extjs_classes/administrator/AdministratorSearchWidget.js",
        "deprecated": null
      }
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
  "name": "devilry.administrator.AdministratorSearchWidget",
  "linenr": 1,
  "xtypes": [

  ],
  "component": false,
  "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/administrator/static/extjs_classes/administrator/AdministratorSearchWidget.js",
  "deprecated": null,
  "extends": "devilry.extjshelpers.searchwidget.SearchWidget",
  "docauthor": null
});