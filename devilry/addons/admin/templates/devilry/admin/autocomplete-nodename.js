{% comment %} vim: set ts=4 sts=4 et sw=4: {% endcomment %}

$(function() {
    $("#autocomplete-{{ clsname }}").keyup(function(e) {
        if (e.ctrlKey || e.altKey || e.shiftKey || e.metaKey) {
            return;
        }
        var value = $(this).val();
        var result = $("#autocomplete-{{ clsname }}-result");
        result.empty();
        if(value.length > 1 || value.length == 0) {
            $.getJSON('{{ jsonurl }}', {'term':value}, function(data) {
                $.each(data, function(i, item) {
                    var path = item.path.replace(value, "<strong>" + value + "</strong>");
                    $("<li></li>").append(
                        $("<a>" + path + "</a>")
                        .attr("href", item.editurl))
                    .appendTo(result);
                });
            });
        }
    });
});
