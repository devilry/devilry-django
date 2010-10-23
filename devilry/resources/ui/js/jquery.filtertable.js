// vim: set ts=2 sts=2 et sw=2:



(function($){
    $.filtertable = {

      create_body: function(data) {
        var tbody = $("<tbody></tbody>");
        $.each(data, function(i, row) {
            var tr = $("<tr></tr>").appendTo(tbody);
            $.each(row.cells, function(index, cell) {
                var td = $("<td></td>")
                  .html(cell)
                  .appendTo(tr);
              });
          });
        return tbody;
      },

      create_header: function(store, columns) {
        var thead = $("<thead></thead>");
        var tr = $("<tr></tr>").appendTo(thead);
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
        return thead;
      },

      refresh_table: function(store, columns, data) {
        store.result_table.empty();
        var thead = $.filtertable.create_header(store, columns);
        thead.appendTo(store.result_table);
        var tbody = $.filtertable.create_body(data);
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
            $.filtertable.refresh_table(store, json.columns, json.data);
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
          store.jsonurl = jsonurl;
          store.searchbox = $("#" + id + " .filtertable-searchbox").first();
          store.filterbox = $("#" + id + " .filtertable-filters").first();
          store.result_table = $("#" + id + " .filtertable-table").first();
          store.pagechangerbox = $("#" + id + " .filtertable-pagechanger").first();
          store.searchfield = $("#" + id + " .filtertable-searchbox input").first();
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
