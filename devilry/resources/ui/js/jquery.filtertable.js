// vim: set ts=2 sts=2 et sw=2:



(function($){
    $.filtertable = {

      refresh_actions: function(store, actions, targetbox, requires_selection) {
        targetbox.empty();
        $.each(actions, function(i, action) {
            var box = $("<li></li>").appendTo(targetbox);
            var button = $("<a></a>")
              .html(action.label)
              .attr("href", requires_selection?"#":action.url)
              .appendTo(box);
            $.each(action.cssclasses, function(ci, cssclass) {
                button.addClass(cssclass);
              });
            if(requires_selection) {
              button.click(function() {
                  var checked = store.result_table.find("tbody input:checkbox:checked");
                  if(checked.length == 0) {
                    store.noselection_dialog.dialog("open");
                    return false;
                  }

                  if(action.confirm_title && action.confirm_message) {
                    store.confirm_dialog_messagebox.empty();
                    $("<span></span>").html(action.confirm_message)
                      .appendTo(store.confirm_dialog_messagebox);
                    store.confirm_dialog_selectionbox.empty();
                    var ul = $("<ul></ul>")
                      .appendTo(store.confirm_dialog_selectionbox);
                    $.each(checked, function(index, checkbox) {
                      //var tr = checkbox.parent();
                      $("<li></li>")
                        .html($(checkbox).data("title"))
                        .appendTo(ul);
                    });
                    store.confirm_dialog.dialog({
                        modal: true,
                        title: action.confirm_title,
                        width: 500,
                        height: 300,
                        buttons: {
                          "Ok": function() {
                            $(this).dialog("close");
                            $(this).dialog("destroy");
                            store.form.attr("action", action.url);
                            store.form.submit();
                          },
                          Cancel: function() {
                            $(this).dialog("close");
                            $(this).dialog("destroy");
                          }
                        },
                      });
                    return false;
                  } else {
                    store.form.attr("action", action.url);
                    store.form.submit();
                  }
                });
            }
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
                  .attr("title", label.labelobj.title)
                  .tipTip({delay:0})
                  .appendTo(li);
                if (label.selected) {
                  button.attr("checked", "checked");
                };
                var lbl = $("<a></a>")
                  .attr("href", "#")
                  .html(label.labelobj.label)
                  .attr("title", label.labelobj.title)
                  .tipTip({delay:0})
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
                        diff = json.filteredsize - filteredsize;
                        if(diff >= 0)
                          diff = "+" + diff;
                        v = v + " [" + diff + "]";
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
            .tipTip({
                content:
                  "<p><strong>Click</strong>: mark all rows matching this filter</p>" +
                  "<p><strong>Shift-click:</strong> mark all rows on this page</p>",
                delay: 200,
                defaultPosition: "left",
              })
            .appendTo(th);
          checkall.click(function(e) {
              var markfunc = function() {
                  var qry = store.result_table.find("input:checkbox");
                  var checked = checkall.is(":checked");
                  qry.attr("checked", checked);
                };
              if(e.shiftKey) {
                markfunc();
              } else {
                $.filtertable.refresh(store, {perpage:"all"}, markfunc);
              }
            });
        }
        $.each(columns, function(i, col) {
            var th = $("<th></th>")
              .addClass("ui-state-default")
              .html(col.heading)
              .appendTo(tr);
            if(col.title) {
              th.tipTip({
                  content: col.title,
                  delay: 200,
                  defaultPosition: "left",
                });
            }
            if(col.can_order) {
              var icon = $("<span></span>")
                .addClass("ui-icon")
                .addClass("devilry-th-ui-icon")
                .appendTo(th);

              th.addClass("devilry-th-clickable");
              if(order_by == col.id) {
                icon.addClass(order_asc?"ui-icon-triangle-1-s":"ui-icon-triangle-1-n")
                th.addClass("ui-state-active");
              } else {
                icon.addClass("ui-icon-carat-2-n-s");
              }
              th.click(function() {
                  $.filtertable.refresh(store, {order_by:col.id});
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

      create_body: function(data, has_selactions, id, order_colnum) {
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
                .data("title", row.title)
                .appendTo(td);
            }
            $.each(row.cells, function(index, cell) {
                var td = $("<td></td>")
                  .html(cell.value)
                  .appendTo(tr);
                if(index == order_colnum) {
                  td.addClass("highlight-column");
                }
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
                      .addClass("ui-priority-secondary")
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
          json.active_columns, json.use_rowactions, json.order_by, json.order_asc);
        thead.appendTo(store.result_table);
        var tbody = $.filtertable.create_body(json.data, has_selactions, store.id,
          json.order_colnum);
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
        if(pages < 2) {
          return;
        };
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


      refresh_optional_cols: function(store, all_columns) {
        store.colsettingsbox.empty();
        var has_optional = false;
        $.each(all_columns, function(index, colinfo) {
            if(colinfo.col.optional) {
              has_optional = true;
            }
        });
        if(!has_optional) {
          return;
        }

        $("<h4>Optional columns</h4>").appendTo(store.colsettingsbox);
        $.each(all_columns, function(index, colinfo) {
            if(colinfo.col.optional) {
              var d = $("<div></div>").boxWithLabel({
                  label: colinfo.col.heading,
                  value: index,
                  checked: colinfo.is_active
                }).appendTo(store.colsettingsbox);
              if(colinfo.col.title) {
                d.tipTip({
                    content: colinfo.col.title,
                    delay: 200,
                    defaultPosition: "right",
                  });
              }
            }
          });
        var button = $("<button></button>")
          .html("Refresh")
          .button({
              text: true,
              icons: {primary: "ui-icon-arrowrefresh-1-w"}
            })
          .addClass("ui-priority-secondary")
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

      refresh: function(store, options, oncomplete) {
        store.result_table.empty();
        store.databox.hide();
        store.loadingbox.show();
        $.getJSON(store.jsonurl, options, function(json) {
            store.loadingbox.hide();
            store.databox.show();
            if(store.has_filters) {
              $.filtertable.refresh_filters(store, json.filterview, json.filteredsize);
            }
            if(store.has_selection_actions) {
              $.filtertable.refresh_actions(store,
                json.selectionactions, store.selectionactionsbox,
                true);
            }
            if(store.has_related_actions) {
              $.filtertable.refresh_actions(store,
                json.relatedactions, store.relatedactionsbox);
            }
            $.filtertable.refresh_table(store, json);
            $.filtertable.refresh_pagechanger(store, json.filteredsize,
              json.currentpage, json.perpage);
            $.filtertable.refresh_optional_cols(store, json.all_columns);

            if(store.has_search) {
              store.searchfield.val(json.search);
            }
            store.statusmsgbox.html(json.statusmsg);
            store.perpagefield.val(json.perpage);
            $.filtertable.recalc_accordion(store);

            if(oncomplete) {
              oncomplete();
            }
          });
      }
    };


    $.fn.filtertable = function(jsonurl, options) {
      return this.each(function() {
          var id = $(this).attr("id");
          var store = options;
          store.id = id;
          store.jsonurl = jsonurl;
          store.form = $(this).find("form").first();
          store.databox = $(this).find(".filtertable-data").first();
          store.result_table = $(this).find(".filtertable-table").first();
          store.pagechangerbox = $(this).find(".filtertable-pagechanger").first();
          store.statusmsgbox = $(this).find(".filtertable-statusmsg").first();
          store.loadingbox = $(this).find(".filtertable-loading").first();
          store.colsettingsbox = $(this).find(".filtertable-settings-cols").first();

          // These might not exists, depending on how the table is configured
          store.searchfield = $(this).find(".filtertable-searchfield").first();
          store.selectionactionsbox = $(this).find(".filtertable-selectionactions").first();
          store.relatedactionsbox = $(this).find(".filtertable-relatedactions").first();
          store.filterbox = $(this).find(".filtertable-filters").first();

          // Show this dialog when selecting a action when no rows are
          // selected.
          store.noselection_dialog = $(this).find(".filtertable-noselection-dialog").first();
          store.noselection_dialog.dialog({
              modal: true,
              autoOpen: false,
              buttons: {
                "Ok": function() {
                  $( this ).dialog( "close" );
                }
              },
            });

          // Show this dialog when selecting a action that requires
          // confirmation
          store.confirm_dialog = $(this).find(".filtertable-confirm-selection-dialog").first();
          store.confirm_dialog_messagebox = store.confirm_dialog.children("p").children().last();
          store.confirm_dialog_selectionbox = store.confirm_dialog.children("div").first();

          // Setup the accordion sidebar
          store.sidebar = $(this).find(".filtertable-sidebar").first();
          store.sidebar.accordion({
            header: "h3",
            autoHeight: false,
            event: store.accordion_event
          });

          // Search
          if(store.has_search) {
            store.searchfield.keydown(function(e) {
                if (e.keyCode==13) {
                  $.filtertable.refresh(store, {search:store.searchfield.val()});
                  return false;
                }
              });
            var searchbtn = $(this).find(".filtertable-searchbtn").first();
            searchbtn.button({
              text: false,
              icons: {primary: "ui-icon-search"}
            }).addClass("ui-priority-secondary");
            searchbtn.click(function(e) {
                $.filtertable.refresh(store, {search:store.searchfield.val()});
                return false;
              });
          }


          // Reset filters
          var resetbtn = $(this).find(".filtertable-reset-button").first();
          resetbtn.click(function(e) {
              $.filtertable.refresh(store, {reset:"yes"});
              return false;
            });

          // Settings
          store.perpagefield = $(this).find(".filtertable-perpagefield").first();
          store.perpagefield.keydown(function(e) {
              if (e.keyCode==13) {
                $.filtertable.refresh(store, {perpage:store.perpagefield.val()});
                return false;
              }
            });
          var perpage_updatebtn = $(this).find(".filtertable-perpage-updatebtn").first();
          perpage_updatebtn.button({
            text: false,
            icons: {primary: "ui-icon-arrowrefresh-1-w"}
          }).addClass("ui-priority-secondary");
          perpage_updatebtn.click(function(e) {
              $.filtertable.refresh(store, {perpage:store.perpagefield.val()});
              return false;
            });
          var perpage_allbtn = $(this).find(".filtertable-perpage-allbtn").first();
          perpage_allbtn.button({
            text: true,
          }).addClass("ui-priority-secondary");
          perpage_allbtn.click(function(e) {
              $.filtertable.refresh(store, {perpage:"all"});
              return false;
            });


          // Set initial data
          $.filtertable.refresh(store);
        });

    };
  })(jQuery);
