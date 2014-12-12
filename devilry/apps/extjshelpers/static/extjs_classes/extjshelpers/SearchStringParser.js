/** Parses values from a string into plain values and filters which is
 * compatible with our RESTful filters.
 * */
Ext.define('devilry.extjshelpers.SearchStringParser', {
    filterToStringTpl: Ext.create('Ext.XTemplate', '{field}:{comp}:{value}'),
    toStringTpl: Ext.create('Ext.XTemplate',
        '<tpl if="type">type:{type} </tpl>',
        '<tpl if="filters">{filters} </tpl>',
        '{query}'),
    config: {
        searchstring: undefined,
        pageSizeWithType: 10,
        pageSizeWithoutType: 3,
        alwaysAppliedFilters: [],
    },

    constructor: function(config) {
        this.initConfig(config);
        this.query = "";
        this.filters = [];
        this.type = undefined;
        this.parseSearchString();
        return this;
    },

    toString: function() {
        return Ext.String.trim(this.toStringTpl.apply({
            query: this.query,
            filters: this.filtersToString(),
            type: this.type
        }));
    },

    filtersToString: function() {
        var filterstring = "";
        var me = this;
        Ext.each(this.filters, function(filter) {
            filterstring += me.filterToString(filter) + ' ';
        });
        return Ext.String.trim(filterstring);
    },

    filterToString: function(filter) {
        return this.filterToStringTpl.apply(filter);
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
        if(!Ext.Array.contains(this.illegalFilters, filter.field)) {
            this.filters.push(filter);
        }
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
        this.illegalFilters = [];
        Ext.each(this.alwaysAppliedFilters, function(filter, index) {
            this.illegalFilters.push(filter.field);
        }, this);

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

    applyPageSizeToStore: function(store) {
        if(this.type) {
            store.pageSize = this.pageSizeWithType;
        } else {
            store.pageSize = this.pageSizeWithoutType;
        }
    },

    applyToExtraParams: function(extraParams, shortcuts) {
        if(!extraParams) {
            extraParams = new Object();
        }
        if(this.query) {
            extraParams.query = this.query;
        }

        var localfilters = [];
        if(this.filters) {
            if(shortcuts) {
                localfilters = this.applyShortcuts(shortcuts);
            } else {
                localfilters = this.filters;
            }
        }
        if(this.alwaysAppliedFilters) {
            Ext.Array.insert(localfilters, 0, this.alwaysAppliedFilters);
        }

        extraParams.filters = Ext.JSON.encode(localfilters);
        return extraParams;
    },

    /**
     * @private
     */
    applyShortcuts: function(shortcuts) {
        var localfilters = Ext.clone(this.filters);
        var me = this;
        Ext.each(this.filters, function(filter, index) {
            var fieldnameFromFilter = me.applyFirstMatchingShortcut(shortcuts, filter.field);
            if(fieldnameFromFilter) {
                localfilters[index].field = fieldnameFromFilter;
            }
            //console.log(localfilters[index].field);
        });
        return localfilters;
    },

    /**
     * @private
     */
    applyFirstMatchingShortcut: function(shortcuts, fieldname) {
        var realFieldname = undefined;
        Ext.Object.each(shortcuts, function(shortcut, replacement) {
            var startswithShortcut = new RegExp("^" + shortcut);
            if(fieldname.match(startswithShortcut)) {
                realFieldname = fieldname.replace(startswithShortcut, replacement);
                return false;
            }
        });
        return realFieldname;
    }
});
