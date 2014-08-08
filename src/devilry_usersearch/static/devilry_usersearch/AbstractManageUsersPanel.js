Ext.define('devilry_usersearch.AbstractManageUsersPanel' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.manageuserspanel',
    //cls: 'devilry_usersearch_manageuserspanel',
    requires: [
        'devilry_usersearch.AutocompleteUserWidget'
    ],
    frame: false,
    border: false,

    /**
     * @cfg prettyFormatUserTpl
     * The template used to render the grid cell by default.
     * Takes the following variables:
     *
     *  - username
     *  - full_name
     *  - email
     */
    prettyFormatUserTpl: [
        '<div class="prettyformattedusercell prettyformattedusercell_{username}">',
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

    /**
     * @cfg [{Object}] columns
     * Grid columns. Defaults to a single column using the #prettyFormatUserTpl.
     */

    /**
     * @cfg {boolean} confirmBeforeRemove
     * Show confirm dialog on remove? Defaults to ``true``.
     */
    confirmBeforeRemove: true,

    /**
     * @cfg {bool} hideHeaders
     * Hide grid headers?
     */
    hideHeaders: true,

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
        this.prettyFormatUserTplCompiled = Ext.create('Ext.XTemplate', this.prettyFormatUserTpl);

        var defaultColumns = [{
            header: 'Userinfo',  dataIndex: 'id', flex: 1,
            renderer: Ext.bind(this.renderPrettyformattedUserGridCell, this)
        }];
        var columns = this.columns || defaultColumns;

        Ext.apply(this, {
            layout: 'fit',
            items: [{
                xtype: 'grid',
                hideHeaders: this.hideHeaders,
                multiSelect: true,
                store: this.store,
                columns: columns,
                listeners: {
                    scope: this,
                    selectionchange: this._onGridSelectionChange
                }
            }],

            fbar: this.getBbarItems(),

            tbar: [{
                xtype: 'button',
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
                cls: 'searchfield',
                emptyText: gettext('Search ...'),
                listeners: {
                    scope: this,
                    change: this._onSearchChange
                }
            }]
        });
        this.callParent(arguments);
    },

    _clearAndfocusAddUserField: function() {
        var field = this.down('autocompleteuserwidget');
        field.clearValue();
        field.focus();
    },

    /** May want to override for custom save masking. */
    saveMask: function() {
        this.setLoading(gettext('Saving ...'))
    },

    /** May want to override for custom save masking. */
    removeSaveMask: function() {
        this.setLoading(false);
    },

    _onAddUser: function(combo, userRecord) {
        var username = userRecord.get('username');
        if(this.store.findExact('username', username) == -1) {
            this.saveMask();
            this.addUser(userRecord);
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
        if(this.confirmBeforeRemove) {
            this._confirmRemove(selectedUsers);
        } else {
            this._removeUsers(selectedUsers);
        }
    },

    _removeUsers: function(selectedUsers) {
        this.saveMask();
        this.removeUsers(selectedUsers);
    },

    _confirmRemove: function(selectedUsers) {
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
                    this._removeUsers(selectedUsers);
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

    _onSearchChange: function(searchfield, newValue, oldValue) {
        if(newValue === '') {
            this._clearSearchFilter();
        } else {
            this._search(newValue);
        }
    },

    _hightlightUser: function(recordToHighlight) {
        var usernameToHightlight = this.getUserDataFromRecord(recordToHighlight).username;
        var index = this.store.findBy(function(storeRecord) {
            return this.getUserDataFromRecord(storeRecord).username === usernameToHightlight;
        }, this);
        this.down('grid').getSelectionModel().select(index);
    },

    _search: function(query) {
        this.store.filterBy(function(record) {
            return this.searchMatchesRecord(query, record);
        }, this);
    },

    _clearSearchFilter: function() {
        this.store.clearFilter();
    },



    /** Use this in subclasses if you have custom columns, but want to be able
     * to re-use the cell renderer for userinfo. */
    renderPrettyformattedUserGridCell: function(unused, unused2, record) {
        return this.prettyFormatUserTplCompiled.apply(this.getUserDataFromRecord(record));
    },

    /**
     * May want to override this in subclasses if the store records are not
     * devilry_usersearch.ManageUsersGridModel objects.
     *
     * @return Object with username, full_name and email attributes.
     * */
    getUserDataFromRecord: function(record) {
        return record.data;
    },

    _onSaveComplete: function() {
        Ext.defer(function() {
            this.removeSaveMask();
            this._clearAndfocusAddUserField();
        }, 200, this);
    },

    /** Called by subclasses when #addUser is successful. */
    onUserAdded: function(userRecord) {
        this._hightlightUser(userRecord);
        this._onSaveComplete();
        this.fireEvent('usersAdded', [userRecord]);
    },

    /** Called by subclasses when #removeUsers is successful. */
    onUsersRemoved: function(userRecords) {
        this._onSaveComplete();
        this.fireEvent('usersRemoved', [userRecords]);
    },

    /** Implement in subclasses */
    addUser: function(userRecord) {
        throw "addUser not implemented";
    },

    /** Implement in subclasses */
    removeUsers: function(userRecord) {
        throw "removeUsers not implemented";
    },

    caseIgnoreContains: function(fieldvalue, query) {
        if(fieldvalue) {
            return fieldvalue.toLocaleLowerCase().indexOf(query) > -1;
        } else {
            return false;
        }
    },

    /** Override this to replace, or extend the search. */
    searchMatchesRecord: function(query, record) {
        var data = this.getUserDataFromRecord(record);
        var username = data.username;
        var full_name = data.full_name;
        var email = data.email;
        return this.caseIgnoreContains(username, query) ||
            this.caseIgnoreContains(full_name, query) ||
            this.caseIgnoreContains(email, query);
    },


    /** Override this to replace the button toolbar. */
    getBbarItems: function() {
        return [{
            xtype: 'autocompleteuserwidget',
            flex: 1,
            listeners: {
                scope: this,
                userSelected: this._onAddUser
            }
        }]
    }
});
