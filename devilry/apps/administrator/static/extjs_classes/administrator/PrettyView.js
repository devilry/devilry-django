/** A prettyview is a read-only view panel used to display a single model record. */
Ext.define('devilry.administrator.PrettyView', {
    extend: 'Ext.panel.Panel',
    cls: 'prettyviewpanel',
    bodyPadding: 20,

    requires: [
        'devilry.extjshelpers.SetListOfUsers'
    ],

    config: {
        /**
         * @cfg
         * The name of the ``Ext.data.Model`` to present in the body. (Required).
         */
        modelname: undefined,

        /**
         * @cfg
         * Unique ID of the object to load from the model. (Required).
         */
        objectid: undefined,

        /**
         * @cfg
         * A ``Ext.XTemplate`` object for the body of this view. (Required).
         */
        bodyTpl: undefined,

        /**
         * @cfg
         * Optional list of buttons for related actions.
         */
        relatedButtons: undefined,

        /**
         * @cfg
         * The url to the dashboard. (Required). Used after delete to return to
         * the dashboard.
         */
        dashboardUrl: undefined

        /**
         * @cfg
         * Optional list of menuitems for plugin actions.
         */
        //pluginItems: undefined
    },

    constructor: function(config) {
        this.addEvents(
            /**
             * @event
             * Fired when the model record is loaded successfully.
             * @param {Ext.model.Model} record The loaded record.
             */
            'loadmodel',
            
            /**
             * @event
             * Fired when the edit button is clicked.
             * @param {Ext.model.Model} record The record to edit.
             * @param button The edit button.
             */
            'edit');
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        this.setadminsbutton = Ext.create('Ext.button.Button', {
            text: 'Manage administrators',
            scale: 'large',
            menu: [],
            enableToggle: true,
            listeners: {
                scope: this,
                click: this.onSetadministrators
            }
        });


        this.deletebutton = Ext.create('Ext.button.Button', {
            text: 'Delete',
            scale: 'large',
            enableToggle: true,
            menu: [],
            listeners: {
                scope: this,
                click: this.onDelete
            }
        });

        this.editbutton = Ext.create('Ext.button.Button', {
            text: 'Edit',
            enableToggle: true,
            menu: [],
            scale: 'large',
            listeners: {
                scope: this,
                click: this.onEdit
            }
        });

        var tbar = ['->', this.deletebutton, this.setadminsbutton, this.editbutton];

        if(this.extraMeButtons) {
            Ext.Array.insert(tbar, 2, this.extraMeButtons);
        }

        //if(this.pluginItems) {
            //Ext.Array.insert(tbar, 0, this.pluginItems);
        //}

        if(this.relatedButtons) {
            Ext.Array.insert(tbar, 0, this.relatedButtons);
        }

        Ext.apply(this, {
            tbar: tbar,
        });
        this.callParent(arguments);

        var model = Ext.ModelManager.getModel(this.modelname);
        model.load(this.objectid, {
            scope: this,
            success: this.onModelLoadSuccess,
            failure: this.onModelLoadFailure
        });

        this.addListener('render', function() {
            this.getEl().mask('Loading');
        }, this);
    },

    onModelLoadSuccess: function(record) {
        this.record = record;
        this.refreshBody();
        this.getEl().unmask();
        this.fireEvent('loadmodel', record);
    },

    refreshBody: function() {
        var bodyData = this.getExtraBodyData(this.record);
        Ext.apply(bodyData, this.record.data);
        this.update(this.bodyTpl.apply(bodyData));
    },

    getExtraBodyData: function(record) {
        return {};
    },

    onModelLoadFailure: function(record, operation) {
        throw 'Failed to load the model';
    },

    onEdit: function(button) {
        this.fireEvent('edit', this.record, button);
    },

    /** Set record. Triggers the loadmodel event. */
    setRecord: function(record) {
        this.onModelLoadSuccess(record);
    },

    onDelete: function(button) {
        var me = this;
        var win = Ext.MessageBox.show({
            title: 'Confirm delete',
            msg: 'Are you sure you want to delete?',
            buttons: Ext.Msg.YESNO,
            icon: Ext.Msg.WARNING,
            closable: false,
            fn: function(btn) {
                if(btn == 'yes') {
                    me.deleteObject();
                }
                button.toggle(false);
            }
        });
        win.alignTo(button, 'br?', [-win.width, 0]);
    },

    deleteObject: function() {
        this.record.destroy({
            scope: this,
            success: function() {
                window.location.href = this.dashboardUrl;
            },
            failure: this.onDeleteFailure
        });
    },

    onDeleteFailure: function(record, operation) {
        var title, msg;
        if(operation.error.status == 403) {
            title = "Forbidden";
            msg = 'You do not have permission to delete this item. Only super-administrators have permission to delete items with any content.';
        } else {
            title = 'An unknow error occurred';
            msg = "This is most likely caused by a bug, or a problem with the Devilry server.";
        }

        Ext.MessageBox.show({
            title: title,
            msg: msg,
            buttons: Ext.Msg.OK,
            icon: Ext.Msg.ERROR
        });
    },

    onSetadministrators: function(button) {
        var win = Ext.widget('window', {
            title: 'Set administrators',
            modal: true,
            width: 450,
            height: 250,
            maximizable: true,
            layout: 'fit',
            listeners: {
                close: function() {
                    button.toggle(false);
                }
            },
            items: {
                xtype: 'setlistofusers',
                usernames: this.record.data.admins__username,
                helptext: '<p>The username of a single administrator on each line. Example:</p>',
                listeners: {
                    scope: this,
                    saveClicked: this.onSaveAdmins
                }
            }
        });
        win.show();
        win.alignTo(button, 'br?', [-win.width, 0]);
    },

    onSaveAdmins: function(setlistofusersobj, usernames) {
        setlistofusersobj.getEl().mask('Saving...');
        this.record.data.fake_admins = usernames
        this.record.save({
            scope: this,
            success: function(record) {
                setlistofusersobj.getEl().unmask();
                record.data.admins__username = usernames
                this.onModelLoadSuccess(record)
                setlistofusersobj.up('window').close();
                this.setadminsbutton.toggle(false);
            },
            failure: function() {
                setlistofusersobj.getEl().unmask();
                Ext.MessageBox.show({
                    title:'Error',
                    msg: 'An error occurred. This is most likely caused by an <strong>invalid username</strong>. Please review the usernames and try again.',
                    buttons: Ext.Msg.OK,
                    icon: Ext.Msg.ERROR
                });
            }
        });
    }
});
