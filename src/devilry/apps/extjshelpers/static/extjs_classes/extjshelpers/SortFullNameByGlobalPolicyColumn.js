Ext.define('devilry.extjshelpers.SortFullNameByGlobalPolicyColumn', {
    extend: 'devilry.extjshelpers.SortByLastnameColumn',
    alias: 'widget.sortfullnamebyglobalpolicycolumn',

    compare: function(afull, bfull) {
        if(DevilrySettings.DEVILRY_SORT_FULL_NAME_BY_LASTNAME) {
            return this.callParent(arguments);
        } else {
            return afull.localeCompare(bfull);
        }
    }
});
