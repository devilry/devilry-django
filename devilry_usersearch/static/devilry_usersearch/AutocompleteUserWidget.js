/** User autocomplete widget. */
Ext.define('devilry_usersearch.AutocompleteUserWidget' ,{
    extend: 'Ext.form.field.ComboBox',
    alias: 'widget.autocompleteuserwidget',
    cls: 'devilry_usersearch_autocompleteuserwidget',
    requires: [
        'devilry_usersearch.UserSearchStore'
    ],

    emptyText: gettext('Start typing name, username or email, and select the user from the popup list ...'),
    fieldLabel: gettext('Add user'),
    queryMode: 'remote',
    hideTrigger: true,
    typeAhead: false,
    displayField: 'full_name',
    minChars: 3,
    selectOnTab: false,

    /**
     * @cfg {String} listEmptyText
     */
    listEmptyText: gettext('No matching users found.'),

    /**
     * @cfg {Function} createStore
     * Callback that returns the store.
     */
    createStore: function() {
        return Ext.create('devilry_usersearch.UserSearchStore');
    },

    /**
     * @cfg {Function} listInnerTpl
     * Returns the xtemplate for listConfig.getInnerTpl
     */
    listGetInnerTpl: function() {
        return[
            '<div class="matchlistitem matchlistitem_{username}">',
                '<h3>{full_name}</h3>',
                '<small class="username">{username}</small>',
                '<tpl if="email">',
                    ' <small class="email">&lt;{email}&gt;</small>',
                '</tpl>',
            '</div>'
        ].join('');
    },

    constructor: function(config) {
        this.addEvents({
            /**
             * @event
             * @param autocompletewidget The autocompletewidget that fired the event.
             * @param userRecord The user record.
             * */
            "userSelected" : true
        });

        // Copy configured listeners into *this* object so that the base class's
        // constructor will add them.
        this.listeners = config.listeners;

        this.callParent(arguments);
    },

    initComponent: function() {
        this.store = this.store || this.createStore();
        var innerTpl = this.listGetInnerTpl();
        Ext.apply(this, {
            listConfig: {
                loadingText: gettext('Searching...'),
                emptyText: this.listEmptyText,
                cls: 'autocompleteuserwidget_matchlist',

                // Custom rendering template for each item
                getInnerTpl: function() {
                    return innerTpl;
                }
            }
        });
        this.on('render', this._onRender, this);
        this.on('select', this._onSelectUser, this);
        this.callParent(arguments);
    },

    _onRender: function(field) {
        Ext.defer(function() {
            field.focus();
        }, 200);
    },

    _onSelectUser: function(combo, records) {
        this.fireEvent('userSelected', combo, records[0]);
    }
});
