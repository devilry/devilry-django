Ext.define('devilry_subjectadmin.view.managestudents.SortByButton', {
    extend: 'Ext.button.Button',
    alias: 'widget.sortgroupsbybutton',
    cls: 'devilry_subjectadmin_sortgroupsbybutton',

    /**
     * @cfg {Object} [grid]
     * The grid to sort. The grid _must_ be configured to use a store that has
     * a sortBySpecialSorter() function.
     */

    text: gettext('Sort'),

    initComponent: function() {
        Ext.apply(this, {
            menu: [{
                itemId: 'sortByFullname',
                text: gettext('Full name'),
                listeners: {
                    scope: this,
                    click: this._onSortByFullname
                }
            }, {
                itemId: 'sortByLastname',
                text: gettext('Last name'),
                listeners: {
                    scope: this,
                    click: this._onSortByLastname
                }
            }, {
                itemId: 'sortByUsername',
                text: gettext('Username'),
                listeners: {
                    scope: this,
                    click: this._onSortByUsername
                }
            }]
        });
        this.callParent(arguments);
    },

    _onSortByFullname: function() {
        this._sortBy('fullname');
    },
    _onSortByLastname: function() {
        this._sortBy('lastname');
    },
    _onSortByUsername: function() {
        this._sortBy('username');
    },

    _sortBy: function(sorter) {
        this.grid.getStore().sortBySpecialSorter(sorter);
        this.fireEvent('afterSortBy', sorter);
    }
});
