Ext.data.JsonP.devilry_extjshelpers_RestProxy({
  "mixedInto": [

  ],
  "href": "RestProxy.html#devilry-extjshelpers-RestProxy",
  "allMixins": [

  ],
  "doc": "<p>REST proxy subclass which handles errors from <a href=\"#/api/devilry.extjshelpers.RestSubmit\" rel=\"devilry.extjshelpers.RestSubmit\" class=\"docClass\">devilry.extjshelpers.RestSubmit</a>.</p>\n\n<p>Since ExtJS for some reason goes into panic mode for any HTTP status\ncode except 200 (and ignores the response text), we need to override\nsetException in the REST proxy and manually decode the responseText.\n(<a href=\"http://www.sencha.com/forum/showthread.php?135143-RESTful-Model-How-to-indicate-that-the-PUT-operation-failed&amp;highlight=store+failure\">see this forum thread</a>)</p>\n\n<p>However how do we get this into the form when we do not have any link to the form?</p>\n\n<ul>\n<li>We add the response and the the decoded responsedata to the operation\nobject, which is available to onFailure in Submit.</li>\n</ul>\n\n\n<h1>Usage</h1>\n\n<p>First we need to use the proxy, for example in a <code>Ext.data.Model</code>:</p>\n\n<pre><code>Ext.define('MyModel', {{\n          extend: 'Ext.data.Model',\n          requires: ['devilry.extjshelpers.RestProxy'],\n          fields: [...],\n             proxy: Ext.create('devilry.extjshelpers.RestProxy', {\n              ...\n          }\n});\n</code></pre>\n\n<p>Then we can handle errors and access the error data as plain text or JSON.\nSee <a href=\"#/api/devilry.extjshelpers.RestProxy-method-setException\" rel=\"devilry.extjshelpers.RestProxy-method-setException\" class=\"docClass\">setException</a> for more details):</p>\n\n<pre><code>myform.getForm().doAction('devilryrestsubmit', {\n    submitEmptyText: true,\n    waitMsg: 'Saving item...',\n    success: function(form, action) {...},\n    failure: function(form, action) {\n        var errorraw = action.operation.responseText;\n        console.log(errorraw);\n        var errorjson = action.operation.responseData;\n        console.log(errorjson);\n    }\n});\n</code></pre>\n\n<h1>See also</h1>\n\n<p>This should be used with <a href=\"#/api/devilry.extjshelpers.RestSubmit\" rel=\"devilry.extjshelpers.RestSubmit\" class=\"docClass\">devilry.extjshelpers.RestSubmit</a>.</p>\n",
  "singleton": false,
  "html_filename": "RestProxy.html",
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
        "href": "RestProxy.html#devilry-extjshelpers-RestProxy-method-setException",
        "owner": "devilry.extjshelpers.RestProxy",
        "params": [
          {
            "type": "Object",
            "doc": "\n",
            "optional": false,
            "name": "operation"
          },
          {
            "type": "Object",
            "doc": "\n",
            "optional": false,
            "name": "response"
          }
        ],
        "doc": "<p>Overrides error handling. Adds error information to the <code>operation</code> parameter.</p>\n\n<p>The error data is added to:</p>\n\n<ul>\n<li><code>operation.responseText</code>: The data in the body of the HTTP response.</li>\n<li><code>operation.responseData</code>: If <code>responseText</code> can be decoded as JSON,\nthis contains the decoded JSON object.</li>\n</ul>\n\n",
        "html_filename": "RestProxy.html",
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
        "name": "setException",
        "shortDoc": "Overrides error handling. ...",
        "linenr": 70,
        "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/RestProxy.js",
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
  "name": "devilry.extjshelpers.RestProxy",
  "linenr": 1,
  "xtypes": [

  ],
  "component": false,
  "filename": "/Volumes/viktig/code/devilry-django/devilry/apps/extjshelpers/static/extjs_classes/extjshelpers/RestProxy.js",
  "deprecated": null,
  "extends": "Ext.data.proxy.Rest",
  "docauthor": null
});