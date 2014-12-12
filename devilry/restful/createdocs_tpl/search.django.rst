Search for {{doc.model_verbose_name_plural}}.

The underlying data model searched is defined in :class:`{{doc.modelclspath}}`.
The :ref:`simplified` that the server forwards this request to is
:meth:`{{doc.simplifiedclspath}}.search`.

The request parameters (below) all modify the result of the search. They are
applied in the following order:

    1. The ``query`` is executed.
    2. The result of the query is filtered through the ``filters``.
    3. The result of the filtering is ordered as specified in ``orderby``.
    4. The result of the ordering is limited by ``start`` and ``limit``.


**************************
Request
**************************

Request example
###############

.. code-block:: javascript

    {{doc.httpmethod}} {{doc.itemexampleurl}}

    {
        query: 'a query string',
        filters: {{ doc.filterexample_for_overview|safe }},
        orderby: {{ doc.orderby_example|safe }},
        start: 10,
        limit: 100
    }



Optional request parameters
###########################

Optional request parameters are encoded as a JSON object and sent as the
request body as shown in the example above.

query
-----
A string to search for. If this is empty or not given, all
{{doc.model_verbose_name_plural}} that the authenticated user has access to is
returned.

If the string is not empty, the ``query``-string is split on whitespace,
resulting in a list of words. Every *word* in the list is searched for
*case-insensitive* matches within the following fields:

    {% for info in doc.searchfields %}
        {{ info.fieldname }}
            Actual location of the field:
                :class:`{{info.modelclspath}}`
            About the field:
                {{ info.help_text|safe }}
            Type
                {{ info.fieldtype }}
    {% endfor %}



{% if doc.filters %}

filters
-------

Filters can be used to perform complex queries. The ``filters`` parameter is a
list of filters, where each filter is a map with the following entries:

    field
        A field name.
    comp
        A comparison operator.
    value
        The value to filter on.

Example:

    .. code-block:: javascript

{{ doc.filterexample|safe }}

{{doc.model_verbose_name_plural}} can be filtered on the following *fields*:
{% if doc.filters.filterspecs %}
{% for fs in doc.filterspecs %}
    {{ fs.filterspec.fieldname }}
        Actual location of the field:
            :class:`{{fs.modelclspath}}`
        About the field:
            {{ fs.help_text|safe }}
        Type
            {{ fs.fieldtype }}
        Supported comparison operators:
            {%for comp in fs.filterspec.supported_comp%}``{{comp|safe}}``{%if not forloop.last%}, {%endif%}{%endfor%}.
{% endfor %}
{% endif %}
{% if doc.filters.patternfilterspecs %}
    Filters matching the following python compatible regular expressions:
    {% for filterspec in doc.patternfilterspecs %}
        ``{{ filterspec.fieldname }}``
            Supported comparison operators:
            {%for comp in filterspec.supported_comp%}``{{comp|safe}}``{%if not forloop.last%}, {%endif%}{%endfor%}.
    {% endfor %}
{% endif %}

{%endif%}


exact_number_of_results
-----------------------
If given, this must be a positive integer (including 0), which specifies the exact number of
expected results. This enables searches that you know should fail if they do not get this
exact number of results, such as filtering for a User by unique username
instead of its numeric ID (where you should expect exactly one result).


orderby
-------
List of fieldnames. Order the result by these fields.
Fieldnames can be prefixed by ``'-'`` for descending ordering.

start
-----
After query, filters and orderby have been executed, the result is limited to
the values from *start* to *start+limit*. Start defalts to ``0``.

limit
-----
Limit results to this number of items. Defaults to ``50``.

{% if doc.result_fieldgroups %}
result_fieldgroups
------------------
A list of group names. Each group adds an additional set of fields to the
results of the search. The following group names are available:
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



{% if doc.search_fieldgroups %}
search_fieldgroups
------------------
A list of group names. Each group adds an additional set of fields to be
searched using the ``query``. The following group names are available:
{% for fieldgroup in doc.search_fieldgroups %}
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




*********************
Response
*********************

On success
##########


Example
------------------------

*note that the is wrong in the example. The id is always unique. However, the
example is generated from a non-varying dataset.*

.. code-block:: javascript

    200 OK

    {
        total: 20,
        items: [
            { {% for info in doc.resultfields %}{{ info.fieldname }}: {{info.valueexample|safe}}{% if not forloop.last %},
              {% endif %}{% endfor %} },
            { {% for info in doc.resultfields %}{{ info.fieldname }}: {{info.valueexample|safe}}{% if not forloop.last %},
              {% endif %}{% endfor %} },
            ...
        ]
    }


Success response details
------------------------

Responds with HTTP code *200* and a *JSON encoded* dict containing the list of
results and the *total* number of items found before applying ``limit`` and
``start``. Each result in the
list is a JSON object where the *key* is a fieldname and the associated value is
the *value* for that field. The result always contains the following fields:

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
