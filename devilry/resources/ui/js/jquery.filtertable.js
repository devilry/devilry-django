// vim: set ts=2 sts=2 et sw=2:



(function($){
    $.filtertable = {
      refresh_actions: function(store, actions) {
        store.actionsbox.empty();
        $.each(actions, function(i, action) {
            var li = $("<li></li>").appendTo(store.actionsbox);
            var button = $("<a></a>")
              .html(action.label)
              .attr("href", "#")
              .addClass("filtertable-action")
              .appendTo(li);
            $.each(action.cssclasses, function(ci, cssclass) {
                button.addClass(cssclass);
              });
            button.click(function() {
                $.log(i);
                store.form.attr("action", action.url);
                store.form.submit();
                return false;
              });
          });
      },

      create_header: function(store, has_actions, columns, use_rowactions) {
        var thead = $("<thead></thead>");
        var tr = $("<tr></tr>").appendTo(thead);
        if(has_actions) {
          var th = $("<th></th>")
            .addClass("filtertable-checkboxcell")
            .appendTo(tr);
          var checkall = $("<input/>")
            .attr("type", "checkbox")
            .appendTo(th);
          checkall.click(function() {
              var qry ="#" + store.id + " input:checkbox";
              var checked = checkall.is(":checked");
              $(qry).attr("checked", checked);
            });
        }
        $.each(columns, function(i, col) {
            var th = $("<th></th>")
              .html(col.title)
              .appendTo(tr);
            if(col.can_order) {
              th.click(function() {
                  $.filtertable.refresh(store, {order_by:i});
                  return false;
                });
            }
          });
        if(use_rowactions) {
          var th = $("<th></th>")
            .html("&nbsp;")
            .appendTo(tr);
        }
        return thead;
      },

      create_body: function(data, has_actions, id) {
        var name = id + "-checkbox";
        var tbody = $("<tbody></tbody>");
        $.each(data, function(i, row) {
            var tr = $("<tr></tr>").appendTo(tbody);
            if(has_actions) {
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
                  .html(cell)
                  .appendTo(tr);
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

      refresh_table: function(store, has_actions, columns, data, use_rowactions) {
        store.result_table.empty();
        var thead = $.filtertable.create_header(store, has_actions, columns,
              use_rowactions);
        thead.appendTo(store.result_table);
        var tbody = $.filtertable.create_body(data, has_actions, store.id);
        tbody.appendTo(store.result_table);
      },

      refresh_filters: function(store, filterview) {
        store.filterbox.empty();
        $.each(filterview, function(filterindex, filter) {
            var box = $("<div></div>").appendTo(store.filterbox);
            $("<h4></h4>").html(filter.title).appendTo(box);
            var ul = $("<ul></ul>").appendTo(box);
            $.each(filter.labels, function(i, label) {
                var li = $("<li></li>").appendTo(ul);
                var button = $("<a></a>")
                  .html(label.label)
                  .attr("href", "#")
                  .addClass("filtertable-filter")
                  .addClass(label.selected?
                    "filtertable-selected-filter":"filtertable-unselected-filter")
                  .appendTo(li);
                button.click(function() {
                    var opt = {};
                    opt["filter_selected_"+filterindex] = i;
                    $.filtertable.refresh(store, opt);
                    return false;
                  });
              });
          });
      },


      refresh_pagechanger: function(store, filteredsize, currentpage, perpage) {
        store.pagechangerbox.empty();
        var pages = parseInt("" + filteredsize / perpage);
        if(filteredsize % perpage == 0) {
          pages --;
        }
        var pagelabel = $("<div></div>")
          .html(currentpage + "/" + pages);
        var slider = $("<div></div>");
        pagelabel.appendTo(store.pagechangerbox);
        slider.appendTo(store.pagechangerbox);
        slider.slider({
            max: pages,
            value: currentpage,
            slide: function(e, ui) {
              pagelabel.html(ui.value + "/" + pages);
            },
            change: function(e, ui) {
              $.filtertable.refresh(store, {gotopage:ui.value});
            }
        });
      },

      refresh: function(store, options) {
        $.getJSON(store.jsonurl, options, function(json) {
            $.filtertable.refresh_filters(store, json.filterview);
            $.filtertable.refresh_actions(store, json.actions);
            $.filtertable.refresh_table(store, json.actions.length > 0,
                json.columns, json.data, json.use_rowactions);
            $.filtertable.refresh_pagechanger(store, json.filteredsize,
              json.currentpage, json.perpage);
            store.searchfield.val(json.search);
          });
      }
    };

    $.fn.filtertable = function(jsonurl) {
      return this.each(function() {
          var id = $(this).attr("id");
          var store = {};
          store.id = id;
          store.jsonurl = jsonurl;
          store.form = $("#" + id + " form").first();
          store.searchbox = $("#" + id + " .filtertable-searchbox").first();
          store.actionsbox = $("#" + id + " .filtertable-actions").first();
          store.filterbox = $("#" + id + " .filtertable-filters").first();
          store.result_table = $("#" + id + " .filtertable-table").first();
          store.pagechangerbox = $("#" + id + " .filtertable-pagechanger").first();
          store.searchfield = $("#" + id + " .filtertable-searchbox input").first();

          var tabs = $("#" + id + " .filtertable-tabs").first();
          tabs.tabs();

          $.filtertable.refresh(store);

          store.searchfield.keydown(function(e) {
              if (e.keyCode==13) {
                $.filtertable.refresh(store, {search:store.searchfield.val()});
                return false;
              }
            });
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
