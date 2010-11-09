// vim: set ts=2 sts=2 et sw=2:

$.widget("ui.combobox", {
    _create: function() {
      var self = this;
      //var select = this.element.hide();
      var availableTimes = ["00:00", "08:00", "10:00", "12:00", "14:00", "16:00",
        "18:00", "20:00", "22:00", "23:59"];
      var input = self.element.autocomplete({
          source: availableTimes,
          delay: 0,
          minLength: 0
        });

      var button_container = $("<span></span>").insertAfter(input);

      // Add the button which triggers a dropdown
      $("<a></a>")
        .attr("tabIndex", -1)
        .attr("title", "Select a time")
        .tipTip()
        .html("Select")
        .appendTo(button_container)
        .button({
            icons: {
              primary: "ui-icon-triangle-1-s"
            },
            text: false
          }).removeClass('ui-corner-all')
        .addClass("ui-corner-right ui-button-icon")
        .click(function() {
            // close if already visible
            if (input.autocomplete("widget").is(":visible")) {
              input.autocomplete("close");
              return false;
            }
            // pass empty string as value to search for, displaying all results
            input.autocomplete("search", "");
            input.focus();
            return false;
          });

      // Add the now button
      $("<a></a>")
        .attr("tabIndex", -1)
        .attr("title", "Set time to current time")
        .tipTip()
        .html("Now")
        .appendTo(button_container)
        .button()
        .addClass("ui-priority-secondary")
        .click(function() {
          var now = new Date();
          var hours = now.getHours();
          if(hours < 10)
            hours = "0" + hours;
          var minutes = now.getMinutes();
          if(minutes < 10)
            minutes = "0" + minutes;
          input.val(hours + ':' + minutes);
          input.focus();

          var qry = $(this).parents('.devilry-datetime');
          if(qry.length != 0) {
            var container = qry.first();
            var datefield = container.find(".devilry-date");
            var month = now.getMonth()<10?"0"+now.getMonth():now.getMonth();
            var day = now.getDate()<10?"0"+now.getDate():now.getDate();
            var d = now.getFullYear() + "-" + month + "-" + day;
            datefield.val(d);
          }

          return false;
        });
  }
});


$(".devilry-time").combobox();
