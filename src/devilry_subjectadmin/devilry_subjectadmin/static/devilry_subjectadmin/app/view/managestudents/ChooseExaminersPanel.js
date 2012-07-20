Ext.define('devilry_subjectadmin.view.managestudents.ChooseExaminersPanel', {
    extend: 'devilry_usersearch.AbstractManageUsersPanel',
    alias: 'widget.chooseexaminerspanel',
    cls: 'devilry_subjectadmin_chooseexaminerspanel',
    requires: [
        'devilry_usersearch.ManageUsersGridModel'
    ],

    //confirmBeforeRemove: false,

    constructor: function(config) {
        this.store = Ext.create('Ext.data.Store', {
            model: 'devilry_usersearch.ManageUsersGridModel'
        });
        this.callParent([config]);

        this.addEvents({
            /**
             * @event
             * Fired to signal that a user should be added.
             * @param {[object]} userRecord A user record.
             * */
            "addUser" : true,

            /**
             * @event
             * Fired to signal that users should be removed.
             * @param {[object]} userRecords Array of user records.
             * */
            "removeUsers" : true
        });
    },

    addUser: function(userRecord) {
        this.store.add(userRecord);
        this.fireEvent('addUser', userRecord);
    },

    removeUsers: function(userRecords) {
        this.store.remove(userRecords);
        this.fireEvent('removeUsers', userRecords);
    }
});
