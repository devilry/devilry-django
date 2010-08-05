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
        var idprefix = searchfield.parent().parent().attr("id") + "-cb";

        $.getJSON(jsonurl, {"term": term, "all": showall}, function(data) {
            $.each(data.result, function(i, item) {
                var id = idprefix + "-" + i;
                var tr = $("<tr></tr>");
                $("<td></td>")
                    .append($("<input />")
                        .attr("type", "checkbox")
                        .attr("value", item.id)
                        .attr("id", id)
                        .attr("name", id))
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
                    return false;
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


jQuery.fn.autocompletetable = function(jsonurl, editlabel, headings,
        showall_label, createlabel, createurl,
        deletelabel, deletetitle, deletemessage, deleteurl,
        cancel_label) {

    return this.each(function(){
        var form = $("<form></form>")
            .attr("method", "post")
            .attr("action", deleteurl)
            .appendTo(this);

        var searchfieldid = $(this).attr("id") + "-searchfield";
        $("<label>Filter: </label>")
            .addClass("autocompletetable-filterlabel")
            .attr("for", searchfieldid)
            .appendTo(form);
        var searchfield =
            $("<input />")
                .attr("id", searchfieldid)
                .addClass("autocompletetable-searchfield")
                .addClass("ui-widget")
                .addClass("ui-widget-content")
                .addClass("ui-corner-all")
            .appendTo(form);

        // Initialize with default search results
        jQuery.autocompletetable.fill(searchfield, showall_label,
            headings, editlabel, jsonurl, "", "no");

        // Add buttonbar
        var buttonbar = $("<div></div>")
            .addClass("autocompletetable-buttonbar")
            .appendTo(this);
        var deletebutton = $("<button></button>")
            .html(deletelabel)
            .button()
            .addClass("delete")
            .appendTo(buttonbar);
        $("<a>" + createlabel + "</a>").button()
            .attr("href", createurl)
            .appendTo(buttonbar);

        // Create confirm delete dialog
        var confirmdelete_buttons = {}
        confirmdelete_buttons[deletelabel] = function() {
            form.submit();
        };
        confirmdelete_buttons[cancel_label] = function() {
            $(this).dialog('close');
        };
        var confirmdelete_dialog = $('<div></div>')
            .html(deletemessage)
            .dialog({
                autoOpen: false,
                title: deletetitle,
                modal: true,
                buttons: confirmdelete_buttons
            });

        // Open confirm-delete dialog when delete button is clicked.
        deletebutton.click(function() {
            confirmdelete_dialog.dialog('open');
            return false;
        });

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
