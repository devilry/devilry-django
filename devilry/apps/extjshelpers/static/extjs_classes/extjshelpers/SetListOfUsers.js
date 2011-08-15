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

        buttonLabel: 'Save',

        example: 'bob\nalice\neve\ndave',
        helptext: '<p>One username on each line. Example:</p>',

        helptpl: Ext.create('Ext.XTemplate',
            '<section class="helpsection">',
            '   {helptext}',
            '   <pre style="border: 1px solid #999; padding: 5px;">{example}</pre>',
            '</section>'
        ),
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
        var currentValue = "";
        Ext.each(this.usernames, function(username, index) {
            currentValue += Ext.String.format('{0}\n', username);
        });

        this.userinput = Ext.widget('textareafield', {
            fieldLabel: 'Usernames',
            flex: 12, // Take up all remaining vertical space
            margin: 10,
            labelAlign: 'top',
            labelWidth: 100,
            labelStyle: 'font-weight:bold',
            value: currentValue
        });

        Ext.apply(this, {
            layout: {
                type: 'hbox',
                align: 'stretch'
            },

            items: [this.userinput, {
                flex: 10,
                xtype: 'box',
                padding: 10,
                html: this.helptpl.apply(this)
            }],

            dockedItems: [{
                xtype: 'toolbar',
                dock: 'bottom',
                ui: 'footer',
                items: ['->', {
                    xtype: 'button',
                    iconCls: 'icon-save-32',
                    scale: 'large',
                    text: this.buttonLabel,
                    listeners: {
                        scope: this,
                        click: this.onSave
                    }
                }]
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
        return usernames;
    },

    /**
     * @private
     */
    onSave: function() {
        var usernames = this.parseInput(this.userinput.getValue());
        this.fireEvent('saveClicked', this, usernames);
    }
});
