Retrieve a {{doc.model_verbose_name}}.

The underlying data model where the item is retrieved from is defined in
:class:`{{doc.modelclspath}}`.
The :ref:`simplified` that the server forwards this request to is
:meth:`{{doc.simplifiedclspath}}.read`.


********
Request
********


Example
################

.. code-block:: javascript

    {{doc.httpmethod}} {{doc.itemexampleurl}}

{% if doc.result_fieldgroups %}

Another example, this one uses the optional *result_fieldgroups* parameter.

.. code-block:: javascript

    {{doc.httpmethod}} {{doc.itemexampleurl}}

    {
        result_fieldgroups: {{ doc.result_fieldgroups_example|safe }}
    }
{% endif %}

Required request parameters encoded in the URL
##############################################

id
--------------

The unique identifier of a {{doc.model_verbose_name}}. You will typically get
this id in response from a search.

{% if doc.result_fieldgroups %}

Optional request parameters
###########################

Optional request parameters are encoded as a JSON object and sent as the
request body as shown in the example above.

result_fieldgroups
------------------
A list of group names. Each group adds an additional set of fields to the
resulting data. The following group names are available:
{% for fieldgroup in doc.result_fieldgroups %}
    {{ fieldgroup.fieldgroup }}
        *Expands to the following fields:*
        {% for info in fieldgroup.fieldinfolist %}
            {{ info.fieldname }}
                Actual location of the field:
                    :class:`{{info.modelclspath}}`
                About the field:
                    {{ info.help_text|safe }}
                Type
                    {{ info.fieldtype }}
        {% endfor %}
{% endfor %}
{% endif %}



**************
Response
**************

On success
##########

Example
-------

.. code-block:: javascript

    200 OK

    {
        {% for info in doc.resultfields %}{{ info.fieldname }}: {{info.valueexample|safe}}{% if not forloop.last %},
        {% endif %}{% endfor %}
    }

Success response details
------------------------

As long as the {{doc.model_verbose_name}} is deleted without an error, the
response is *HTTP 200* with the requested data in the body.
The result always contains the following fields:

    {% for info in doc.resultfields %}
        {{ info.fieldname }}
            Actual location of the field:
                :class:`{{info.modelclspath}}`
            About the field:
                {{ info.help_text|safe }}
            Type
                {{ info.fieldtype }}
    {% endfor %}

{% if doc.result_fieldgroups %}
However, there may be more fields if specified with the ``result_fieldgroups``
request parameter.
{% endif %}



On error
########

On errors, we respond with one of the :ref:`restful_api_error_statuscodes`.
