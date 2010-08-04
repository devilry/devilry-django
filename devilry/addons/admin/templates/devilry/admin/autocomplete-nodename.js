{% comment %} vim: set ts=4 sts=4 et sw=4: {% endcomment %}

$(function() {
    $("#autocomplete-{{ clsname }}name").keyup(function(e) {
        if (e.ctrlKey || e.altKey || e.shiftKey || e.metaKey) {
            return;
        }
        var value = $(this).val();
        var result = $("#autocomplete-{{ clsname }}name-result");
        result.empty();
        if(value.length > 1 || value.length == 0) {
            $.getJSON('{{ jsonurl }}', {'term':value}, function(data) {
                $.each(data, function(i, item) {
                    $("<li></li>").append(
                        $("<a>" + item.path + "</a>")
                        .attr("href", item.editurl))
                    .appendTo(result);
                });
            });
        }
    });
});
