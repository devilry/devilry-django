Ext.define('devilry_subjectadmin.view.relatedstudents.SelectUserPanel', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.selectrelateduserpanel',
    cls: 'devilry_subjectadmin_selectrelateduserpanel',
    requires: [
        'devilry_usersearch.AutocompleteUserWidget'
    ],
    bodyPadding: 10,

    constructor: function(config) {
        this.callParent([config]);
        this.addEvents(
            /** @event
             * Fired when the Cancel-button is clicked.
             * @param panel This panel.
             */
            'cancel'
        );
    },

    initComponent: function() {
        Ext.apply(this, {
            dockedItems: [{
                xtype: 'toolbar',
                dock: 'bottom',
                ui: 'footer',
                items: [{
                    xtype: 'button',
                    itemId: 'cancelbutton',
                    cls: 'cancelbutton',
                    text: gettext('Cancel'),
                    listeners: {
                        scope: this,
                        click: this._onCancelButtonClick
                    }
                }]
            }],
            layout: 'anchor',
            items: [{
                anchor: '100%',
                xtype: 'autocompleteuserwidget',
                emptyText: gettext('Search by username, name or email ...'),
                hideLabel: true
            }]
        });
        this.callParent(arguments);
    },

    _onCancelButtonClick: function() {
        this.fireEvent('cancel', this);
    }
});

