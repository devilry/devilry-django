/**
 * Selection model that checks the clicked row without deselecting the previous
 * selection.
 * */
Ext.define('devilry_extjsextras.GridMultiSelectModel', {
    extend: 'Ext.selection.CheckboxModel',

    onRowMouseDown: function(view, record, item, index, e) {
        view.el.focus();
        var me = this;

        // checkOnly set, but we didn't click on a checker.
        if (me.checkOnly && !checker) {
            return;
        }

        // Only check with left mouse button
        if(e.button !== 0) {
            return;
        }

        var mode = me.getSelectionMode();
        // dont change the mode if its single otherwise
        // we would get multiple selection
        if (mode !== 'SINGLE') {
            me.setSelectionMode('SIMPLE');
        }
        me.selectWithEvent(record, e);
        me.setSelectionMode(mode);
    }
});
