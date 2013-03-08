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
                    this.progressWindow.start('Open/close groups');
                    this._finishedSavingGroupCount = 0;
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
    openOrCloseGroup: function(record, index, totalSelectedGroups, is_open) {
        var msg = Ext.String.format('{0} group {1}/{2}',
            (is_open? 'Opening': 'Closing'),
            index, totalSelectedGroups
        );
        this.getEl().mask(msg);

        var editRecord = this.createRecordFromStoreRecord(record);
        editRecord.data.is_open = is_open;
        editRecord.save({
            scope: this,
            callback: function(r, operation) {
                if(operation.success) {
                    this.progressWindow.addSuccess(record, Ext.String.format('Group successfully {0}.', (is_open? 'opened': 'closed')));
                } else {
                    this.progressWindow.addErrorFromOperation(
                        record,
                        Ext.String.format('Failed to {0} group.', (is_open? 'open': 'close')),
                        operation
                    );
                }

                this._finishedSavingGroupCount ++;
                if(this._finishedSavingGroupCount == totalSelectedGroups) {
                    this.loadFirstPage();
                    this.getEl().unmask();
                    this.progressWindow.finish(interpolate(gettext('%(opened_or_closed)s %(count)s groups'), {
                        opened_or_closed: (is_open? gettext('Opened'): gettext('Closed')),
                        count: totalSelectedGroups
                    }, true));
                }
            }
        });
    }

});
