/** Parses values from a string into plain values and filters which is
 * compatible with our RESTful filters.
 * */
Ext.define('devilry.extjshelpers.SearchStringParser', {
    constructor: function(searchstring) {
        this.searchstring = searchstring;
        this.nonFilterValues = "";
        this.filters = new Array();
        this.parseSearchString();
        return this;
    },

    parseFilter: function(filtersplit) {
        var filter = new Object();
        filter.field = filtersplit[0];
        if(filtersplit.length === 2) {
            filter.comp = 'exact';
            filter.value = filtersplit[1];
        } else {
            filter.comp = filtersplit[1];
            filter.value = filtersplit[2];
        }
        this.filters.push(filter);
    },

    parseFilterIsh: function(filterstring) {
        var split = filterstring.split(':');
        var first = split[0].toLowerCase();
        if(first === 'type') {
            this.type = first;
        } else {
            this.parseFilter(split);
        }
    },

    parseSearchString: function() {
        var split = this.searchstring.split(' ');
        var nonFilterValues = "";
        var me = this;
        Ext.each(split, function(word) {
            if(word.indexOf(':') === -1) {
                nonFilterValues += word + ' ';
            } else {
                me.parseFilterIsh(word);
            }
        });
        this.nonFilterValues = nonFilterValues;
        //console.log(nonFilterValues);
    }
});
