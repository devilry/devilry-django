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

    node_modelname: 'devilry.apps.administrator.simplified.SimplifiedNode',
    subject_modelname: 'devilry.apps.administrator.simplified.SimplifiedSubject',
    period_modelname: 'devilry.apps.administrator.simplified.SimplifiedPeriod',
    assignment_modelname: 'devilry.apps.administrator.simplified.SimplifiedAssignment',


    /**
     * @cfg
     * (Required)
     */
    is_superuser: undefined,

    initComponent: function() {
        var nodestore_node = this._createStore(this.node_modelname);
        var nodestore = this._createStore(this.node_modelname);
        var subjectstore = this._createStore(this.subject_modelname);
        var periodstore = this._createStore(this.period_modelname);
        
        var me = this;
        Ext.apply(this, {
            items: [{
                xtype: 'buttonbarbutton',
                is_superuser: this.is_superuser,
                text: gettext('Node'),
                store: nodestore_node,
                iconCls: 'icon-add-32',
                tooltipCfg: {
                    title: [
                        '<span class="tooltip-title-current-item">', gettext('Node'), '</span> &rArr; ',
                        gettext('Subject'), ' &rArr; ',
                        gettext('Period'), ' &rArr; ',
                        gettext('Assignment')
                    ].join(''),
                    body: interpolate(gettext('A %(Node_term)s is a place to organise top-level administrators.'), {
                        Node_term: gettext('Node')
                    }, true)
                },
                handler: function() {
                    Ext.create('devilry.administrator.DefaultCreateWindow', {
                        title: interpolate(gettext('Create new %(node_term)s'), {
                            node_term: gettext('node')
                        }, true),
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
                store: nodestore,
                iconCls: 'icon-add-32',
                tooltipCfg: {
                    title: [
                        gettext('Node'), ' &rArr; ',
                        '<span class="tooltip-title-current-item">', gettext('Subject'), '</span> &rArr; ',
                        gettext('Period'), ' &rArr; ',
                        gettext('Assignment')
                    ].join(''),
                    body: ''
                },
                handler: function() {
                    Ext.create('devilry.administrator.DefaultCreateWindow', {
                        title: interpolate(gettext('Create new %(subject_term)s'), {
                            subject_term: gettext('subject')
                        }, true),
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
                store: subjectstore,
                iconCls: 'icon-add-32',
                tooltipCfg: {
                    title: [
                        gettext('Node'), ' &rArr; ',
                        gettext('Subject'), ' &rArr; ',
                        '<span class="tooltip-title-current-item">', gettext('Period'), '</span> &rArr; ',
                        gettext('Assignment')
                    ].join(''),
                    body: ''
                },
                handler: function() {
                    Ext.create('devilry.administrator.DefaultCreateWindow', {
                        title: interpolate(gettext('Create new %(period_term)s'), {
                            period_term: gettext('period')
                        }, true),
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
                text: gettext('Assignment'),
                store: periodstore,
                iconCls: 'icon-add-32',
                tooltipCfg: {
                    title: [
                        gettext('Node'), ' &rArr; ',
                        gettext('Subject'), ' &rArr; ',
                        gettext('Period'), ' &rArr; ',
                        '<span class="tooltip-title-current-item">', gettext('Assignment'), '</span>'
                    ].join(''),
                    body: interpolate(gettext('An %(assignment_term)s, such as an obligatory %(assignment_term)s, an anoymous home examination or a semester %(assignment_term)s.'), {
                        assignment_term: gettext('assignment')
                    }, true)
                },
                handler: function() {
                    Ext.create('devilry.administrator.DefaultCreateWindow', {
                        title: interpolate(gettext('Create new %(assignment_term)s'), {
                            assignment_term: gettext('assignment')
                        }, true),
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
    },

    _createStore: function(modelname) {
        var model = Ext.ModelManager.getModel(modelname);
        var store = Ext.create('Ext.data.Store', {
            model: model,
            remoteFilter: true,
            remoteSort: true,
            pageSize: 1,
            proxy: model.proxy.copy()
        });
        return store;
    },
});
