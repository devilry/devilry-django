Update a {{doc.model_verbose_name}}.

The underlying data model where the item is updated is defined in
:class:`{{doc.modelclspath}}`.
The :ref:`simplified` that the server forwards this request to is
:meth:`{{doc.simplifiedclspath}}.update`.



********
Request
********


Example
################

.. code-block:: javascript

    {{doc.httpmethod}} {{doc.itemexampleurl}}

    {
        {% for info in doc.editablefields %}{{ info.fieldname }}: {{info.valueexample|safe}}{% if not forloop.last %},
        {% endif %}{% endfor %}
    }


Required request parameters encoded in the URL
##############################################

id
--------------

The unique identifier of a {{doc.model_verbose_name}} as the last item in the
URL. You will typically get this id in response from a search.


Required request parameters
###########################

The following request parameters are encoded as a JSON object and sent as the
request body as shown in the example above.

{% for info in doc.editablefields %}

{{ info.fieldname }}
--------------------------------------------------

Actual location of the field:
    :class:`{{info.modelclspath}}`
About the field:
    {{ info.help_text|safe }}
Type
    {{ info.fieldtype }}
{% endfor %}



**************
Response
**************

On success
##########

Example
----------------

.. code-block:: javascript

    200 OK

    {
        {% for info in doc.editablefields_and_id %}{{ info.fieldname }}: {{info.valueexample|safe}}{% if not forloop.last %},
        {% endif %}{% endfor %}
    }


Success response details
------------------------

As long as the {{doc.model_verbose_name}} is updated without an error, the
response is *HTTP 201* with the requested data in the body.  The result always
contains the data you sent in to the update method, however some values may
have been changed due to logic performed on the server before saving.



On error
########

On errors, we respond with one of the :ref:`restful_api_error_statuscodes`.
