/** Parses values from a string into plain values and filters which is
 * compatible with our RESTful filters.
 * */
Ext.define('devilry.extjshelpers.SearchStringParser', {
    config: {
        searchstring: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.query = "";
        this.filters = [];
        this.type = undefined;
        this.parseSearchString();
        return this;
    },

    isInt: function(value) {
        return !isNaN(parseInt(value));
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
        if(this.isInt(filter.value)) {
            filter.value = parseInt(filter.value);
        }
        this.filters.push(filter);
    },

    parseFilterIsh: function(filterstring) {
        var split = filterstring.split(':');
        var first = split[0].toLowerCase();
        if(first === 'type') {
            this.type = split[1];
        } else {
            this.parseFilter(split);
        }
    },

    /**
     * @private
     * Parse ``this.searchstring`` into:
     *
     *  ``this.filters``
     *      A filter list on the format used by Devilry.
     *      This goes into the ``filters`` parameter of
     *      a Devilry search. Set to ``undefined`` if no
     *      filters are found.
     *
     * ``this.query``
     *      Other values (all words not containing :). This goes
     *      into the ``query`` parameter of a Devilry search.
     *      Set to ``undefined if no query is found.
     *
     *  ``this.type``
     *      A special *filter* (type:mytype) which specifies that a search should
     *      be done for a specific type instead of on multiple types. Set to
     *      ``undefined`` if not found.
     */
    parseSearchString: function() {
        var split = this.searchstring.split(' ');
        var query = "";
        var me = this;
        Ext.each(split, function(word) {
            if(word.indexOf(':') === -1) {
                query += word + ' ';
            } else {
                me.parseFilterIsh(word);
            }
        });
        this.query = query;
        //console.log(this.query);
        //console.log(this.filters);
    },


    applyToExtraParams: function(extraParams, shortcuts) {
        if(!extraParams) {
            extraParams = new Object();
        }
        if(this.query) {
            extraParams.query = this.query;
        }
        if(this.filters) {
            var localfilters;
            if(shortcuts) {
                localfilters = this.applyShortcuts(shortcuts);
            } else {
                localfilters = this.filters;
            }
            extraParams.filters = Ext.JSON.encode(localfilters);
        }
        return extraParams;
    },

    applyShortcuts: function(shortcuts) {
        var localfilters = Ext.clone(this.filters);
        Ext.each(this.filters, function(filter, index) {
            if(shortcuts.hasOwnProperty(filter.field)) {
                //console.log(filter);
                localfilters[index].field = shortcuts[filter.field];
            }
        });
        return localfilters;
    }
});
