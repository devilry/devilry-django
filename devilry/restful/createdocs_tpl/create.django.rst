Create a {{doc.model_verbose_name}}.

The underlying data model where the item is created is defined in :class:`{{doc.modelclspath}}`.


Request example
################

.. code-block:: javascript

    {{doc.httpmethod}} {{doc.itemexampleurl}}

    {
        {% for info in doc.editablefields %}{{ info.fieldname }}: {{info.valueexample|safe}}{% if not forloop.last %},
        {% endif %}{% endfor %}
    }


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
