Ext.define('devilry_subjectadmin.view.managestudents.ChooseExaminersPanel', {
    extend: 'devilry_usersearch.AbstractManageUsersPanel',
    alias: 'widget.chooseexaminerspanel',
    cls: 'devilry_subjectadmin_chooseexaminerspanel',
    requires: [
        'devilry_extjsextras.PrimaryButton',
        'devilry_usersearch.ManageUsersGridModel'
    ],

    /**
     * @cfg {string} buttonText
     * Text of the "save" button
     */

    confirmBeforeRemove: false,

    constructor: function(config) {
        this.store = Ext.create('Ext.data.Store', {
            model: 'devilry_usersearch.ManageUsersGridModel'
        });
        this.callParent([config]);
    },

    _mask: function(message) {
        this.setLoading(message);
    },
    _unmask: function() {
        this.setLoading(false);
    },

    addUser: function(userRecord) {
        console.log('Add user', userRecord.data);
        this.store.add(userRecord);
        this.onUserAdded(userRecord);
        this.down('#saveButton').enable();
    },

    removeUsers: function(userRecords) {
        this.store.remove(userRecords);
        this.onUsersRemoved();
        if(this.store.count() == 0) {
            this.down('#saveButton').disable();
        }
    },

    getBbarItems: function() {
        var items = this.callParent();
        items.push({
            xtype: 'primarybutton',
            itemId: 'saveButton',
            disabled: true,
            text: this.buttonText
        });
        return items;
    }
});
