Ext.define('devilry.administrator.DashboardButtonBar', {
    extend: 'devilry.extjshelpers.ButtonBar',
    cls: 'dashboard-buttonbar',

    requires: [
        'devilry.extjshelpers.forms.administrator.Node',
        'devilry.extjshelpers.forms.administrator.Subject',
        'devilry.extjshelpers.forms.administrator.Period',
        'devilry.extjshelpers.forms.administrator.Assignment',
        'devilry.administrator.DefaultCreateWindow',
        'devilry.extjshelpers.RestfulSimplifiedEditPanel',
        'devilry.extjshelpers.ButtonBarButton'
    ],

    config: {
        node_modelname: undefined,
        subject_modelname: undefined,
        period_modelname: undefined,
        assignment_modelname: undefined,
        is_superuser: undefined,
        nodestore: undefined,
        subjectstore: undefined,
        periodstore: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        var me = this;
        Ext.apply(this, {
            items: [{
                xtype: 'buttonbarbutton',
                is_superuser: this.is_superuser,
                text: 'Node',
                store: this.nodestore,
                iconCls: 'icon-add-32',
                tooltipCfg: {
                    title: '<span class="tooltip-title-current-item">Node</span> &rArr; Subject &rArr; Period &rArr; Assignment',
                    body: 'A Node is a place to organise top-level administrators.'
                },
                handler: function() {
                    Ext.create('devilry.administrator.DefaultCreateWindow', {
                        title: 'Create new node',
                        editpanel: Ext.ComponentManager.create({
                            xtype: 'restfulsimplified_editpanel',
                            model: me.node_modelname,
                            editform: Ext.widget('administrator_nodeform')
                        }),
                        successUrlTpl: Ext.create('Ext.XTemplate', 'node/{id}')
                    }).show();
                }
            }, {
                xtype: 'buttonbarbutton',
                text: 'Subject',
                store: this.nodestore,
                iconCls: 'icon-add-32',
                tooltipCfg: {
                    title: 'Node &rArr; <span class="tooltip-title-current-item">Subject</span> &rArr; Period &rArr; Assignment',
                    body: 'A Subject is often also called a course.'
                },
                handler: function() {
                    Ext.create('devilry.administrator.DefaultCreateWindow', {
                        title: 'Create new subject',
                        editpanel: Ext.ComponentManager.create({
                            xtype: 'restfulsimplified_editpanel',
                            model: me.subject_modelname,
                            editform: Ext.widget('administrator_subjectform')
                        }),
                        successUrlTpl: Ext.create('Ext.XTemplate', 'subject/{id}')
                    }).show();
                }
            }, {
                xtype: 'buttonbarbutton',
                text: 'Period/Semester',
                store: this.subjectstore,
                iconCls: 'icon-add-32',
                tooltipCfg: {
                    title: 'Node &rArr; Subject &rArr; <span class="tooltip-title-current-item">Period</span> &rArr; Assignment',
                    body: 'A Period is a limited period in time, such as a semester.'
                },
                handler: function() {
                    Ext.create('devilry.administrator.DefaultCreateWindow', {
                        title: 'Create new period',
                        editpanel: Ext.ComponentManager.create({
                            xtype: 'restfulsimplified_editpanel',
                            model: me.period_modelname,
                            editform: Ext.widget('administrator_periodform')
                        }),
                        successUrlTpl: Ext.create('Ext.XTemplate', 'period/{id}')
                    }).show();
                }
            }, {
                xtype: 'buttonbarbutton',
                text: 'Assignment',
                store: this.periodstore,
                iconCls: 'icon-add-32',
                tooltipCfg: {
                    title: 'Node &rArr; Subject &rArr; Period &rArr; <span class="tooltip-title-current-item">Assignment</span>',
                    body: 'An Assignment, such as an obligatory assignment, an anoymous home examination or a semester assignment.'
                },
                handler: function() {
                    Ext.create('devilry.administrator.DefaultCreateWindow', {
                        title: 'Create new assignment',
                        editpanel: Ext.ComponentManager.create({
                            xtype: 'restfulsimplified_editpanel',
                            model: me.assignment_modelname,
                            editform: Ext.widget('administrator_assignmentform')
                        }),
                        successUrlTpl: Ext.create('Ext.XTemplate', 'assignment/{id}')
                    }).show();
                }
            }]
        });
        this.callParent(arguments);
    }
});
