Ext.define('devilry.extjshelpers.studentsmanager.ImportGroupsFromAnotherAssignment', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.importgroupsfromanotherassignment',

    config: {
        help: undefined,
        periodid: undefined
    },
    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        var assignmentModel = Ext.ModelManager.getModel('devilry.apps.administrator.simplified.SimplifiedAssignment');
        this.assignmentStore = Ext.create('Ext.data.Store', {
            model: assignmentModel,
            proxy: Ext.create('devilry.extjshelpers.RestProxy', {
                url: assignmentModel.proxy.url
            })
        });
        this.assignmentStore.proxy.setDevilryFilters([{
            field: 'parentnode',
            comp: 'exact',
            value: this.periodid
        }]);

        Ext.apply(this, {
            layout: {
                type: 'hbox',
                align: 'stretch'
            },
            items: [{
                xtype: 'form',
                padding: 20,
                border: false,
                flex: 6,
                layout: {
                    type: 'vbox',
                    align: 'stretch'
                },
                fieldDefaults: {
                    labelAlign: 'top',
                    labelWidth: 100,
                    labelStyle: 'font-weight:bold'
                },
                defaults: {
                    margin: '0 0 10 0'
                },
                items: [{
                    xtype: 'combo',
                    store: this.assignmentStore,
                    name: "assignment",
                    fieldLabel: "Choose an assignment",
                    emptyText: 'Choose an assignment...',
                    displayField: 'long_name',
                    valueField: 'id',
                    forceSelection: true,
                    editable: false,
                    listeners: {
                        scope: this,
                        select: function() {
                            this.down('button').enable();
                        }
                    }
                }]
            }, {
                xtype: 'box',
                flex: 4,
                html: this.help
            }],

            dockedItems: [{
                xtype: 'toolbar',
                dock: 'bottom',
                ui: 'footer',

                items: ['->', {
                    xtype: 'button',
                    text: 'Next',
                    scale: 'large',
                    iconCls: 'icon-next-32',
                    disabled: true,
                    listeners: {
                        scope: this,
                        click: this.onNext
                    }
                }]
            }]
        });
        this.callParent(arguments);
    },

    onNext: function() {
        var assignmentid = this.down('form').getForm().getValues().assignment;
        this.getEl().mask('Loading assignment groups...');
        devilry.administrator.studentsmanager.StudentsManager.getAllGroupsInAssignment(assignmentid, {
            scope: this,
            callback: function(records, op, success) {
                if(success) {
                    this.getEl().unmask();
                    this.fireEvent('next', this, records);
                } else {
                    this.loadAssignmentGroupStoreFailed();
                }
            }
        });
    },

    loadAssignmentGroupStoreFailed: function() {
        this.getEl().unmask();
        Ext.MessageBox.alert('Failed to load assignment groups. Please try again.');
    }
});
