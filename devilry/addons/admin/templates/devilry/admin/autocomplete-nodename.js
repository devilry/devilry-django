{% comment %} vim: set ts=4 sts=4 et sw=4: {% endcomment %}
{% load i18n %}

$(function() {
    $("#autocomplete-{{ clsname }}").autocompletetable(
        "{{ jsonurl }}",
        [{% for h in headings %}"{{ h }}",{% endfor %}],
        "{% trans "edit" %}", "{% trans "Show all" %}",
        {
          links: {
            createnew: {
              label: "{% trans "Create new" %}",
              url: "{{ createurl }}"
            }
          },
          buttons: {
            deleteselected: {
              label: "{% trans "Delete selected" %}",
              classes: ['delete'],
              confirmtitle: "{% trans "Confirm delete" %}",
              confirmlabel: "{% trans "Confirm delete" %}",
              cancel_label: "{% trans "Cancel" %}",
              confirm_message: "{{ deletemessage }}",
              classes: ['delete'],
              url: "{{ deleteurl }}"
            }
          }
        })
});
