/** The close/open methods for StudentsManager.
 *
 * Note that this class depends on createRecordFromStoreRecord(),
 * onSelectNone() and loadFirstPage() from StudentsManager to be available. */
Ext.define('devilry.extjshelpers.studentsmanager.StudentsManagerCloseOpen', {
    /**
     * @private
     */
    onCloseGroups: function() {
        this.openOrCloseGroups(false);
    },

    /**
     * @private
     */
    onOpenGroups: function() {
        this.openOrCloseGroups(true);
    },

    /**
     * @private
     */
    openOrCloseGroups: function(is_open) {
        if(this.noneSelected()) {
            this.onSelectNone();
            return;
        }
        var action = is_open? 'open': 'close';
        Ext.MessageBox.show({
            title: Ext.String.format('Confirm {0} groups?', action),
            msg: Ext.String.format('Are you sure you want to {0} the selected groups?', action),
            buttons: Ext.Msg.YESNO,
            icon: Ext.Msg.WARNING,
            scope: this,
            fn: function(btn) {
                if(btn == 'yes') {
                    this.down('studentsmanager_studentsgrid').performActionOnSelected({
                        scope: this,
                        callback: this.openOrCloseGroup,
                        extraArgs: [is_open]
                    });
                }
            }
        });

    },

    /**
     * @private
     */
    openOrCloseGroup: function(record, index, total, is_open) {
        var msg = Ext.String.format('Closing group {0}/{1}', index, total);
        this.getEl().mask(msg);

        var editRecord = this.createRecordFromStoreRecord(record);
        editRecord.data.is_open = is_open;
        editRecord.save({
            failure: function() {
                console.error('Failed to save record');
            }
        });

        if(index == total) {
            this.loadFirstPage();
            this.getEl().unmask();
        }
    },

});
