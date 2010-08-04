{% comment %} vim: set ts=4 sts=4 et sw=4: {% endcomment %}
{% load i18n %}

$(function() {
    $("#autocomplete-{{ clsname }}").autocompletetable("{{ jsonurl }}", "edit",
        [{% for h in headings %}
            "{{ h }}",
        {% endfor %}],
        "{% trans "Show all" %}",
        "{% trans "Create new" %}", "{{ createurl }}");
});
