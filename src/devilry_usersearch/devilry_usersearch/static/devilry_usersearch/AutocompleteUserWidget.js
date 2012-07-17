/** User autocomplete widget. */
Ext.define('devilry_usersearch.AutocompleteUserWidget' ,{
    extend: 'Ext.form.field.ComboBox',
    alias: 'widget.autocompleteuserwidget',
    cls: 'devilry_usersearch_autocompleteuserwidget',
    requires: [
    ],

    emptyText: gettext('Start typing name, username or email, and select the user from the popup list ...'),
    fieldLabel: gettext('Add user'),

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
        this.store = Ext.create('devilry_usersearch.UserSearchStore');
        Ext.apply(this, {
            queryMode: 'remote',
            store: this.store,
            hideTrigger: true,
            typeAhead: false,
            displayField: 'full_name',
            minChars: 3,
            listConfig: {
                loadingText: gettext('Searching...'),
                emptyText: gettext('No matching users found.'),
                cls: 'autocompleteuserwidget_matchlist',

                // Custom rendering template for each item
                getInnerTpl: function() {
                    return [
                        '<div class="matchlistitem matchlistitem_{username}">',
                            '<h3>{full_name}</h3>',
                            '<small class="username">{username}</small>',
                            '<tpl if="email">',
                                ' <small class="email">&lt;{email}&gt;</small>',
                            '</tpl>',
                        '</div>'
                    ].join('');
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
