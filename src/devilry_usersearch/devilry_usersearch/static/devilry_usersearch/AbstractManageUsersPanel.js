Ext.define('devilry_usersearch.AbstractManageUsersPanel' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.manageuserspanel',
    //cls: 'devilry_usersearch_manageuserspanel',
    requires: [
        'devilry_usersearch.AutocompleteUserWidget'
    ],

    gridCellTpl: [
        '<div class="gridcellbody gridcellbody_{username}">',
        '   <div class="full_name"><strong>{full_name}</strong></div>',
        '   <tpl if="!full_name">',
        '       <strong class="username">{username}</strong>',
        '       <small>(', gettext('Full name missing') ,')</small>',
        '   </tpl>',
        '   <div class="username_and_email">',
        '       <tpl if="full_name">',
        '           <small class="username">{username}</small>',
        '       </tpl>',
        '       <tpl if="email">',
        '          <small class="email">&lt;{email}&gt;</small>',
        '       </tpl>',
        '   </div>',
        '</div>'
    ],

    /**
     * @cfg {Ext.data.Store} store
     * The store where users are added/deleted by this panel.
     */

    constructor: function(config) {
        config.cls = config.cls || this.cls || '';
        config.cls += ' devilry_usersearch_manageuserspanel';
        this.addEvents({
            /**
             * @event
             * Fired when one or more users are added.
             * @param {[object]} userRecords Array of user records that was added.
             * */
            "usersAdded" : true,

            /**
             * @event
             * Fired when one or more users are removed.
             * @param {[object]} userRecords Array of user records that was removed.
             * */
            "usersRemoved" : true
        });

        // Copy configured listeners into *this* object so that the base class's
        // constructor will add them.
        this.listeners = config.listeners;

        this.callParent(arguments);
    },

    initComponent: function() {
        var me = this;
        this.gridCellTplCompiled = Ext.create('Ext.XTemplate', this.gridCellTpl);

        Ext.apply(this, {
            frame: false,
            border: 0,
            layout: 'border',
            items: [{
                xtype: 'grid',
                region: 'center',
                hideHeaders: true,
                multiSelect: true,
                store: this.store,
                columns: [{
                    header: 'Col1',  dataIndex: 'id', flex: 1,
                    renderer: function(unused, unused2, userRecord) {
                        return me.rendererGridCell(userRecord);
                    }
                }],
                listeners: {
                    scope: this,
                    selectionchange: this._onGridSelectionChange
                }
            }, {
                xtype: 'container',
                layout: 'fit',
                region: 'south',
                height: 36,
                padding: 4,
                items: {
                    xtype: 'autocompleteuserwidget',
                    listeners: {
                        scope: this,
                        userSelected: this._onAddUser
                    }
                }
            }],


            tbar: [{
                xtype: 'button',
                itemId: 'selectAllButton',
                cls: 'selectAllButton',
                text: gettext('Select all'),
                listeners: {
                    scope: this,
                    click: this._onSelectAll
                }
            }, {
                xtype: 'button',
                text: gettext('Remove'),
                itemId: 'removeButton',
                cls: 'removeButton',
                disabled: true,
                listeners: {
                    scope: this,
                    click: this._onRemoveUsers
                }
            }, '->', {
                xtype: 'textfield',
                emptyText: gettext('Search ...')
            }],
        });
        this.callParent(arguments);
    },

    _clearAndfocusAddUserField: function() {
        var field = this.down('autocompleteuserwidget');
        field.clearValue();
        field.focus();
    },

    _onAddUser: function(combo, userRecord) {
        var username = userRecord.get('username');
        if(this.store.findExact('username', username) == -1) {
            this.addUser(userRecord);
            this._clearAndfocusAddUserField();
        } else {
            Ext.MessageBox.show({
                title: gettext('Already in list'),
                msg: gettext('The selected user is already in the list'),
                buttons: Ext.MessageBox.OK,
                icon: Ext.MessageBox.ERROR,
                fn: function() {
                    Ext.defer(function() {
                        this._clearAndfocusAddUserField();
                    }, 100, this);
                },
                scope: this
            });
        }
    },

    _getSelectedUsers: function() {
        return this.down('grid').getSelectionModel().getSelection();
    },

    _onRemoveUsers: function() {
        var selectedUsers = this._getSelectedUsers();
        var confirmMessage = gettext('Do you really want to remove the {numselected} selected users from the list?');
        Ext.MessageBox.show({
            title: gettext('Confirm remove'),
            msg: Ext.create('Ext.XTemplate', confirmMessage).apply({
                numselected: selectedUsers.length
            }),
            buttons: Ext.MessageBox.YESNO,
            icon: Ext.MessageBox.QUESTION,
            fn: function(buttonId) {
                if(buttonId == 'yes') {
                    this.removeUsers(selectedUsers);
                }
            },
            scope: this
        });
    },
    _onSelectAll: function() {
        this.down('grid').getSelectionModel().selectAll();
    },

    _onGridSelectionChange: function(selectionmodel) {
        if(selectionmodel.getSelection().length == 0) {
            this.down('#removeButton').disable();
        } else {
            this.down('#removeButton').enable();
        }
    },

    /**
     * May want to override this in subclasses.
     * */
    rendererGridCell: function(userRecord) {
        return this.gridCellTplCompiled.apply(userRecord.data);
    },

    _hightlightUser: function(userRecord) {
        var index = this.store.findExact('username', userRecord.get('username'));
        this.down('grid').getSelectionModel().select(index);
    },

    onUserAdded: function(userRecord) {
        this._hightlightUser(userRecord);
        this.fireEvent('usersAdded', [userRecord]);
    },

    onUsersRemoved: function(userRecords) {
        this.fireEvent('usersRemoved', [userRecords]);
    },


    /** Implement in subclasses */
    addUser: function(userRecord) {
        throw "addUser not implemented";
    },

    /** Implement in subclasses */
    removeUsers: function(userRecord) {
        throw "removeUsers not implemented";
    }
});
