Ext.data.JsonP.devilry_extjshelpers_GridPeformActionOnSelected({
  "subclasses": [

  ],
  "doc": "<p>A mixin to perform an action each selected item in a grid, including grids using paging.</p>\n",
  "docauthor": null,
  "singleton": false,
  "html_filename": "GridPeformActionOnSelected.html",
  "href": "GridPeformActionOnSelected.html#devilry-extjshelpers-GridPeformActionOnSelected",
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
            "doc": "<p>An object with the following attributes:</p>\n\n<pre><code> callback\n     A callback function that is called for each record in the\n     store. The callback gets the folling arguments: `(record,\n     index, total)`. Index is the index of the record starting with\n     1, and total is the total number of records.\n scope\n     The scope to execute `callback` in.\n extraArgs\n     Array of extra arguments to callback.\n</code></pre>\n",
            "name": "action",
            "optional": false
          }
        ],
        "owner": "devilry.extjshelpers.GridPeformActionOnSelected",
        "doc": "<p>Call the given action on each item in the store (on all pages in the store).</p>\n",
        "html_filename": "GridPeformActionOnSelected.html",
        "href": "GridPeformActionOnSelected.html#devilry-extjshelpers-GridPeformActionOnSelected-method-performActionOnAll",
        "tagname": "method",
        "shortDoc": "Call the given action on each item in the store (on all pages in the store). ...",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 40,
        "inheritable": false,
        "alias": null,
        "name": "performActionOnAll",
        "return": {
          "type": "void",
          "doc": "\n"
        },
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/GridPeformActionOnSelected.js",
        "deprecated": null
      },
      {
        "params": [
          {
            "type": "Object",
            "doc": "<p>See <a href=\"#/api/devilry.extjshelpers.GridPeformActionOnSelected-method-performActionOnAll\" rel=\"devilry.extjshelpers.GridPeformActionOnSelected-method-performActionOnAll\" class=\"docClass\">performActionOnAll</a>.</p>\n",
            "name": "action",
            "optional": false
          }
        ],
        "owner": "devilry.extjshelpers.GridPeformActionOnSelected",
        "doc": "<p>Call the given action on each selected item. If all items on the current page is selected,\na MessageBox will be shown to the user where they can choose to call the action on all items\ninstead of just the ones on the current page.</p>\n",
        "html_filename": "GridPeformActionOnSelected.html",
        "href": "GridPeformActionOnSelected.html#devilry-extjshelpers-GridPeformActionOnSelected-method-performActionOnSelected",
        "tagname": "method",
        "shortDoc": "Call the given action on each selected item. ...",
        "protected": false,
        "static": false,
        "private": false,
        "linenr": 5,
        "inheritable": false,
        "alias": null,
        "name": "performActionOnSelected",
        "return": {
          "type": "void",
          "doc": "\n"
        },
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/GridPeformActionOnSelected.js",
        "deprecated": null
      }
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
  "name": "devilry.extjshelpers.GridPeformActionOnSelected",
  "xtypes": [

  ],
  "extends": "Ext.Base",
  "allMixins": [

  ],
  "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/GridPeformActionOnSelected.js",
  "deprecated": null
});