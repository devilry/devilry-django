Ext.define('devilry_subjectadmin.view.managestudents.ChooseExaminersWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.chooseexaminerswindow',
    cls: 'devilry_subjectadmin_chooseexaminerswindow',

    requires: [
        'devilry_subjectadmin.view.managestudents.ChooseExaminersPanel'
    ],

    layout: 'fit',
    closable: true,
    width: 700,
    height: 500,
    maximizable: true,
    modal: true,

    initComponent: function() {
        Ext.apply(this, {
            items: {
                xtype: 'chooseexaminerspanel',
                buttonText: this.title
            },
            listeners: {
                scope: this,
                beforeclose: this._onBeforeClose
            }
        });
        this.callParent(arguments);
    },

    _onBeforeClose: function() {
        var panel = this.down('chooseexaminerspanel');
        var itemCount = panel.store.getCount();

        if(itemCount > 0 && !this.closeConfirmed) {
            Ext.MessageBox.show({
                title: gettext('Close without saving?'),
                msg: gettext('Are you sure you want to close the window without saving your changes?'),
                buttons: Ext.Msg.YESNO,
                icon: Ext.Msg.QUESTION,
                scope: this,
                fn: function(button) {
                    if(button == 'yes') {
                        this.closeConfirmed = true;
                        this.close();
                    }
                }
            });
            return false;
        }
    },

    closeWithoutConfirm: function() {
        this.closeConfirmed = true;
        this.close();
    }
});
