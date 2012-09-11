Ext.define('devilry_subjectadmin.store.AbstractRelatedUsers', {
    extend: 'Ext.data.Store',

    requires: [
        'devilry_extjsextras.DjangoRestframeworkProxyErrorHandler',
        'devilry_extjsextras.HtmlErrorDialog'
    ],

    loadInPeriod: function(periodId, loadConfig) {
        this.setPeriod(periodId);
        this.load(loadConfig);
    },


    /**
     * @param {Function} [config.success]
     *     Callback invoked in ``config.scope``
     *     when the store loads successfully. Parameters are ``records`` and
     *     ``operation``.
     * @param {Boolean} [config.scope]
     *     Scope to invoke ``config.success`` in.
     * @param {String} [config.errortitle] The title of the error message shown on load error.
     */
    loadWithAutomaticErrorHandling: function(config) {
        this.load({
            scope: this,
            callback: function(records, operation) {
                if(operation.success) {
                    Ext.callback(config.success, config.scope, [records, operation]);
                } else {
                    this._onLoadFailure(operation, config.errortitle);
                }
            }
        });
    },
    _onLoadFailure: function(operation, errortitle) {
        var error = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler', operation);
        error.addErrors(null, operation);
        var errormessage = error.asHtmlList();
        Ext.widget('htmlerrordialog', {
            title: errortitle,
            bodyHtml: errormessage
        }).show();
    },


    sortBySpecialSorter: function(sortby) {
        var sorter = null;
        if(sortby == 'username') {
            sorter = this._sortByUsername;
        } else if(sortby == 'full_name') {
            sorter = this._sortByFullname;
        } else {
            throw "Invalid sorter: " + sortby;
        }
        this.sort(Ext.create('Ext.util.Sorter', {
            sorterFn: Ext.bind(sorter, this)
        }));
    },

    _sortByUsername: function(a, b) {
        return this._sortByUserProperty('username', a, b);
    },

    _sortByFullname: function(a, b) {
        return this._sortByUserProperty('full_name', a, b);
    },

    _sortByUserProperty: function(property, a, b) {
        var avalue = a.get('user')[property];
        var bvalue = b.get('user')[property];
        if(Ext.isEmpty(avalue)) {
            return 1;
        } else if(Ext.isEmpty(bvalue)) {
            return -1;
        } else {
            return avalue.localeCompare(bvalue);
        }
    },


    /**
     * Get the contents of the related users store as an object with tag as key
     * and an array of related user records as value.
     */
    getMappedByTags: function() {
        var map = {}; // tag -> [relatedUserRecord]
        this.each(function(relatedUserRecord) {
            Ext.each(relatedUserRecord.getTagsAsArray(), function(tag) {
                if(map[tag]) {
                    map[tag].push(relatedUserRecord);
                } else {
                    map[tag] = [relatedUserRecord];
                }
            }, this);
        }, this);
        return map;
    },


    getByUserid: function(userId) {
        var index = this.findBy(function(record) {
            return record.get('user').id === userId;
        }, this);
        if(index === -1) {
            return null;
        } else {
            return this.getAt(index);
        }
    }
});
