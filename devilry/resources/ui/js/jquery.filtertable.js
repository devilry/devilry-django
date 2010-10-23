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
                  .addClass(label.selected?"selected_filter":"unselected_filter")
                  .appendTo(li);
                button.click(function() {
                    var fs = [filterindex, i]
                    $.filtertable.refresh(store, {filter_selected:fs});
                    return false;
                  });
              });
          });
      },

      refresh: function(store, options) {
        var options = options==null?{}:options;
        var prop = {
          start: 0,
          perpage: 20
        }
        if(options.filter_selected != null) {
          var fs = options.filter_selected;
          prop['filter_selected_' + fs[0]] = fs[1];
        }
        if(options.order_by != null) {
          prop['order_by'] = options.order_by;
        }
        $.getJSON(store.jsonurl, prop, function(json) {
            $.filtertable.refresh_filters(store, json.filterview);
            store.result_table.empty();
            var thead = $.filtertable.create_header(store, json.columns);
            thead.appendTo(store.result_table);
            var tbody = $.filtertable.create_body(json.data);
            tbody.appendTo(store.result_table);
          });
      }
    };

    $.fn.filtertable = function(jsonurl) {
      return this.each(function() {
          var id = $(this).attr("id");
          var store = {};
          store.jsonurl = jsonurl;
          store.result_table = $("#" + id + " .filtertable-table").first();
          store.filterbox = $("#" + id + " .filtertable-filters").first();
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
