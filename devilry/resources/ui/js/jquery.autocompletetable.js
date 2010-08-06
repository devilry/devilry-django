// vim: set ts=4 sts=4 et sw=4:

jQuery.autocompletetable = {
    refreshtable: function(searchfield, showall_label, headings,
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
                    $("<button></button>")
                        .html(showall_label + " (" + data.allcount + ")")
                        .button();
                searchfield.after(showallbutton);
                showallbutton.click(function(e) {
                    var term = searchfield.val();
                    jQuery.autocompletetable.refreshtable(searchfield, showall_label,
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


jQuery.fn.autocompletetable = function(jsonurl, headings, editlabel,
        showall_label, args) {

    return this.each(function(){
        var form = $("<form></form>")
            .attr("method", "post")
            .attr("action", '#') //.attr("action", deleteurl)
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
        jQuery.autocompletetable.refreshtable(searchfield, showall_label,
            headings, editlabel, jsonurl, "", "no");

        // Add buttonbar
        var buttonbar = $("<div></div>")
            .addClass("autocompletetable-buttonbar")
            .appendTo(this);

        if(args.buttons) {
            // Create buttons
            $.each(args.buttons, function(key, button) {
                //$.log("button:: key: " + key
                    //+ " label:" + button.label
                    //+ " confirmtitle:" + button.confirmtitle
                    //+ " confirmlabel:" + button.confirmlabel
                    //+ " cancel_label:" + button.cancel_label
                    //+ " confirm_message:" + button.confirm_message
                    //+ " url:" + button.url);
                var htmlbutton = $("<button></button>")
                    .html(button.label)
                    .button()
                    .appendTo(buttonbar);
                if(button.classes) {
                    $.each(button.classes, function(i, cls) {
                        htmlbutton.addClass(cls);
                    });
                }

                // Create confirm delete dialog
                var confirmbuttons = {}
                confirmbuttons[button.confirmlabel] = function() {
                    form.attr("action", button.url);
                    form.submit();
                };
                confirmbuttons[button.cancel_label] = function() {
                    $(this).dialog('close');
                };
                var confirmdialog = $('<div>' + button.confirm_message + '</div>')
                    .dialog({
                        autoOpen: false,
                        title: button.confirmtitle,
                        modal: true,
                        buttons: confirmbuttons
                    });

                // Open confirm-delete dialog when delete button is clicked.
                htmlbutton.click(function() {
                    confirmdialog.dialog('open');
                    return false;
                });
            });
        }

        if(args.links) {
            // Create links
            $.each(args.links, function(key, link) {
                var html_link = $("<a></a>").html(link.label)
                    .attr("href", link.url)
                    .button()
                    .appendTo(buttonbar);
                if(link.classes) {
                    $.each(link.classes, function(i, cls) {
                        html_link.addClass(cls);
                    });
                }
                //$.log("link:: key: " + key + " label:" + link.label + " url:" + link.url);
            });
        }

        // Search when at least 2 characters are in the searchfield, and reset
        // when searchfield is empty.
        searchfield.keyup(function(e) {
            if (e.ctrlKey || e.altKey || e.shiftKey || e.metaKey) {
                return;
            }
            var term = $(this).val();
            if(term.length > 1 || term.length == 0) {
                jQuery.autocompletetable.refreshtable(searchfield, showall_label,
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
