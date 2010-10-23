// vim: set ts=2 sts=2 et sw=2:



(function($){
    $.filtertable = {

      create_table_row: function(i, row) {
        var tr = $("<tr></tr>");
        $.each(row.cells, function(index, cell) {
            var td = $("<td></td>")
            .html(cell)
            .appendTo(tr);
          });
        return tr;
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
                    $.filtertable.refresh(store, fs);
                    return false;
                  });
              });
          });
      },

      refresh: function(store, filter_selected) {
        var prop = {
          start: 0,
          perpage: 20
        }
        if(filter_selected != null) {
          prop['filter_selected_' + filter_selected[0]] = filter_selected[1];
        }
        $.getJSON(store.jsonurl, prop, function(json) {
            $.filtertable.refresh_filters(store, json.filterview);
            store.result_tbody.empty();
            $.each(json.data, function(i, row) {
                var tr = $.filtertable.create_table_row(i, row);
                tr.appendTo(store.result_tbody);
              });
          });
      }
    };

    $.fn.filtertable = function(jsonurl) {
      return this.each(function() {
          var id = $(this).attr("id");
          var store = {};
          store.jsonurl = jsonurl;
          store.result_tbody = $("#" + id + " .filtertable-table tbody").first();
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
