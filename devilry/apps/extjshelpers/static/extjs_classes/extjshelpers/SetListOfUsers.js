Ext.define('devilry.extjshelpers.SetListOfUsers', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.setlistofusers',
    frame: false,
    border: false,

    config: {
        /**
         * @cfg
         * Usernames to fill in on load.
         */
        usernames: [],

        /**
         * @cfg
         * The label of the box/field.
         */
        fieldLabel: 'Usernames',

        buttonLabel: 'Save',

        example: 'bob\nalice\neve\ndave',
        helptext: '<p>One username on each line. Example:</p>',

        helptpl: Ext.create('Ext.XTemplate',
            '<div class="section helpsection">',
            '   {helptext}',
            '   <pre style="padding: 5px;">{example}</pre>',
            '</div>'
        )
    },


    constructor: function(config) {
        this.addEvents(
            /**
             * @event
             * Fired when the save button is clicked.
             *
             * @param setlistofusersobj This object.
             * @param usernames Array of usernames.
             */
            'saveClicked');
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        this.userinput = Ext.widget('textareafield', {
            fieldLabel: this.fieldLabel,
            flex: 12, // Take up all remaining vertical space
            margin: 10,
            labelAlign: 'top',
            labelWidth: 100,
            labelStyle: 'font-weight:bold'
        });
        this.setValueFromArray(this.usernames);

        var toolbarItems = ['->', {
            xtype: 'button',
            iconCls: 'icon-save-32',
            scale: 'large',
            text: this.buttonLabel,
            listeners: {
                scope: this,
                click: this.onSave
            }
        }];

        if(this.extraToolbarButtons) {
            Ext.Array.insert(toolbarItems, 0, this.extraToolbarButtons);
        }

        Ext.apply(this, {
            layout: {
                type: 'hbox',
                align: 'stretch'
            },

            items: [this.userinput, {
                flex: 10,
                xtype: 'box',
                padding: 10,
                autoScroll: true,
                html: this.helptpl.apply(this)
            }],

            dockedItems: [{
                xtype: 'toolbar',
                dock: 'bottom',
                ui: 'footer',
                items: toolbarItems
            }]
        });
        this.callParent(arguments);
    },

    parseInput: function(rawValue) {
        var asArray = rawValue.split('\n');
        var usernames = [];
        Ext.Array.each(asArray, function(username) {
            username = Ext.String.trim(username);
            if(username != "") {
                usernames.push(username);
            }
        });
        return Ext.Array.unique(usernames);
    },

    setValueFromArray: function(arrayOfUsernames) {
        var currentValue = "";
        Ext.each(arrayOfUsernames, function(username, index) {
            currentValue += Ext.String.format('{0}\n', username);
        });
        this.userinput.setValue(currentValue);
    },

    /**
     * @private
     */
    onSave: function() {
        var usernames = this.parseInput(this.userinput.getValue());
        this.fireEvent('saveClicked', this, usernames);
    }
});
