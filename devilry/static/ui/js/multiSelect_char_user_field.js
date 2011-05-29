
$(function() {
		function split(val) {
			return val.split(/,\s*/);
		}
		function extractLast(term) {
			return split(term).pop();
		}
		
		$(".devilry_multiselect_few").autocomplete({
				source: function(request, response) {
					$.getJSON(DEVILRY_MAIN_PAGE + "/ui/user_json", {
						  term: extractLast(request.term)
						  }, response);
				},
				search: function() {
					// custom minLength
					var term = extractLast(this.value);
					if (term.length < 2) {
						return false;
					}
				},
				focus: function() {
					// prevent value inserted on focus
					return false;
				},
				select: function(event, ui) {
	
					var terms = split( this.value );
					// remove the current input
					terms.pop();
					// add the selected item
					terms.push( ui.item.value);
				
					// add placeholder to get the comma-and-space at the end
					terms.push("");
					this.value = terms.join(", ");
					return false;
				}
			})
			.data( "autocomplete" )._renderItem = function( ul, item ) {
			     return $( "<li></li>" )
				     .data( "item.autocomplete", item )
				     .append( "<a class='autocomplete_item'>"+
							  "<span class='autocomplete_item_label'>" + item.label + "</span>"+
							  "<span class='autocomplete_item_desc'>" + item.desc + "</span></a>" )
				     .appendTo( ul );
		};
	});
