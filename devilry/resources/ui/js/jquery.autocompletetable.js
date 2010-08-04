// vim: set ts=4 sts=4 et sw=4:

jQuery.autocompletetable = {
    fill: function(searchfield, showall_label, headings,
                  editlabel, jsonurl, term, showall) {
        var tbl = $("<table></table>")
            .addClass("autocompletetable-result")
            .addClass("horizontal_ordered_table");
        var headrow = $("<tr></tr>");
        $("<th>&nbsp;</th>").appendTo(headrow);
        $.each(headings, function(i, heading) {
            $("<th>" + heading + "</th>").appendTo(headrow);
        });
        $("<th>&nbsp;</th>").appendTo(headrow);
        $("<thead></thead>").append(headrow).appendTo(tbl);
        var result = $("<tbody></tbody>").appendTo(tbl);
        var idprefix = searchfield.parent().attr("id") + "-";

        $.getJSON(jsonurl, {"term": term, "all": showall}, function(data) {
            $.each(data.result, function(i, item) {
                var id = idprefix + i;
                var tr = $("<tr></tr>");
                $("<td></td>")
                    .append($("<input />").attr("type", "checkbox").attr("id", id))
                .appendTo(tr);
                $.each(item.path, function(index, part) {
                    var p = part.replace(term,
                            "<strong>" + term + "</strong>");
                    $("<td></td>")
                        .append($("<label>" + p + "</label>").attr("for", id))
                    .appendTo(tr);
                });
                $("<td></td>").append($("<a>" + editlabel + "</a>")
                    .attr("href", item.editurl))
                .appendTo(tr);
                tr.appendTo(result);
            });

            searchfield.next("button").remove();
            if(data.allcount > data.result.length) {
                var showallbutton =
                    $("<button>" + showall_label + " (" + data.allcount + ")</button>")
                    .attr("class", "button").button();
                searchfield.after(showallbutton);
                showallbutton.click(function(e) {
                    var term = searchfield.val();
                    jQuery.autocompletetable.fill(searchfield, showall_label,
                        headings, editlabel, jsonurl, term, "yes");
                });
            }
        });

        if(searchfield.parent().children("table").length == 0) {
            searchfield.parent().append(tbl);
        } else {
            searchfield.parent().children("table").first().replaceWith(tbl);
        }
    },
}


jQuery.fn.autocompletetable = function(jsonurl, editlabel, headings, showall_label,
        createlabel, createurl) {
    return this.each(function(){
        var searchfieldid = $(this).attr("id") + "-searchfield";
        $("<label>Filter: </label>")
            .addClass("autocompletetable-filterlabel")
            .attr("for", searchfieldid)
            .appendTo(this);
        var searchfield =
            $("<input />")
                .attr("id", searchfieldid)
                .addClass("autocompletetable-searchfield")
                .addClass("ui-widget")
                .addClass("ui-widget-content")
                .addClass("ui-corner-all")
            .appendTo(this);

        // Initialize with default search results
        jQuery.autocompletetable.fill(searchfield, showall_label,
            headings, editlabel, jsonurl, "", "no");

        // Add buttonbar
        var buttonbar = $("<div></div>").attr("class", "autocompletetable-buttonbar")
            .appendTo(this);
        $("<a>" + createlabel + "</a>").attr('href', createurl).button()
            .appendTo(buttonbar);

        // Search when at least 2 characters are in the searchfield, and reset
        // when searchfield is empty.
        searchfield.keyup(function(e) {
            if (e.ctrlKey || e.altKey || e.shiftKey || e.metaKey) {
                return;
            }
            var term = $(this).val();
            if(term.length > 1 || term.length == 0) {
                jQuery.autocompletetable.fill(searchfield, showall_label,
                    headings, editlabel, jsonurl, term, "no");
            }
        });
    });
};
jQuery.log = function(message) {
    if(window.console) {
        console.debug(message);
    } else {
        alert(message);
    }
};
