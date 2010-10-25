// vim: set ts=2 sts=2 et sw=2:



(function($){
    $.filtertable = {

      refresh_actions: function(store, actions, targetbox, requires_selection) {
        targetbox.empty();
        $.each(actions, function(i, action) {
            var box = $("<li></li>").appendTo(targetbox);
            var button = $("<a></a>")
              .html(action.label)
              .attr("href", "#")
              .appendTo(box);
            $.each(action.cssclasses, function(ci, cssclass) {
                button.addClass(cssclass);
              });
            button.click(function() {
                var c = $("#" + store.id + " input:checkbox:checked");
                if(c.length == 0 && requires_selection) {
                  store.noselection_dialog.dialog("open");
                  return false;
                }
                store.form.attr("action", action.url);
                store.form.submit();
              });
          });
      },


      refresh_filters: function(store, filterview, filteredsize) {
        store.filterbox.empty();
        $.each(filterview, function(filterindex, filter) {
            var box = $("<div></div>").appendTo(store.filterbox);
            $("<h4></h4>").html(filter.title).appendTo(box);
            var ul = $("<ul></ul>").appendTo(box);
            //var idprefix = store.id + "-filter-" + filterindex + "-";
            if(filter.multiselect) {
              var li = $("<li></li>").appendTo(ul);
              var toggleall = $("<a></a>")
                .attr("href", "#")
                .html("Check/uncheck all")
                .appendTo(li);
              toggleall.click(function() {
                  $.filtertable.refresh(store, 
                    {checkall_in_filter:filterindex});
                  return false;
                });
            }
            $.each(filter.labels, function(i, label) {
                //var id = idprefix + i;
                var li = $("<li></li>").appendTo(ul);
                var button = $("<input></input>")
                  .attr("type", filter.multiselect?"checkbox":"radio")
                  .appendTo(li);
                if (label.selected) {
                  button.attr("checked", "checked");
                };
                var lbl = $("<a></a>")
                  .attr("href", "#")
                  .html(label.label)
                  .appendTo(li);
                var count = $("<span></span>")
                  .addClass("filtertable-filtercount")
                  .appendTo(lbl);

                // Events
                lbl.click(function() {
                    button.click();
                    return false;
                  });
                button.click(function() {
                    var opt = {};
                    opt["filter_selected_"+filterindex] = i;
                    $.filtertable.refresh(store, opt);
                    return false;
                  });

                if(store.resultcount_supported) {
                  var opt = {countonly:"yes"};
                  opt["filter_selected_"+filterindex] = i;
                  $.getJSON(store.jsonurl, opt, function(json) {
                      var v = json.filteredsize;
                      if(filter.multiselect) {
                        v = json.filteredsize - filteredsize;
                        if(v >= 0)
                          v = "+" + v;
                      }
                      count.html(" (" + v + ")");
                      $.filtertable.recalc_accordion(store);
                    });
                }
              });
          });
      },



      create_header: function(store, has_selactions, columns, use_rowactions,
          order_by, order_asc) {
        var thead = $("<thead></thead>")
          .addClass("ui-widget-header");
        var tr = $("<tr></tr>").appendTo(thead);
        if(has_selactions) {
          var th = $("<th></th>")
            .addClass("filtertable-checkboxcell")
            .addClass("ui-state-default")
            .appendTo(tr);
          var checkall = $("<input/>")
            .attr("type", "checkbox")
            .appendTo(th);
          checkall.click(function() {
              var qry ="#" + store.id + " .filtertable-table input:checkbox";
              var checked = checkall.is(":checked");
              $(qry).attr("checked", checked);
            });
        }
        $.each(columns, function(i, col) {
            var th = $("<th></th>")
              .addClass("ui-state-default")
              .html(col.title)
              .appendTo(tr);
            if(col.can_order) {
              var icon = $("<span></span>")
                .addClass("ui-icon")
                .addClass("devilry-th-ui-icon")
                .appendTo(th);

              th.addClass("devilry-th-clickable")
              if(order_by == i) {
                icon.addClass(order_asc?"ui-icon-triangle-1-n":"ui-icon-triangle-1-s")
                th.addClass("ui-state-active");
              } else {
                icon.addClass("ui-icon-carat-2-n-s");
              }
              th.click(function() {
                  $.filtertable.refresh(store, {order_by:i});
                  return false;
                });
            }
          });
        if(use_rowactions) {
          var th = $("<th></th>")
            .addClass("ui-state-default")
            .html("&nbsp;")
            .appendTo(tr);
        }
        return thead;
      },

      create_body: function(data, has_selactions, id) {
        var name = id + "-checkbox";
        var tbody = $("<tbody></tbody>")
        $.each(data, function(i, row) {
            var tr = $("<tr></tr>")
              .addClass(i%2?"even":"odd")
              .appendTo(tbody);
            if(has_selactions) {
              var td = $("<td></td>")
                .addClass("filtertable-checkboxcell")
                .appendTo(tr);
              var checkbox = $("<input/>")
                .attr("type", "checkbox")
                .attr("name", name)
                .attr("value", row.id)
                .appendTo(td);
            }
            $.each(row.cells, function(index, cell) {
                var td = $("<td></td>")
                  .html(cell.value)
                  .appendTo(tr);
                if (cell.cssclass) {
                  td.addClass(cell.cssclass);
                };
              });
            if(row.actions.length > 0) {
                var td = $("<td></td>").appendTo(tr);
                $.each(row.actions, function(i, action) {
                    $("<a></a>")
                      .html(action.label)
                      .attr("href", action.url)
                      .button()
                      .appendTo(td);
                  });
            };
          });
        return tbody;
      },

      refresh_table: function(store, json) {
        store.result_table.empty();
        var has_selactions = json.selectionactions.length > 0;
        var thead = $.filtertable.create_header(store, has_selactions,
          json.columns, json.use_rowactions, json.order_by, json.order_asc);
        thead.appendTo(store.result_table);
        var tbody = $.filtertable.create_body(json.data, has_selactions, store.id);
        tbody.appendTo(store.result_table);
      },


      refresh_pagechanger: function(store, filteredsize, currentpage, perpage) {
        store.pagechangerbox.empty();
        var pages = parseInt("" + filteredsize / perpage) + 1;
        if(filteredsize % perpage == 0) {
          pages --;
        }
        if(pages == 0) {
          pages = 1;
        }
        var pagelabel = $("<div></div>")
          .addClass("filtertable-pagelabel")
          .html("Page " + (currentpage+1) + " of " + pages);
        var slider = $("<div></div>");
        pagelabel.appendTo(store.pagechangerbox);
        slider.appendTo(store.pagechangerbox);
        slider.slider({
            max: pages - 1,
            value: currentpage,
            slide: function(e, ui) {
              pagelabel.html("Page " + (ui.value+1) + " of " + pages);
            },
            change: function(e, ui) {
              $.filtertable.refresh(store, {gotopage:ui.value});
            }
        });
      },


      refresh_optional_cols: function(store, all_columns, active_optional_columns) {
        store.colsettingsbox.empty();
        $("<h4>Optional columns</h4>").appendTo(store.colsettingsbox);
        $.each(all_columns, function(index, colinfo) {
            if(colinfo.col.optional) {
              $("<div></div>").boxWithLabel({
                  label: colinfo.col.title,
                  value: index,
                  checked: colinfo.is_active
                }).appendTo(store.colsettingsbox);
            }
          });
        var button = $("<button></button>")
          .html("Refresh")
          .button({
              text: true,
              icons: {primary: "ui-icon-arrowrefresh-1-w"}
            })
          .appendTo(store.colsettingsbox);
        button.click(function() {
            var ch = store.colsettingsbox.find("input:checkbox:checked");
            if(ch.length == 0) {
              opt = {active_cols:"none"};
            } else {
              var opt = [];
              $.each(ch, function(index, checkbox) {
                  opt.push({name:"active_cols", value:checkbox.value});
                });
            }
            $.filtertable.refresh(store, opt);
            return false;
            //return false;
          });
      },

      recalc_accordion: function(store) {
        store.sidebar.accordion("option", "autoHeight", true);
        store.sidebar.accordion("resize");
      },

      refresh: function(store, options) {
        $.getJSON(store.jsonurl, options, function(json) {
            $.filtertable.refresh_filters(store, json.filterview, json.filteredsize);
            $.filtertable.refresh_actions(store,
              json.selectionactions, store.selectionactionsbox,
              true);
            $.filtertable.refresh_actions(store,
              json.relatedactions, store.relatedactionsbox);
            $.filtertable.refresh_table(store, json);
            $.filtertable.refresh_pagechanger(store, json.filteredsize,
              json.currentpage, json.perpage);
            $.filtertable.refresh_optional_cols(store, json.all_columns,
              json.active_optional_columns);

            store.searchfield.val(json.search);
            store.statusmsgbox.html(json.statusmsg);
            store.perpagefield.val(json.perpage);
            $.filtertable.recalc_accordion(store);
          });
      }
    };



    $.fn.boxWithLabel = function(args) {
      args.type = args.type || "checkbox";

      var box = $(this);
      var button = $("<input></input>")
        .attr("type", args.type)
        .appendTo(box);
      if(typeof(args.value) != undefined) {
        button.val(args.value);
      }
      if(args.checked) {
        button.attr("checked", "checked");
      }
      var lbl = $("<a></a>")
        .attr("href", "#")
        .html(args.label)
        .appendTo(box);

      // Events
      lbl.click(function() {
          button.click();
          return false;
        });
      if(args.click) {
        button.click(args.click);
      }

      return box;
    };


    $.fn.filtertable = function(jsonurl, resultcount_supported) {
      return this.each(function() {
          var id = $(this).attr("id");
          var store = {};
          store.id = id;
          store.jsonurl = jsonurl;
          store.form = $("#" + id + " form").first();
          store.searchbox = $("#" + id + " .filtertable-searchbox").first();
          store.selectionactionsbox = $("#" + id + " .filtertable-selectionactions").first();
          store.relatedactionsbox = $("#" + id + " .filtertable-relatedactions").first();
          store.filterbox = $("#" + id + " .filtertable-filters").first();
          store.result_table = $("#" + id + " .filtertable-table").first();
          store.pagechangerbox = $("#" + id + " .filtertable-pagechanger").first();
          store.searchfield = $("#" + id + " .filtertable-searchfield").first();
          store.statusmsgbox = $("#" + id + " .filtertable-statusmsg").first();
          store.colsettingsbox = $("#" + id + " .filtertable-settings-cols").first();
          store.resultcount_supported = resultcount_supported;

          // Show this dialog when selecting a action when no rows are
          // selected.
          store.noselection_dialog = $("#" + id + " .filtertable-noselection-dialog").first();
          store.noselection_dialog.dialog({
              modal: true,
              autoOpen: false,
              buttons: {
                "Ok": function() {
                  $( this ).dialog( "close" );
                }
              },
            });

          // Setup the accordion sidebar
          store.sidebar = $("#" + id + "-filtertable-sidebar");
          store.sidebar.accordion({
            header: "h3",
            autoHeight: false,
            event: "mouseover"
          });

          // Search
          store.searchfield.keydown(function(e) {
              if (e.keyCode==13) {
                $.filtertable.refresh(store, {search:store.searchfield.val()});
                return false;
              }
            });
          var searchbtn = $("#" + id + " .filtertable-searchbtn").first();
          searchbtn.button({
            text: false,
            icons: {primary: "ui-icon-search"}
          });
          searchbtn.click(function(e) {
              $.filtertable.refresh(store, {search:store.searchfield.val()});
              return false;
            });


          // Reset filters
          var resetfiltersbtn = $("#" + id + " .filtertable-resetfilters-button").first();
          resetfiltersbtn.click(function(e) {
              $.filtertable.refresh(store, {reset_filters:"yes"});
              return false;
            });

          // Settings
          store.perpagefield = $("#" + id + " .filtertable-perpagefield").first();
          store.perpagefield.keydown(function(e) {
              if (e.keyCode==13) {
                $.filtertable.refresh(store, {perpage:store.perpagefield.val()});
                return false;
              }
            });
          var perpagebtn = $("#" + id + " .filtertable-perpagebtn").first();
          perpagebtn.button({
            text: false,
            icons: {primary: "ui-icon-arrowrefresh-1-w"}
          });
          perpagebtn.click(function(e) {
              $.filtertable.refresh(store, {perpage:store.perpagefield.val()});
              return false;
            });


          // Set initial data
          $.filtertable.refresh(store);
        });

    };





    $.log = function(message) {
      if(window.console) {
        console.debug(message);
      } else {
        alert(message);
      }
    };
  })(jQuery);
