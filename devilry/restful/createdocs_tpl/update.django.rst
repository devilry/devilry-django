Update a {{doc.model_verbose_name}}.

The underlying data model where the item is updated is defined in :class:`{{doc.modelclspath}}`.


Request example
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
