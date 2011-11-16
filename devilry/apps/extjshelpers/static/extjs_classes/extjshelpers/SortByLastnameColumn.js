Ext.define('devilry.extjshelpers.SortByLastnameColumn', {
    extend: 'Ext.grid.column.Column',
    alias: 'widget.sortbylastnamecolumn',

    doSort: function(direction) {
        var store = this.up('tablepanel').store;
        store.sort(Ext.create('Ext.util.Sorter', {
            direction: direction,
            sorterFn: Ext.bind(this._sorter, this)
        }));
    },

    _getLastName: function(fullname) {
        var sp = fullname.split(' ');
        return sp[sp.length - 1];
    },

    _sorter: function(a, b) {
        afull = a.get('full_name');
        bfull = b.get('full_name');
        if(Ext.typeOf(afull) != 'string') {
            return 1;
        } else if(Ext.typeOf(bfull) != 'string') {
            return -1;
        } else {
            var alast = this._getLastName(afull);
            var blast = this._getLastName(bfull);
            return alast.localeCompare(blast);
        }
    }
});
