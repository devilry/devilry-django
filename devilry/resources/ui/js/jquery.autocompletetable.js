// vim: set ts=4 sts=4 et sw=4:

jQuery.autocompletetable = {
    refreshtable: function(properties, term, showall) {
        var tbl = $("<table></table>")
            .addClass("autocompletetable-result")
            .addClass("horizontal_ordered_table");
        var headrow = $("<tr></tr>");
        var checkall = $("<input/>")
            .attr("type", "checkbox");
        $("<th></th>")
            .append(checkall)
            .appendTo(headrow);
        $.each(properties.headings, function(i, heading) {
            $("<th>" + heading + "</th>").appendTo(headrow);
        });
        $("<th>&nbsp;</th>").appendTo(headrow);
        $("<thead></thead>").append(headrow).appendTo(tbl);
        var result = $("<tbody></tbody>").appendTo(tbl);
        var idprefix = properties.searchfield.parent().parent().attr("id") + "-cb";

        var postdata = {
            "term": properties.term,
            "all": properties.showall
        };
        if(properties.filters) {
            $.each(properties.filters, function(key, f) {
                postdata[key] = f.enabled?"yes": "";
            });
        }

        $.getJSON(properties.jsonurl, postdata, function(data) {
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
                    var terms = properties.term.split(" AND ");
                    var p = part;
                    $.each(terms, function(index, term) {
                        p = p.replace(term.trim(),
                                "<strong>" + term + "</strong>");
                    });
                    $("<td></td>")
                        .append($("<label>" + p + "</label>").attr("for", id))
                    .appendTo(tr);
                });
                $("<td></td>").append($("<a>" + properties.editlabel + "</a>")
                    .attr("href", item.editurl))
                .appendTo(tr);
                tr.appendTo(result);
            });

            properties.searchfield.next("button").remove();
            if(data.allcount > data.result.length) {
                var showallbutton =
                    $("<button></button>")
                        .html(properties.showall_label + " (" + data.allcount + ")")
                        .button();
                properties.searchfield.after(showallbutton);
                showallbutton.click(function(e) {
                    var term = properties.searchfield.val();
                    properties.term = term;
                    properties.showall = 'yes';
                    jQuery.autocompletetable.refreshtable(properties);
                    return false;
                });
            }
        });

        if(properties.searchfield.parent().children("table").length == 0) {
            properties.searchfield.parent().append(tbl);
        } else {
            properties.searchfield.parent().children("table").first().replaceWith(tbl);
        }


        // Check all checkboxes when clicking checkall
        checkall.click(function() {
            var qry ="#" + properties.id + " input:checkbox";
            var checked = checkall.is(":checked");
            //$.log(qry);
            //$.log(checked);
            $(qry).attr("checked", checked);
        });
    },
}


jQuery.fn.autocompletetable = function(jsonurl, headings, editlabel,
        showall_label, args) {

    return this.each(function(){
        this.properties = {};
        this.properties.id = $(this).attr("id");
        this.properties.jsonurl = jsonurl;
        this.properties.headings = headings;
        this.properties.editlabel = editlabel;
        this.properties.showall_label = showall_label;
        this.properties.showall = 'no';
        this.properties.term = '';

        var form = $("<form></form>")
            .attr("method", "post")
            .attr("action", '#') //.attr("action", deleteurl)
            .appendTo(this);

        var searchfieldid = $(this).attr("id") + "-searchfield";
        $("<label>Search: </label>")
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
        this.properties.searchfield = searchfield;

        // Add filterbar
        var filterbar = $("<div></div>")
            .addClass("autocompletetable-filterbar")
            .appendTo(form);

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

                submitfunc = function() {
                    form.attr("action", button.url);
                    form.submit();
                };

                if(button.confirmlabel) {
                    // Create confirm delete dialog
                    var confirmbuttons = {}
                    confirmbuttons[button.confirmlabel] = submitfunc;
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
                } else {
                    htmlbutton.click(submitfunc);
                }
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

        if(args.filters) {
            this.properties.filters = {}
            var filterid_prefix= $(this).attr("id") + "-filter-";

            var properties = this.properties;
            $.each(args.filters, function(filtertitle, filters) {
                var filterbox = $("<div></div>").appendTo(filterbar);
                $("<h3></h3>")
                    .html(filtertitle)
                    .appendTo(filterbox);
                var filterlist = $("<ul></ul>").appendTo(filterbox);
                $.each(filters, function(key, filter) {
                    var id = filterid_prefix + key;
                    var li = $("<li></li>").appendTo(filterlist);
                    $("<label></label>")
                        .html(filter.label)
                        .attr("for", id)
                        .appendTo(li);
                    var checkbox = $("<input/>")
                        .attr("type", "checkbox")
                        .attr("id", id)
                        .appendTo(li);
                    if(filter.classes) {
                        $.each(filter.classes, function(i, cls) {
                            checkbox.addClass(cls);
                        });
                    }
                    properties.filters[key] = filter
                    //this.properties.filters[key].enabled = false;
                    if(filter.enabled) {
                        checkbox.attr('checked', 'checked');
                    } else {
                        filter.enabled = false;
                    }
                    checkbox.button();

                    checkbox.click(function() {
                        properties.filters[key].enabled = !properties.filters[key].enabled;
                        $.each(properties.filters, function(k, f) {
                            $.log(k + ":" + f.enabled);
                        });
                        jQuery.autocompletetable.refreshtable(properties);
                        return false;
                    });
                });
            });
        }


        // Search when at least 2 characters are in the searchfield, and reset
        // when searchfield is empty.
        var properties = this.properties;
        searchfield.keydown(function(e) {
            if (e.keyCode==13) {
                return false;
            }
            });
        searchfield.keyup(function(e) {
            if (e.ctrlKey || e.altKey || e.shiftKey || e.metaKey) {
                return;
            }
            var term = $(this).val();
            if(term.length > 1 || term.length == 0) {
                properties.term = term;
                jQuery.autocompletetable.refreshtable(properties);
            }
        });


        // Initialize with default search results
        jQuery.autocompletetable.refreshtable(this.properties);
    });
};
jQuery.log = function(message) {
    if(window.console) {
        console.debug(message);
    } else {
        alert(message);
    }
};
