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
        var idprefix = properties.searchfield.parent().parent().parent().attr("id") + "-cb";

        var postdata = {
            "term": properties.term,
            "all": properties.showall
        };
        if(properties.filters) {
            $.each(properties.filters, function(key, choice) {
                postdata["filter-" + key] = choice.enabled?choice.value: "";
            });
        }

        //var qrystring = ""
        //$.each(postdata, function(key, value) {
            //if(value != "")
                //qrystring += key + "=" + value + "&";
            //$.log(key + ":" + value);
        //});
        //$.log(qrystring);

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
                    var td = $("<td></td>");
                    var terms = properties.term.split(" AND ");
                    var label = part;
                    var cssclasses = false;
                    if(part instanceof Object) {
                        label = part.label;
                        cssclasses = part.cssclasses;
                    }
                    var p = label;
                    $.each(terms, function(index, term) {
                        p = p.replace(term.trim(),
                                "<strong>" + term + "</strong>");
                    });
                    var labeltag = $("<label>" + p + "</label>").attr("for", id);
                    if(cssclasses) {
                        labeltag.attr("class", cssclasses);
                    }
                    td.append(labeltag);
                    td.appendTo(tr);
                });
                var td = $("<td></td>");
                var first = true;
                $.each(item.actions, function(key, a) {
                    if(!first) {
                        $("<span></span>")
                            .html('&nbsp;|&nbsp;')
                            .attr("href", a.url)
                            .appendTo(td);
                    }
                    $("<a></a>")
                        .addClass("autocompletetable-singleaction")
                        .html(a.label)
                        .attr("href", a.url)
                        .appendTo(td);
                    first = false;
                });
                td.appendTo(tr);
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

            properties.resultcount.html("Current filters match "
                    + data.allcount + " of " + data.total + ".");
        });

        //if(properties.searchfield.parent().parent().children("table").length == 0) {
            //properties.searchfield.parent().parent().append(tbl);
        //} else {
            //properties.searchfield.parent().parent().children("table").first().replaceWith(tbl);
        //}
        properties.resulttable.replaceWith(tbl);
        properties.resulttable = tbl;


        // Check all checkboxes when clicking checkall
        checkall.click(function() {
            var qry ="#" + properties.id + " .autocompletetable-result input:checkbox";
            var checked = checkall.is(":checked");
            //$.log(qry);
            //$.log(checked);
            $(qry).attr("checked", checked);
        });
    },
}


jQuery.fn.autocompletetable = function(jsonurl, headings, showall_label, args)
{
    return this.each(function(){
        this.properties = {};
        this.properties.id = $(this).attr("id");
        this.properties.jsonurl = jsonurl;
        this.properties.headings = headings;
        this.properties.showall_label = showall_label;
        this.properties.showall = 'no';
        this.properties.term = '';

        // Add actions
        var actionscontainer = $("<div></div>")
            .addClass("autocompletetable-actionscontainer")
            .appendTo(this);
        $("<span></span>")
            .html("Select an action")
            .addClass("autocompletetable-selectaction")
            .appendTo(actionscontainer);
        var showhideactions= $("<button></button>")
            .html("Show actions")
            .addClass("autocompletetable-showhide-actions")
            .button({
                icons: {primary: 'ui-icon-triangle-1-s'},
                text: false
            })
            .appendTo(actionscontainer);
        var actions = $("<div></div>")
            .addClass("autocompletetable-actions")
            .appendTo(actionscontainer)
            .hide();
        showhideactions.click(function() {
            actions.toggle('blind', {}, 200);
            return false;
        });


        // Searchfield
        var form = $("<form></form>")
            .attr("method", "post")
            .attr("action", '#')
            .appendTo(this);
        var searchfieldcontainer = $("<div></div>")
            .addClass("autocompletetable-searchfieldcontainer")
            .appendTo(form);
        var searchfieldid = $(this).attr("id") + "-searchfield";
        $("<label>Search: </label>")
            .addClass("autocompletetable-filterlabel")
            .attr("for", searchfieldid)
            .appendTo(searchfieldcontainer);
        var searchfield =
            $("<input />")
                .attr("id", searchfieldid)
                .addClass("autocompletetable-searchfield")
                .addClass("ui-widget")
                .addClass("ui-widget-content")
                .addClass("ui-corner-all")
            .appendTo(searchfieldcontainer);
        var resulttable = $("<table></table>").appendTo(form);
        var resultcount = $("<div></div>")
            .addClass("autocompletetable-resultcount")
            .appendTo(form);
        this.properties.searchfield = searchfield;
        this.properties.resulttable = resulttable;
        this.properties.resultcount = resultcount;


        // Buttonbar actions
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
                var htmlbutton = $("<a></a>")
                    .attr("href", "#")
                    .addClass("autocompletetable-action")
                    .addClass("autocompletetable-action-button")
                    .html(button.label)
                    .appendTo(actions);
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
                    .addClass("autocompletetable-action")
                    .addClass("autocompletetable-action-link")
                    .appendTo(actions);
                if(link.classes) {
                    $.each(link.classes, function(i, cls) {
                        html_link.addClass(cls);
                    });
                }
                //$.log("link:: key: " + key + " label:" + link.label + " url:" + link.url);
            });
        }


        if(args.filters) {
            // Add filterbar
            var filterbar = $("<div></div>")
                .addClass("autocompletetable-filterbar")
                .insertBefore(resulttable);
            $("<div></div>")
                .html("Filters")
                .addClass("autocompletetable-filter-title")
                .appendTo(filterbar);

            this.properties.filters = {}
            var filterid_prefix= $(this).attr("id") + "-filter-";

            var properties = this.properties;
            $.each(args.filters, function(filterkey, filter) {
                var filterbox = $("<div></div>").appendTo(filterbar);
                $("<div></div>")
                    .html(filter.title)
                    .addClass("autocompletetable-filter-subtitle")
                    .appendTo(filterbox);
                var choicelist = $("<ul></ul>").appendTo(filterbox);
                var prefix = filterkey + "-"
                $.each(filter.choices, function(i, choice) {
                    var key = prefix + i;
                    var id = filterid_prefix + key;
                    var li = $("<li></li>").appendTo(choicelist);
                    var checkbox = $("<input/>")
                        .attr("type", "checkbox")
                        .attr("id", id)
                        .appendTo(li);
                    $("<label></label>")
                        .html(choice.label)
                        .attr("for", id)
                        .appendTo(li);
                    if(!choice.value) {
                        choice.value = "yes";
                    }
                    properties.filters[key] = choice
                    if(choice.enabled) {
                        checkbox.attr('checked', 'checked');
                    } else {
                        choice.enabled = false;
                    }
                    //checkbox.button();

                    checkbox.click(function() {
                        properties.filters[key].enabled = !properties.filters[key].enabled;
                        //$.each(properties.filters, function(k, choice) {
                            //$.log(k + ":" + choice.enabled + " (" + choice.value + ")");
                        //});
                        jQuery.autocompletetable.refreshtable(properties);
                        //return false;
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
