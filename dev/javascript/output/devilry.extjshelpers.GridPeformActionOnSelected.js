Ext.data.JsonP.devilry_extjshelpers_GridPeformActionOnSelected({
  "mixedInto": [

  ],
  "href": "GridPeformActionOnSelected.html#devilry-extjshelpers-GridPeformActionOnSelected",
  "allMixins": [

  ],
  "doc": "<p>A mixin to perform an action each selected item in a grid, including grids using paging.</p>\n",
  "singleton": false,
  "html_filename": "GridPeformActionOnSelected.html",
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

    ],
    "event": [

    ],
    "property": [

    ],
    "method": [
      {
        "href": "GridPeformActionOnSelected.html#devilry-extjshelpers-GridPeformActionOnSelected-method-gatherSelectedRecordsInArray",
        "owner": "devilry.extjshelpers.GridPeformActionOnSelected",
        "params": [
          {
            "type": "Object",
            "doc": "<p>An object with the following attributes:</p>\n\n<pre><code> callback\n     A callback function that is called for each record in the\n     store. The callback gets the array as argument.\n scope\n     The scope to execute `callback` in.\n extraArgs\n     Array of extra arguments to callback.\n</code></pre>\n",
            "optional": false,
            "name": "action"
          }
        ],
        "doc": "<p>Gather all selected records in an array. This array is forwarded to the action specified as parameter.</p>\n",
        "html_filename": "GridPeformActionOnSelected.html",
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
        "name": "gatherSelectedRecordsInArray",
        "shortDoc": "Gather all selected records in an array. ...",
        "linenr": 64,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/GridPeformActionOnSelected.js",
        "deprecated": null
      },
      {
        "href": "GridPeformActionOnSelected.html#devilry-extjshelpers-GridPeformActionOnSelected-method-performActionOnAll",
        "owner": "devilry.extjshelpers.GridPeformActionOnSelected",
        "params": [
          {
            "type": "Object",
            "doc": "<p>An object with the following attributes:</p>\n\n<pre><code> callback\n     A callback function that is called for each record in the\n     store. The callback gets the folling arguments: `(record,\n     index, total)`. Index is the index of the record starting with\n     1, and total is the total number of records.\n scope\n     The scope to execute `callback` in.\n extraArgs\n     Array of extra arguments to callback.\n</code></pre>\n",
            "optional": false,
            "name": "action"
          }
        ],
        "doc": "<p>Call the given action on each item in the store (on all pages in the store).</p>\n",
        "html_filename": "GridPeformActionOnSelected.html",
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
        "name": "performActionOnAll",
        "shortDoc": "Call the given action on each item in the store (on all pages in the store). ...",
        "linenr": 40,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/GridPeformActionOnSelected.js",
        "deprecated": null
      },
      {
        "href": "GridPeformActionOnSelected.html#devilry-extjshelpers-GridPeformActionOnSelected-method-performActionOnSelected",
        "owner": "devilry.extjshelpers.GridPeformActionOnSelected",
        "params": [
          {
            "type": "Object",
            "doc": "<p>See <a href=\"#/api/devilry.extjshelpers.GridPeformActionOnSelected-method-performActionOnAll\" rel=\"devilry.extjshelpers.GridPeformActionOnSelected-method-performActionOnAll\" class=\"docClass\">performActionOnAll</a>.</p>\n",
            "optional": false,
            "name": "action"
          }
        ],
        "doc": "<p>Call the given action on each selected item. If all items on the current page is selected,\na MessageBox will be shown to the user where they can choose to call the action on all items\ninstead of just the ones on the current page.</p>\n",
        "html_filename": "GridPeformActionOnSelected.html",
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
        "name": "performActionOnSelected",
        "shortDoc": "Call the given action on each selected item. ...",
        "linenr": 5,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/GridPeformActionOnSelected.js",
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
  "name": "devilry.extjshelpers.GridPeformActionOnSelected",
  "linenr": 1,
  "xtypes": [

  ],
  "component": false,
  "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/GridPeformActionOnSelected.js",
  "deprecated": null,
  "extends": "Ext.Base",
  "docauthor": null
});