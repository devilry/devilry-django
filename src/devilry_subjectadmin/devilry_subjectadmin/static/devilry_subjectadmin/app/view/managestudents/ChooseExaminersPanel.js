Ext.define('devilry_subjectadmin.view.managestudents.ChooseExaminersPanel', {
    extend: 'devilry_extjsextras.ManageItemsPanel',
    alias: 'widget.chooseexaminerspanel',
    cls: 'devilry_subjectadmin_chooseexaminerspanel',
    requires: [
        'devilry_usersearch.ManageUsersGridModel',
        'devilry_subjectadmin.view.managestudents.AutocompleteRelatedUserWidget'
    ],

    constructor: function(config) {
        this.callParent([config]);
        this.addEvents({
            /**
             * @event
             * Fired to signal that a user should be added.
             * @param {[Object]} [userRecord] A user record.
             * @param [panel] The object of this panel that fired the event.
             * */
            "addUser" : true,

            /**
             * @event
             * Fired to signal that users should be removed.
             * @param {[object]} userRecords Array of user records.
             * @param [panel] The object of this panel that fired the event.
             * */
            "removeUsers" : true
        });
    },

    initComponent: function() {
        this.store = Ext.create('Ext.data.Store', {
            model: 'devilry_usersearch.ManageUsersGridModel'
        });

        this.addListener({
            scope: this,
            removeItems: this._onRemoveItems
        });

        var cellTpl = devilry_usersearch.ManageUsersGridModel.gridCellXTemplate();
        Ext.apply(this, {
            columns: [{
                header: 'Userinfo',  dataIndex: 'id', flex: 1,
                renderer: function(unused1, unused2, record) {
                    return cellTpl.apply(record.data);
                }
            }],

            fbar: [{
                xtype: 'autocompleterelateduserwidget',
                fieldLabel: gettext('Add examiner'),
                flex: 1,
                store: this.sourceStore,
                listeners: {
                    scope: this,
                    userSelected: this._onUserSelected
                }
            }]
        });
        this.callParent(arguments);
    },

    _clearAndfocusAddField: function() {
        this.clearAndfocusField('autocompleterelateduserwidget');
    },

    _onUserSelected: function(combo, relatedExaminerRecord) {
        var username = relatedExaminerRecord.get('user').username;
        combo.clearValue();
        if(this.store.findExact('username', username) == -1) {
            var userRecord = this.store.add(relatedExaminerRecord.get('user'))[0];
            this.fireEvent('addUser', userRecord, this);
        } else {
            this.showDuplicateItemMessage({
                callback: this._clearAndfocusAddField,
                scope: this
            });
        }
    },

    _onRemoveItems: function(userRecords) {
        this.store.remove(userRecords);
        this.fireEvent('removeUsers', userRecords, this);
    },

    afterItemAddedSuccessfully: function(record) {
        this.callParent(arguments);
        this._clearAndfocusAddField();
    },

    afterItemsRemovedSuccessfully: function(removedRecords) {
        this.callParent(arguments);
        this._clearAndfocusAddField();
    }
});
