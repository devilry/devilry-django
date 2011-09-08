Ext.define('devilry.extjshelpers.studentsmanager.ImportGroupsFromAnotherAssignment', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.importgroupsfromanotherassignment',

    help: '<section class="helpsection">Select the assignment you wish to import assignment groups from, and click <em>Next</em> to further edit the selected groups.</section>',

    config: {
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
                    margins: '0 0 10 0'
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
        assignmentGroupModel = Ext.ModelManager.getModel('devilry.apps.administrator.simplified.SimplifiedAssignmentGroupImportFromPrevAssignment');
        var assignmentGroupStore = Ext.create('Ext.data.Store', {
            model: assignmentGroupModel,
            proxy: Ext.create('devilry.extjshelpers.RestProxy', {
                url: assignmentGroupModel.proxy.url
            })
        });
        assignmentGroupStore.proxy.setDevilryResultFieldgroups(['users']);

        var assignmentid = this.down('form').getForm().getValues().assignment;
        assignmentGroupStore.proxy.setDevilryFilters([{
            field: 'parentnode',
            comp: 'exact',
            value: assignmentid
        }]);

        assignmentGroupStore.pageSize = 1;
        this.getEl().mask('Loading assignment groups...');
        assignmentGroupStore.load({
            scope: this,
            callback: function(records, op, success) {
                if(!success) {
                    this.loadAssignmentGroupStoreFailed();
                }
                assignmentGroupStore.pageSize = assignmentGroupStore.totalCount;
                assignmentGroupStore.load({
                    scope: this,
                    callback: function(records, op, success) {
                        if(!success) {
                            this.loadAssignmentGroupStoreFailed();
                        }
                        this.getEl().unmask();
                        this.fireEvent('next', this, records);
                    }
                });
            }
        });
    },

    loadAssignmentGroupStoreFailed: function() {
        this.getEl().unmask();
        Ext.MessageBox.alert('Failed to load assignment groups. Please try again.');
    }
});
