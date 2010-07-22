
var availableTags = ["00:00", "08:00", "10:00", "12:00", "14:00", "16:00",
	"18:00", "20:00", "22:00"];
//$(".devilry-time").autocomplete({
	//source: availableTags,
	//minLength: 0
//});


$.widget("ui.combobox", {
	_create: function() {
		var self = this;
		//var select = this.element.hide();
		var input = self.element.autocomplete({
				source: availableTags,
				delay: 0,
				minLength: 0
			});

		var button_container = $("<span></span>").insertAfter(input);

		// Add the button which triggers a dropdown
		$("<button>&nbsp;</button>")
			.attr("tabIndex", -1).attr("title", "Select a time")
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
		$("<button>Now</button>")
			.attr("tabIndex", -1).attr("title", "Set time to current time")
			.appendTo(button_container)
			.button()
			.click(function() {
				// pass empty string as value to search for, displaying all results
				var now = new Date();
				var hours = now.getHours();
				if(hours < 10)
					hours = "0" + hours;
				var minutes = now.getMinutes();
				if(minutes < 10)
					minutes = "0" + minutes;
				input.val(hours + ':' + minutes);
				input.focus();
				return false;
			});
	}
});


$(".devilry-time").combobox();
